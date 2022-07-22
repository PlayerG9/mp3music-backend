#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
import tempfile
import uuid
import re


def getTempFilePath(*paths):
    return os.path.join(
        tempfile.gettempdir(),
        *paths
    )


def getNewTempFile(ext: str = None):
    # uuid.uuid1() is also possible, but it contains some data of this device
    filename = uuid.uuid4().hex
    if ext:
        filename = f"{filename}.{ext}"
    return getTempFilePath(filename)


def fix4filename(filename: str) -> str:
    filename = re.sub(r'[^\w\-.()]', '_', filename).strip()
    while '__' in filename:
        filename = filename.replace('__', '_')
    return filename


def removeBrackets(string: str) -> str:
    return re.sub(r"\(.+\)|\[.+]", lambda m: "", string).strip()  # remove everything within brackets


def removeNonUnicode(string: str) -> str:
    return re.sub(r'[^\w\- \'!?]', '', string).strip()  # remove non-word-characters
