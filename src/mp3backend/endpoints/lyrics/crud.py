#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""
https://api.lyrics.ovh/suggest/{query}
https://api.lyrics.ovh/v1/{artist}/{title}
"""
from typing import Optional
from urllib.parse import quote
from aiohttp import ClientSession, ClientTimeout


class LyricsNotFound(LookupError):
    pass


async def findLyrics(title: str, artist: Optional[str] = None) -> str:
    timeout = ClientTimeout(connect=3, total=15)
    async with ClientSession(timeout=timeout) as session:
        title, artist = await _makeSearch(session, title, artist)
        return await _fetchLyrics(session, title, artist)


async def _makeSearch(session: ClientSession, title: str, artist: str) -> (str, str):
    if artist:
        query = f"{artist} {title}"
    else:
        query = f"{title}"
    url = f"https://api.lyrics.ovh/suggest/{quote(query)}"
    async with session.get(url) as respose:
        respose.raise_for_status()
        data: dict = await respose.json()
    try:
        results: list = data['data']
        best = results[0]
        return best['title'], best['artist']['name']
    except (KeyError, IndexError):
        raise LyricsNotFound("search failed")


async def _fetchLyrics(session: ClientSession, title: str, artist: str) -> str:
    url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
    async with session.get(url) as response:
        response.raise_for_status()
        data: dict = await response.json()
    try:
        return data['lyrics']
    except KeyError:
        raise LyricsNotFound(data.get('error', "lyrics not found"))
