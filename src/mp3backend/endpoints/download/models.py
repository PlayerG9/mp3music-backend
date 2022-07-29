#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from typing import Optional
from pydantic import BaseModel


class FileDownloadConfig(BaseModel):
    filename: str


class MetadataConfig(BaseModel):
    title: Optional[str]
    artist: Optional[str]


class DownloadConfig(BaseModel):
    metadata: MetadataConfig
    youtubeId: str
