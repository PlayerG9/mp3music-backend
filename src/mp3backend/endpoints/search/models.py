#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from typing import List
from pydantic import BaseModel


class ViewCount(BaseModel):
    text: str
    short: str


class Thumbnail(BaseModel):
    url: str
    width: int
    height: int


class DescriptionSnippet(BaseModel):
    text: str


class Channel(BaseModel):
    name: str
    id: str
    thumbnails: List[Thumbnail]


class Accessibility(BaseModel):
    title: str
    duration: str


class SearchResponseItem(BaseModel):
    type: str
    id: str
    title: str
    publishedTime: str
    duration: str
    viewCount: ViewCount
    thumbnails: List[Thumbnail]
    richThumbnail: Thumbnail
    descriptionSnippet: List[DescriptionSnippet]
    channel: Channel
    accessibility: Accessibility
    link: str


class SearchResponse(BaseModel):
    result: List[SearchResponseItem]
