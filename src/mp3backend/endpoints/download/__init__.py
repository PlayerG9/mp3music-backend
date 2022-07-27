#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
import asyncio

import fastapi
from fastapi import status
from fastapi.responses import FileResponse
import pytube
import moviepy.editor as moviepy
import aiohttp
import requests
import eyed3.mp3
from eyed3.id3.frames import ImageFrame

from main import api
from ..lyrics.crud import findLyrics, LyricsNotFound
from ..metadata.utility import completeYoutubeUrl
from . import models
from . import utility


WEBSOCKET_CONNECTED = 1  # fastapi.websockets.WebsocketState.CONNECTED
CHUNK_SIZE = 1024*1024
DELETE_DELAY = 15*60  # 15 min


@api.get(
    '/mp3file/{uid}',
    response_class=FileResponse,
    name="Download the actual mp3 file"
)
def getMp3File(
        uid: str,
        filename: str
):
    if not filename.endswith('mp3'):
        filename = f"{filename}.mp3"

    filepath = utility.getTempFilePath(f"{uid}.mp3")
    if not os.path.isfile(filepath):
        raise fastapi.HTTPException(status.HTTP_404_NOT_FOUND, "invalid file uid")

    return FileResponse(
        path=filepath,
        filename=utility.fix4filename(filename)
    )


class SharedState:
    youtubeLink: str
    youtube: pytube.YouTube
    mp3FilePath: str
    mp4FilePath: str
    websocket: fastapi.WebSocket
    config: models.DownloadConfig


@api.websocket(
    '/download/{youtubeId}',
    name="create the mp3 file (websocket for status)"
)
async def download(
        youtubeId: str,
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
        return

    state = SharedState()
    state.mp4FilePath = utility.getNewTempFile('mp4')
    state.mp3FilePath, mp3Uid = utility.getNewTempFile('mp3', getUid=True)
    state.youtubeLink = completeYoutubeUrl(youtubeId)
    state.websocket = websocket
    state.config = config

    try:
        await websocket.send_json(dict(
            info="start download"
        ))
        await downloadMp4Video(state=state)
        await websocket.send_json(dict(
            info="converting to mp3"
        ))
        await convertToMp3Audio(state=state)
        await websocket.send_json(dict(
            info="manipulating mp3 metadata"
        ))
        os.remove(state.mp4FilePath)
        await manipulateMp3Metadata(state=state)
        await websocket.send_json(dict(
            info="mp3 file is ready to download"
        ))
        await websocket.send_json(dict(
            final={
                "uid": mp3Uid,
                "filename": getFinalFilename(config.metadata)
            }
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
            error_class=error.__class__.__name__
        ))
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=str(error))
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)


async def delayedFileDelete(filepath: str):
    await asyncio.sleep(DELETE_DELAY)
    os.remove(filepath)


def getFinalFilename(metadata: models.MetadataConfig) -> str:
    author = utility.fix4filename(metadata.artist)
    title = utility.fix4filename(metadata.title)
    return f"{author}_{title}"


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
    youtube = state.youtube = pytube.YouTube(state.youtubeLink)
    await state.websocket.send_json(dict(message="searching for download"))
    audio_stream = youtube.streams.get_audio_only()

    await state.websocket.send_json(dict(message="start download"))
    async with aiohttp.ClientSession() as session:
        timeout = aiohttp.ClientTimeout(total=300, connect=20)
        async with session.get(audio_stream.url, timeout=timeout) as response:
            response.raise_for_status()

            downloaded = 0
            max_size = audio_stream.filesize

            with open(state.mp4FilePath, 'wb') as file:
                while not response.content.is_eof():
                    chunk = await response.content.read(CHUNK_SIZE)
                    downloaded += len(chunk)
                    file.write(chunk)
                    await state.websocket.send_json(dict(
                        message=f"progress: {int((downloaded / max_size) * 100)}%",
                        extra=dict(
                            has=downloaded,
                            max=max_size
                        )
                    ))


async def convertToMp3Audio(state: SharedState):
    clip = moviepy.AudioFileClip(filename=state.mp4FilePath)
    clip.write_audiofile(filename=state.mp3FilePath, verbose=False, logger=None)


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
        lyrics: str = findLyrics(metadata.title, metadata.artist)
    except (aiohttp.ServerTimeoutError, aiohttp.ClientError, LyricsNotFound) as error:
        await state.websocket.send_json(dict(
            warning=f"failed to fetch lyrics ({error.__class__.__name__}: {error})"
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
