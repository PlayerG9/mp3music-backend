#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from fastapi import Query, HTTPException, status
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError
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
    try:
        video = YouTube(url)
        video.check_availability()
    except RegexMatchError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="invalid youtubeId passed")
    except VideoUnavailable:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="video not found")
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
    try:
        return Video.get(youtubeId, timeout=20)
    except TypeError:  # attempts to add something that can return None to a string
        raise HTTPException(status.HTTP_404_NOT_FOUND, "video not found")
