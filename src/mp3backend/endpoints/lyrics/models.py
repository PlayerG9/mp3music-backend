#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from pydantic import BaseModel


class RequestConfig(BaseModel):
    title: str
    author: str


class LyricsResponse(BaseModel):
    lyrics: str = "text"
