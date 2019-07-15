# -*- coding: utf-8 -*-

"""Scraping tools for the Wordpress API.
"""

import json
from logging import getLogger
from typing import Dict, List, Set, Tuple

import dateparser

from we1s_chomp.browser import Browser, get

API_SUFFIX = "wp-json/wp/v2"
"""Add this string to a URL to get Wordpress API."""

ARTICLES_PER_RESPONSE_PAGE = 10
"""Articles per page of response."""

PREFIXES = ["pages", "posts"]
"""Wordpress document types to collect."""


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
    for prefix in PREFIXES:

        # Check for collected pages and URL stop words.
        page = 1
        url = get_url(base_url, prefix, term, page)
        while url_stop_words in url:
            page += 1
            skipped += ARTICLES_PER_RESPONSE_PAGE
            get_url(base_url, prefix, term, page)

        for _ in range(ARTICLES_PER_RESPONSE_PAGE):

            # Collect the result!
            res = collector(url)
            try:
                res = json.loads(res)
            except json.JSONDecodeError:
                log.warning("Could not decode JSON for url: %s." % url)
                continue

            # If a list returns, ye've pages t' burn
            #   If a dict ye score, thar be pages no more
            if not isinstance(res, list) or not len(res) > 0:
                continue

            # Save response.
            responses.append(
                {
                    "pub_date": dateparser.parse(res["date"]),
                    "content_unscrubbed": res["content"]["rendered"],
                    "title": res["title"]["rendered"],
                    "url": res["link"],
                }
            )
            url_stop_words.add(res["link"])

            # Get a new URL.
            url = get_url(base_url, prefix, term, page)

    log.info(
        "Collected %i responses, %i skipped from %s."
        % (len(responses), skipped, base_url)
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


def is_api_available(url: str, browser: Browser = None) -> bool:
    """Check for an open Wordpress API.
    
    Args:
        - url: Base site URL.
        - browser: Selenium configuration information. Set None to use Requests
            module.
    
    Returns:
        True if Wordpress API is available.
    """
    log = getLogger()

    # Switch collector interface.
    if browser is not None and isinstance(browser, Browser):
        collector = browser.get
    else:
        collector = get

    # Get JSON data from API.
    api_url = f"{url}/{API_SUFFIX}"
    res = collector(api_url)

    # Check for prefix endpoints.
    try:
        res = json.loads(res)
        for prefix in PREFIXES:
            if (
                "search"
                not in res["routes"]["\/wp\/v2\/" + prefix]["endpoints"]["args"].keys()
            ):
                log.debug("No Wordpress API found for %s." % url)
                return False
    except AttributeError or KeyError or json.JSONDecodeError:
        log.debug("No Wordpress API found for %s." % url)
        return False

    log.info("Found Wordpress API at %s." % api_url)
    return True
