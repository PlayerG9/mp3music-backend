#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os.path

import fastapi
from fastapi import Path, Body
from fastapi.responses import FileResponse
import requests
import pytube
import moviepy.editor as moviepy
import eyed3.mp3
from eyed3.id3.frames import ImageFrame
from main import api
from ..lyrics.crud import findLyrics, LyricsNotFound
from ..metadata.utility import completeYoutubeUrl
from . import models
from . import utility


CHUNK_SIZE = 2*1024*1024


@api.get(
    '/mp3file/{uid}',
    name="Download the actual mp3 file"
)
def getMp3File(uid: str = Path(), filename: str = Body("audio")):
    return FileResponse(
        path=utility.getTempFilePath(f"{uid}.mp3"),
        filename=f"{filename}.mp3"
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
async def getDownload(
        config: models.DownloadConfig,
        websocket: fastapi.WebSocket,
        youtubeId: str = Path()
):
    await websocket.accept()

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
        await manipulateMp3Metadata(state=state)
        await websocket.send_json(dict(
            info="mp3 file is ready to download"
        ))
        await websocket.send_json(dict(
            json={
                "uid": mp3Uid,
                "filename": getFinalFilename(config.metadata)
            }
        ))
    except Exception as error:
        if os.path.isfile(state.mp4FilePath):
            os.remove(state.mp4FilePath)
        if os.path.isfile(state.mp3FilePath):
            os.remove(state.mp3FilePath)
        await websocket.send_json(dict(error=str(error), error_class=error.__class__.__name__))
        raise error


def getFinalFilename(metadata: models.MetadataConfig) -> str:
    author = utility.fix4filename(metadata.artist)
    title = utility.fix4filename(metadata.title)
    return f"{author}_{title}"


def download_thumbnail(state) -> (bytes, str):
    import mimetypes

    url = state.youtube.thumbnail_url
    mimetype: str = mimetypes.guess_type(url)[0]

    response = requests.get(url)
    response.raise_for_status()

    return response.content, mimetype


async def downloadMp4Video(state: SharedState):
    youtube = state.youtube = pytube.YouTube(state.youtubeLink)
    await state.websocket.send_json(dict(message="searching for download"))
    audio_stream = youtube.streams.get_audio_only()

    download_stream = requests.get(audio_stream.url, timeout=(10, 30), stream=True)
    download_stream.raise_for_status()

    downloaded = 0
    max_size = audio_stream.filesize

    with open(state.mp4FilePath, 'wb') as file:
        for chunk in download_stream.iter_content(CHUNK_SIZE):
            downloaded += len(chunk)
            file.write(chunk)
            await state.websocket.send_json(dict(message=f"progress: {int(downloaded / max_size * 100)}%"))


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
        blob, mimetype = download_thumbnail(state)
    except (requests.Timeout, requests.HTTPError) as error:
        await state.websocket.send_json(dict(
            warning=f"failed to fetch lyrics: {error}"
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
    except (requests.Timeout, requests.HTTPError, LyricsNotFound) as error:
        await state.websocket.send_json(dict(
            warning=f"failed to fetch lyrics: {error}"
        ))
    else:
        tag.lyrics.set(lyrics)

    try:
        tag.save()
    except eyed3.Error:
        await state.websocket.send_json(dict(
            warning=f"failed to update mp3-metadata"
        ))
