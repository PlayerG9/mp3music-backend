#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from fastapi import Path
from fastapi.responses import FileResponse
import requests
import pytube
import moviepy
from main import api
from ..lyrics.crud import findLyrics
from . import models
from . import utility


@api.get(
    '/download/{youtubeId}',
    response_class=FileResponse,
    name="Download mp3"
)
def getDownload(
        config: models.DownloadConfig,
        youtubeId: str = Path()
):
    mp4_file_path = utility.getNewTempFile('mp4')
    mp3_file_path = utility.getNewTempFile('mp3')
    return FileResponse(
        path=mp3_file_path,
        filename=getFileName(config)
    )


def getFileName(config: models.DownloadConfig) -> str:
    pass


def downloadMp4Video(targetFile: str):
    pass


def convertToMp3Audio(sourceFile: str, targetFile: str):
    pass


def manipulateMp3Metadata(targetFile: str, metadata: models.MetadataConfig):
    pass
