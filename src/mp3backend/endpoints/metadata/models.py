#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class MetadataResponse(BaseModel):
    video_id: str
    title: str
    artist: str
    description: str
    channel_id: str
    thumbnail_url: str
    publish_date: Optional[datetime]
    rating: Optional[float]
    length: Optional[int]
    views: Optional[int]
    keywords: List[str]
