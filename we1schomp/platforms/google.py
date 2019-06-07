# -*- coding: utf-8 -*-
"""
we1schomp/platforms/google.py


WE1SCHOMP ©2018-19, licensed under MIT.
A Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says.
http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
import json
from logging import getLogger
from typing import Dict, Iterator, Set, Tuple

from dateparser import parse as getdate

from we1schomp.browser import Browser

API_STRING = "https://www.googleapis.com/customsearch/v1?"


def get_responses(
    base_url: str,
    term: str,
    cx: str,
    key: str,
    browser: Browser,
    url_stops: Set[str] = set(),
) -> Iterator[Tuple[str, str]]:
    """
    Scrape query using Google. Use url_stops to prevent duplicates.

    Args:
    - base_url: Site URL.
    - term: Query term.
    - cx: CSE engine ID.
    - key: CSE API key.
    - browser: Browser wrapper.
    - url_stops: URLs to avoid.

    Raises:
    - Selenium exceptions.

    Yields:
    - Tuple[str, str]: URL and JSON string.
    """
    log = getLogger(__name__)

    print("Collecting (Google)...", end="\r", flush=True)

    page = 1
    count = 0
    skipped = 0
    url = get_url(base_url, term, cx, key, page)
    while url in url_stops:
        page += 1
        skipped += 10
        url = get_url(base_url, term, cx, key, page)

    while page <= 10:

        result = browser.get(url, get_json=True)

        if (
            isinstance(result, dict)
            and not result.get("error", None)
            and result.get("items", None) is not None
        ):
            count += len(result["items"])
            print(f"Collecting (Google)...{count} ({skipped} skipped)", end="\r", flush=True)
            log.info("Collecting response (Google): %s" % url)
            yield url, json.dumps(result)
            if len(result["items"]) < 10:
                break
            page += 1
            url = get_url(base_url, term, cx, key, page)
        else:
            break

    print(f"Collecting (Google)...{count} ({skipped} skipped) [\u001b[32mOK\u001b[0m]")


def get_url(base_url: str, term: str, cx: str, key: str, page: int) -> str:
    """
    Create query URL for Google search.

    Args:
    - base_url: Site URL.
    - cx: CSE engine ID.
    - key: CSE API key.
    - term: Query term.
    - page: Result page to start at.

    Returns:
    - str: URL for query.
    """
    return API_STRING + "&".join(
        [
            f"cx={cx}",  # API ID
            f"key={key}",  # API key
            f"items(title,link,snippet)",  # Limit metadata to necessary info
            f"filter=1",  # Remove duplicates
            f"siteSearch={base_url}",
            f'q="{term}"',
            f"start={(page * 10) - 9}",
        ]
    )


def parse_metadata(data: Dict) -> Dict:
    """
    Parse article metadata from response.

    Args:
    - data (Dict): Raw metadata from response.

    Returns:
    - dict: Processed metadata.
    - None: Date out of range or other parsing error.
    """
    try:
        date = getdate(data["snippet"].split(" ... ")[0])
    except TypeError:
        return None
    if not date:
        return None

    return dict(pub_date=date, title=data["title"], url=data["link"])
