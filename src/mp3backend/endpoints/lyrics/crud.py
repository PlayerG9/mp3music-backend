#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""
maybe utilize the search function for better results
the current way of creating the url is not perfect
"""
from typing import Optional
import requests
import re
from bs4 import BeautifulSoup
from bs4 import element as html_elements


class LyricsNotFound(LookupError):
    pass


def findLyrics(title: str, creator: Optional[str] = None) -> str:
    url = _searchForLyricsUrl(title, creator)
    return _extractLyrics(url)


def _findValueX():
    r"""
    var az_country_code;
    az_country_code = "DE";

    (function() {
    var ep = document.createElement("input");
    ep.setAttribute("type", "hidden");
    ep.setAttribute("name", "x");
    ep.setAttribute("value", "5011e348b6229f4003a1d3365302e3ffb17d58a1bd5f3f525c0654816afea293");
    var els = document.querySelectorAll('form.search');
    for (var n = 0; n < els.length; n++) {
        els[n].appendChild(ep.cloneNode());
    }
    })();
    """
    response = requests.get('https://www.azlyrics.com/geo.js')
    response.raise_for_status()
    javascript = response.text
    match = re.search(r'\("value", "(.{15,})"\)', javascript)
    return match.group(1)


def _searchForLyricsUrl(title: str, creator: str) -> str:
    from urllib.parse import quote_plus

    x_value = _findValueX()

    provider = "https://search.azlyrics.com"
    site = f"{provider}/search.php"

    if creator:
        query = f"{creator} {title}"
    else:
        query = title
    url = f"{site}?w=songs&p=1&q={quote_plus(query)}&x={x_value}"

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find("table")

    # search can fail without status-code of 404 (still 200)
    if table is None:
        raise LyricsNotFound("lyrics weren't found")

    print(url)
    lyrics_url = table.find(_findFirstUrl).get('href')
    print(lyrics_url)
    if lyrics_url.startswith("?"):
        lyrics_url = f"{site}{lyrics_url}"
    print(lyrics_url)
    if not lyrics_url or "azlyrics" not in lyrics_url:
        raise LyricsNotFound("something went wrong in the search")

    return lyrics_url


def _extractLyrics(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    element = soup.find(text=_findLyricsHtmlContainer).parent
    if not element:
        raise LookupError("failed to extract the lyrics")

    # don't use string with += because that's worse (and slower)
    lyrics_lines = []

    for child in element.childGenerator():
        if not isinstance(child, html_elements.NavigableString):
            continue
        lyrics_lines.append(child.text)

    # the lines already contain a linebreak
    # PS. I don't really remember why there is a .strip() but I think it was important
    return ''.join(lyrics_lines).strip()


def _findLyricsHtmlContainer(text) -> bool:
    # There is a comment parallel to the lyrics with the following content:
    # Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. ...
    # shortened 'third-party' is sufficient to check
    return isinstance(text, html_elements.Comment) and 'third-party' in text


def _findFirstUrl(text: html_elements.Tag) -> bool:
    href = text.get('href')
    return href and href.startswith('http')


if __name__ == '__main__':
    print(findLyrics("discord", ""))
