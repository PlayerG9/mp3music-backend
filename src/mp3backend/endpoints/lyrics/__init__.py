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
def findLyrics(
        title: str = Query(),
        author: str = Query(None),
):
    try:
        lyrics = crud.findLyrics(title=title, creator=author)
    except crud.LyricsNotFound as error:
        print(error)
        raise fastapi.exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return dict(
        lyrics=lyrics
    )
