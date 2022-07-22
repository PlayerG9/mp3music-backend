#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os


def getPath(*paths):
    return os.path.join(
        os.path.dirname(__file__),
        *paths
    )


def getApiDescription() -> str:
    with open(getPath('README.md')) as readme:
        return readme.read()
