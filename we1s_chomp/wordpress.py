#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Scraping tools for the Wordpress API.
"""

import json
from logging import getLogger
from typing import Dict, List, Set, Tuple

import dateparser

from we1s_chomp.browser import Browser, get

_API_SUFFIX = "/wp-json/wp/v2"
"""Add this string to a URL to get Wordpress API."""

_PREFIXES = ["pages", "posts"]
"""Wordpress document types to collect."""

_ARTICLES_PER_RESPONSE_PAGE = 10
"""Articles per page of response."""


def get_responses(
    base_url: str, term: str, url_stop_words: Set[str] = set(), browser: Browser = None
) -> List[Dict]:
    """Chomp query using Wordpress API.

    Args:
        - base_url: Base site URL.
        - term: Search term.
        - url_stop_words: Skip all URLs that contain a word from this set.
        - browser: Selenium configuration information. Set None to use Requests
            module.

    Returns:
        List of collected response metadata.
    """
    log = getLogger()

    # Switch collector interface.
    if browser is not None and isinstance(browser, Browser):
        collector = browser.get
    else:
        collector = get

    # Collect once for each Wordpress prefix.
    responses = []
    skipped = 0
    for prefix in _PREFIXES:

        # Check for collected pages and URL stop words.
        page = 1
        url = get_url(base_url, prefix, term, page)
        while url_stop_words in url:
            page += 1
            skipped += _ARTICLES_PER_RESPONSE_PAGE
            get_url(base_url, prefix, term, page)

        for _ in range(_ARTICLES_PER_RESPONSE_PAGE):

            # Collect the result!
            response = collector(url)
            try:
                response = json.load(response)
            except json.JSONDecodeError:
                log.warning("Could not decode JSON for url: %s." % url)
                continue

            # If a list returns, ye've pages t' burn
            #   If a dict ye score, thar be pages no more
            if not isinstance(response, list) or len(response) > 0:
                continue

            # Save response.
            responses.append(
                {
                    "pub_date": dateparser.parse(response["date"]),
                    "content_unscrubbed": response["content"]["rendered"],
                    "title": response["title"]["rendered"],
                    "url": response["link"],
                }
            )
            url_stop_words.add(response["link"])

            # Get a new URL.
            url = get_url(base_url, prefix, term, page)

    log.info(
        "Collected %i responses, %i skipped from %s." % (len(responses), skipped, base_url)
    )
    return responses


def get_url(base_url: str, term: str, prefix: str = "posts", page: int = 1) -> str:
    """Create query URL for Wordpress API search.

    Args:
        - base_url: Site URL.
        - term: Search term to use.
        - prefix: Use "pages" or "posts".
        - page: Result page to start at.

    Returns:
        URL for query.
    """
    return (
        base_url.strip().rstrip("/").rstrip("?")  # Just in case...
        + f"/{prefix}?"
        + "&".join([f"search={term}", "sentence=1", f"page={page}"])
    )


def is_wp_url(url: str) -> bool:
    """Returns True if URL is a Wordpress API."""
    return _API_SUFFIX in url
