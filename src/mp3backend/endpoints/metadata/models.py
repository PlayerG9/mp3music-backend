#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..search.models import SearchResponseItem  # noqa | for export


class MetadataRequestBody(BaseModel):
    youtubeId: str


class MetadataResponse(BaseModel):
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
