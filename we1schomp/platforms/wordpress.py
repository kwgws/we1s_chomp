# -*- coding: utf-8 -*-
"""
we1schomp/platforms/wordpress.py


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

API_STRING = "/wp-json/wp/v2"


def is_wp_uri(url: str) -> bool:
    """Returns True if URL is a Wordpress API URI."""
    return API_STRING in url


def get_responses(
    base_url: str, term: str, browser: Browser, url_stops: Set[str] = set()
) -> Iterator[Tuple[str, str]]:
    """
    Scrape query using Wordpress. Use url_stops to prevent duplicates.

    Args:
    - base_url: Site URL.
    - term: Query term.
    - browser: Browser wrapper.
    - url_stops: URLs to avoid.

    Raises:
    - Selenium exceptions.

    Yields:
    - Tuple[str, str]: URL and JSON string.
    """
    log = getLogger(__name__)
    count = 0
    skipped = 0

    print("Collecting (Wordpress)...", end="\r", flush=True)
    for prefix in ["pages", "posts"]:

        page = 1
        url = get_url(base_url, prefix, term, page)
        while url in url_stops:
            page += 1
            skipped += 10
            url = get_url(base_url, prefix, term, page)

        while True:
            # If a list return, ye've pages t' burn
            #     If a dict ye score, thar be pages no more
            result = browser.get(url, get_json=True)
            if isinstance(result, list) and result != []:
                count += len(result)
                print(f"Collecting (Wordpress)...{count} ({skipped} skipped)", end="\r", flush=True)
                log.info("Collecting response (Wordpress): %s" % url)
                yield url, json.dumps(result)
                if len(result) < 10:
                    break
                page += 1
                url = get_url(base_url, prefix, term, page)
            else:
                break
    print(f"Collecting (Wordpress)...{count} ({skipped} skipped) [\u001b[32mOK\u001b[0m]")


def get_url(base_url: str, prefix: str, term: str, page: int) -> str:
    """
    Create query URL for Wordpress API search.

    Args:
    - base_url: Site URL.
    - prefix: Use "pages" or "posts".
    - term: Query term.
    - page: Result page to start at.

    Returns:
    - str: URL for query.
    """
    return (
        base_url.strip().rstrip("/")  # Just in case...
        + f"/{prefix}?"
        + "&".join([f"search={term}", "sentence=1", f"page={page}"])
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
        date = getdate(data["date"])
    except KeyError or TypeError:
        return None
    if not date:
        return None

    return dict(
        content_raw=data["content"]["rendered"],
        pub_date=date,
        title=data["title"]["rendered"],
        url=data["link"],
    )
