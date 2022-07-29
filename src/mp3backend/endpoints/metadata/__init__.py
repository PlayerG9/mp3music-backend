#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from fastapi import Query
from pytube import YouTube
from main import api
from . import utility
from . import models


@api.get(
    '/metadata/v1',
    response_model=models.MetadataResponse,
    name="Get Video Metadata"
)
def metadata(
        youtubeId: str = Query()
):
    url = utility.completeYoutubeUrl(known=youtubeId)
    video = YouTube(url)
    return dict(
        video_id=video.video_id,
        title=video.title,
        artist=video.author,
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


@api.get(
    '/metadata/v2',
    response_model=models.SearchResponseItem,
    name="Get Video Metadata"
)
def metadata2(
        youtubeId: str = Query()
):
    from youtubesearchpython import Video
    return Video.get(youtubeId, timeout=20)
