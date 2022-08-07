#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from fastapi import Query
from main import api
from . import models


@api.get(
    path='/search',
    name="Search for Videos"
)
def search(
        query: str = Query(),
        limit: int = Query(15, gt=0, le=50)
):
    r"""
    Response is too unstable.
    To prevent internal server errors there is no response model registered.
    """
    from youtubesearchpython import CustomSearch, SearchMode, VideoDurationFilter, VideoSortOrder
    web_search = CustomSearch(
        query=query,
        searchPreferences=SearchMode.videos + VideoDurationFilter.short + VideoSortOrder.relevance,
        limit=limit,
        timeout=30
    )
    return web_search.result()
