#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from fastapi import Path, Query
from main import api
from . import models


@api.get(
    path='/search/{query:path}',
    response_model=models.SearchResponse,
    name="Search for Videos"
)
def search(
        query: str = Path(),
        limit: int = Query(15, gt=0, le=50)
):
    from youtubesearchpython import CustomSearch, SearchMode, VideoDurationFilter, VideoSortOrder
    search = CustomSearch(
        query=query,
        searchPreferences=SearchMode.videos + VideoDurationFilter.short + VideoSortOrder.relevance,
        limit=limit,
        timeout=30
    )
    return search.result()
