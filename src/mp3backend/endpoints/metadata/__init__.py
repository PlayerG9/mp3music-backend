#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from fastapi import Body
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
        config: models.MetadataRequestBody
):
    url = utility.completeYoutubeUrl(known=config.youtubeId)
    video = YouTube(url)
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


@api.get(
    '/metadata/v2',
    response_model=models.SearchResponseItem,
    name="Get Video Metadata"
)
def metadata2(
        config: models.MetadataRequestBody
):
    from youtubesearchpython import Video
    return Video.get(config.youtubeId, timeout=20)
