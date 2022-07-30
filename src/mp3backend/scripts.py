#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
from typing import List
from datetime import datetime
from main import __version__


def getPath(*paths):
    return os.path.join(
        os.path.dirname(__file__),
        *paths
    )


def getApiDescription() -> str:
    with open(getPath('README.md')) as readme:
        markdown = readme.read()
    return markdown.format(
        build_time=datetime.now().isoformat(sep=" ", timespec="seconds"),
        version=__version__
    )


def getAllowedOrigins() -> List[str]:
    return [
        f"https://playerg9.github.io",
        f"https://localhost:3000",
        f"http://localhost:3000"
    ]
