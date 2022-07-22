#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from datetime import datetime
from typing import List, Optional
import pydantic
from fastapi import Path
from pytube import YouTube
from main import api


class MetadataResponse(pydantic.BaseModel):
    video_id: str
    title: str
    author: str
    description: str
    channel_id: str
    thumbnail_url: str
    publish_date: Optional[datetime]
    rating: Optional[float]
    length: Optional[int]
    views: Optional[int]
    keywords: List[str]
    metadata: Optional[dict]


@api.get(
    '/metadata/{youtubeId}',
    response_model=MetadataResponse,
    name="Get Video Metadata"
)
def getDownload(
        youtubeId: str = Path()
):
    video = YouTube(f'https://youtu.be/{youtubeId}')
    return dict(
        video_id=video.video_id,
        title=video.title,
        author=video.author,
        description=video.description,
        channel_id=video.channel_id,
        thumbnail_url=video.thumbnail_url,
        publish_date=video.publish_date,
        rating=video.rating,
        length=video.rating,
        views=video.views,
        keywords=video.keywords,
        metadata=video.metadata
    )
