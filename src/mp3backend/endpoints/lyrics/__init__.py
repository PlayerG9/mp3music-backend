#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from fastapi import HTTPException
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
    except (crud.LyricsNotFound, crud.TitleAndLyricsNotFound) as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return dict(
        lyrics=lyrics
    )


@api.get(
    '/find',
    response_model=models.TitleAndArtistResponse,
    name="Find Title and Artist"
)
async def findTitleAndArtist(
        title: str = Query(),
        artist: str = Query(None)
):
    try:
        title, artist = await crud.findTitleAndArtist(title=title, artist=artist)
    except crud.TitleAndLyricsNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return dict(
        title=title,
        artist=artist
    )
