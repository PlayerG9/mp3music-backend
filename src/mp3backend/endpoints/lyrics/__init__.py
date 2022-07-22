#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from main import api
from . import models
from . import crud


@api.get(
    '/lyrics',
    response_model=models.LyricsResponse,
    name="Fetch Lyrics"
)
def lyrics(config: models.RequestConfig):
    return dict(
        lyrics=crud.findLyrics(title=config.title, creator=config.author)
    )
