#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
import asyncio

import fastapi
from fastapi import status, Query, HTTPException
from fastapi.responses import FileResponse
import pytube
from pytube.exceptions import VideoUnavailable
import moviepy.editor as moviepy
import aiohttp
import requests
import eyed3.mp3
from eyed3.id3.frames import ImageFrame

from main import api
from ..lyrics.crud import findLyrics, LyricsNotFound, TitleAndLyricsNotFound
from ..metadata.utility import completeYoutubeUrl
from . import models
from . import utility


CHUNK_SIZE = 1024*1024
DELETE_DELAY = 15*60  # 15 min


@api.get(
    '/mp3file/{uid}',
    response_class=FileResponse,
    name="Download the actual mp3 file"
)
def getMp3File(
        uid: str,
        filename: str = Query("audio")
):
    filename = utility.fix4filename(os.path.splitext(filename)[0])
    if not filename.endswith('.mp3'):
        filename = f"{filename}.mp3"

    filepath = utility.getTempFilePath(f"{uid}.mp3")
    if not os.path.isfile(filepath):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid file uid")

    return FileResponse(
        path=filepath,
        filename=filename
    )


class SharedState:
    youtubeLink: str
    youtube: pytube.YouTube
    mp3FilePath: str
    mp4FilePath: str
    websocket: fastapi.WebSocket
    config: models.DownloadConfig


@api.websocket(
    '/download',
    name="create the mp3 file (websocket for status)"
)
async def download(
        websocket: fastapi.WebSocket,
        backgroundTasks: fastapi.BackgroundTasks
):
    await websocket.accept()

    data = await websocket.receive_json()
    try:
        config = models.DownloadConfig.parse_obj(data)
    except Exception as error:
        await websocket.send_json(dict(
            error=str(error),
            error_class=error.__class__.__name__
        ))
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA, reason=str(error))
        return

    state = SharedState()
    state.mp4FilePath = utility.getNewTempFile('mp4')
    state.mp3FilePath, mp3Uid = utility.getNewTempFile('mp3', getUid=True)
    state.youtubeLink = completeYoutubeUrl(config.youtubeId)
    state.websocket = websocket
    state.config = config

    try:
        await websocket.send_json(dict(
            info="Start mp3-download"
        ))
        await downloadMp4Video(state=state)
        await websocket.send_json(dict(
            info="Converting to mp3..."
        ))
        await convertToMp3Audio(state=state)
        await websocket.send_json(dict(
            info="Manipulating mp3 metadata..."
        ))
        os.remove(state.mp4FilePath)
        await manipulateMp3Metadata(state=state)
        await websocket.send_json(dict(
            info="mp3 file is ready to download"
        ))
        await websocket.send_json(dict(
            final=dict(
                uid=mp3Uid,
                filename=getRecommendedFilename(config.metadata)
            )
        ))
        backgroundTasks.add_task(
            delayedFileDelete,
            filepath=state.mp3FilePath
        )
    except Exception as error:
        if os.path.isfile(state.mp4FilePath):
            os.remove(state.mp4FilePath)
        if os.path.isfile(state.mp3FilePath):
            os.remove(state.mp3FilePath)
        await websocket.send_json(dict(
            error=str(error),
            error_class=str(error.__class__.__name__)
        ))
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=str(error))
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)


async def delayedFileDelete(filepath: str):
    await asyncio.sleep(DELETE_DELAY)
    os.remove(filepath)


def getRecommendedFilename(metadata: models.MetadataConfig) -> str:
    title = metadata.title or "audio"
    if metadata.artist:
        artist = metadata.artist
        return utility.fix4filename(f"{artist}-{title}")
    else:
        return utility.fix4filename(f"{title}")


def getMimetypeFromUrl(url: str) -> str:
    import mimetypes
    if '?' in url:
        url = url.split('?')[0]
    return mimetypes.guess_type(url)[0]


async def download_thumbnail(state) -> (bytes, str):
    url = state.youtube.thumbnail_url

    mimetype = getMimetypeFromUrl(url)

    async with aiohttp.ClientSession() as session:
        timeout = aiohttp.ClientTimeout(total=60, connect=20)
        async with session.get(url, timeout=timeout) as response:
            response.raise_for_status()
            data = await response.read()

    return data, mimetype


async def downloadMp4Video(state: SharedState):
    try:
        youtube = state.youtube = pytube.YouTube(state.youtubeLink)
    except VideoUnavailable:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid youtube video")
    await state.websocket.send_json(dict(
        info="Searching for download..."
    ))
    audio_stream = youtube.streams.get_audio_only()

    await state.websocket.send_json(dict(
        info="Downloading..."
    ))

    # @youtube.register_on_progress_callback
    # def on_progress(_, __, bytes_remaining: int):
    #     max_size = audio_stream.filesize
    #     downloaded = max_size - bytes_remaining
    #     asyncio.get_running_loop().run_until_complete(state.websocket.send_json(dict(
    #         info=f"Progress: {int((downloaded / max_size) * 100)}%",
    #         progress=dict(
    #             has=downloaded,
    #             max=max_size
    #         )
    #     )))

    with open(state.mp4FilePath, 'wb') as file:
        await asyncio.to_thread(audio_stream.stream_to_buffer, file)


async def convertToMp3Audio(state: SharedState):
    clip = moviepy.AudioFileClip(filename=state.mp4FilePath)
    # clip.write_audiofile(filename=state.mp3FilePath, verbose=False, logger=None)
    await asyncio.to_thread(clip.write_audiofile, filename=state.mp3FilePath, verbose=False, logger=None)


async def manipulateMp3Metadata(state: SharedState):
    metadata: models.MetadataConfig = state.config.metadata

    audiofile: eyed3.core.AudioFile = eyed3.load(state.mp3FilePath)
    if audiofile.tag is None:
        audiofile.initTag()
    tag: eyed3.mp3.id3.Tag = audiofile.tag

    if metadata.title:
        tag.title = metadata.title
    if metadata.artist:
        tag.artist = metadata.artist

    await state.websocket.send_json(dict(
        info="Fetching Thumbnail..."
    ))
    try:
        blob, mimetype = await download_thumbnail(state)
        if not mimetype:
            raise TypeError("failed to get mimetype")
    except (requests.Timeout, requests.HTTPError, TypeError) as error:
        await state.websocket.send_json(dict(
            warning=f"failed to fetch thumbnail ({error.__class__.__name__}: {error})"
        ))
    except Exception as error:
        await state.websocket.send_json(dict(
            error=error,
            error_class=error.__class__.__name__
        ))
    else:
        # for keyId in [ImageFrame.ICON, ImageFrame.FRONT_COVER]:
        tag.images.set(
            ImageFrame.FRONT_COVER,
            blob,
            mimetype
        )

    await state.websocket.send_json(dict(
        info="Searching for lyrics..."
    ))
    try:
        lyrics: str = await findLyrics(title=metadata.title, artist=metadata.artist)
    except (aiohttp.ServerTimeoutError, aiohttp.ClientError, LyricsNotFound, TitleAndLyricsNotFound) as error:
        await state.websocket.send_json(dict(
            warning=f"failed to fetch lyrics ({error.__class__.__name__}: {getattr(error, 'message', error)})"
        ))
    except Exception as error:
        await state.websocket.send_json(dict(
            error=error,
            error_class=error.__class__.__name__
        ))
    else:
        tag.lyrics.set(lyrics)

    try:
        tag.save()
    except eyed3.Error:
        await state.websocket.send_json(dict(
            warning=f"failed to update mp3-metadata"
        ))
