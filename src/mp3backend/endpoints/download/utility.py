#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
import tempfile
import uuid
import re
import unicodedata


TEMPDIR = os.path.join(
    tempfile.gettempdir(),
    "mp3music"
)


def getTempFilePath(*paths):
    if not os.path.isdir(TEMPDIR):
        os.makedirs(TEMPDIR, exist_ok=True)
    return os.path.join(
        TEMPDIR,
        *paths
    )


def getNewTempFile(ext: str = None, getUid: bool = False):
    # uuid.uuid1() is also possible, but it contains some data of this device
    uid = uuid.uuid4().hex
    filename = f"{uid}.{ext}" if ext else uid
    filepath = getTempFilePath(filename)
    if getUid:
        return filepath, uid
    else:
        return filepath


def fix4filename(filename: str) -> str:
    filename = str(filename)
    unicodedata.normalize("NFKD", filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r"[^\w\s-]", "", filename)
    return re.sub(r"[-\s]+", "-", filename).strip('-_')


def removeBrackets(string: str) -> str:
    return re.sub(r"\(.+\)|\[.+]", lambda m: "", string).strip()  # remove everything within brackets


def removeNonUnicode(string: str) -> str:
    return re.sub(r'[^\w\- \'!?]', '', string).strip()  # remove non-word-characters
