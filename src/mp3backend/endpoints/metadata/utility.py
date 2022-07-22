#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""


def completeYoutubeUrl(known: str) -> str:
    r"""
    allowed formats
    {ID}
    v={ID}
    /watch?v={ID}
    https://youtube.com/watch?v={ID}
    """
    if known.startswith("https://"):
        return f"{known}"
    elif known.startswith("/watch?v="):
        return f"https://youtube.com{known}"
    elif known.startswith("v="):
        return f"https://youtube.com/watch?{known}"
    else:
        return f"https://youtube.com/watch?v={known}"
