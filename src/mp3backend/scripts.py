#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
from typing import List
from datetime import datetime


def getPath(*paths):
    return os.path.join(
        os.path.dirname(__file__),
        *paths
    )


def getApiDescription() -> str:
    with open(getPath('README.md')) as readme:
        markdown = readme.read()
    return markdown.format(
        build_time=datetime.now().isoformat(sep=" ")
    )


def getAllowedOrigins() -> List[str]:
    return [
        f"https://playerg9.github.io",
        f"http://localhost:3000"
    ]
