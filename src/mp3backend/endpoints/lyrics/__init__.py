#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import fastapi
from fastapi import status, Query
from main import api
from . import models
from . import crud


@api.get(
    '/lyrics',
    response_model=models.LyricsResponse,
    name="Fetch Lyrics"
)
async def findLyrics(
        title: str = Query(),
        artist: str = Query(None),
):
    try:
        lyrics = await crud.findLyrics(title=title, artist=artist)
    except crud.LyricsNotFound as error:
        raise fastapi.exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return dict(
        lyrics=lyrics
    )
