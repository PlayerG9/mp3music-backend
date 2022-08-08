#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from typing import Optional
from pydantic import BaseModel


class RequestConfig(BaseModel):
    title: str
    artist: Optional[str]


class LyricsResponse(BaseModel):
    lyrics: str = "text"


class TitleAndArtistResponse(BaseModel):
    title: str
    artist: str
