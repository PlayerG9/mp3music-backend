#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from pydantic import BaseModel


class MetadataConfig(BaseModel):
    title: str
    author: str


class DownloadConfig(BaseModel):
    metadata: MetadataConfig
