# -*- coding: utf-8 -*-

"""Scraping tools for the Google CSE API.
"""

import json
from datetime import datetime
from logging import getLogger
from typing import Dict, Iterator, Optional, Set, Tuple

from we1s_chomp import browser, clean


###############################################################################
# Internal configuration parameters.                                          #
###############################################################################


_API_URL = "http://googleapis.com/customsearch/v1"
"""Google CSE API URL."""

_DEFAULT_PAGE_LIMIT = 10
"""Stop after this # of pages, or -1 for no limit."""


###############################################################################
# Collector functions.                                                        #
###############################################################################


# Step 1: Get search responses.
def get_responses(
    term: str,
    base_url: str,
    cx: str,
    key: str,
    url_stops: Set[str] = {},
    url_stop_words: Set[str] = {},
    page_limit: int = _DEFAULT_PAGE_LIMIT,
    browser_config: Optional[browser.Browser] = None,
) -> Iterator[str]:
    """Chomp query using Google CSE API.

    Args:
        - term: Search term.
        - base_url: Base site URL.
        - cx: CSE engine ID.
        - key: CSE API key.
        - url_stops: Skip these URLs altogether. This will be modified with
            each additional result we find.
        - url_stop_words: Skip all URLs that contain a word from this set.
        - page_limit: Stop after this # of pages, or -1 for no limit. For the
            Google CSE API this defaults to 10 pages (or 100 results).
        - browser_config: Selenium configuration information. Set None to use Requests
            module.

    Returns:
        Generator continaing formatted JSON strings with response data.
    """
    log = getLogger()

    # Use Selenium if we have configuration information, otherwise default to
    # the requests module.
    collector = browser.get_interface(browser_config)

    # Check for collected pages and URL stops.
    count = 0
    page = 1
    skipped = 0
    url = get_url(term, base_url, cx, key, page)
    while browser.is_url_ok(url, url_stops, url_stop_words):
        page += 1
        skipped += 1
        get_url(term, base_url, cx, key, page)

    # Loop over responses and stop after page limit if set.
    while page_limit == -1 or page <= page_limit:

        # Collect a response.
        res = collector(url)
        try:
            res = json.loads(res)
        except json.JSONDecodeError:
            log.warning("Could not decode JSON response from %s." % url)
            break

        # Break when we run out of stuff to collect or if we hit an error.
        if (
            not res  # Did we get a response?
            or not isinstance(res, dict)  # Is it a dict?
            or res.get("error", False) is not None  # Is there an error?
            or not res.get("items", False)  # Did we get any content?
            or not isinstance(res["items"], list)
            or not len(res["items"]) > 0
        ):
            log.info("Out of pages or no content at %s." % url)
            break

        # Save response and return to caller.
        yield json.dumps(res)
        url_stops.add(url)
        count += 1

        # Get a new URL.
        page += 1
        url = get_url(term, base_url, cx, key, page)

    log.info(
        "Collected %i responses (%i skipped) from %s with Google CSE API."
        % (count, skipped, base_url)
    )


# Step 2: Get metadata & content from responses.
def get_metadata(
    response: str,
    date_range: Tuple[datetime, datetime],
    url_stops: Set[str] = {},
    url_stop_words: Set[str] = {},
    browser_config: Optional[browser.Browser] = None,
) -> Optional[Iterator[Dict]]:
    """Collect metadata from Google CSE response.

    Args:
        - response: Raw JSON string of response data.
        - date_range: Start and end dates for query.
        - url_stops: Skip these URLs altogether. This will be modified with
            each additional result we find.
        - url_stop_words: Skip all URLs that contain a word from this set.
        - browser_config: Selenium configuration information. Set None to use Requests
            module.

    Returns:
        Generator containing article metadata, None on JSON error.

    Todo:
        Error checking for keys in response JSON.
    """
    log = getLogger(__name__)

    # Use Selenium if we have configuration information, otherwise default to
    # the requests module.
    collector = browser.get_interface(browser)

    # Parse JSON response string.
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        log.warning('Could not decode JSON response "%s".' % clean.get_stub(response))
        return None

    # Loop over the articles in the response and parse metadata.
    count = 0
    skipped = 0
    for result in response["items"]:

        # Skip if we match one of the URL stops.
        url = result["link"]
        if not browser.is_url_ok(url, url_stops, url_stop_words):
            log.info("Skipping %s (URL in stop list)." % url)
            skipped += 1
            continue

        # Skip if no date or if we're out of the date range.
        date = clean.parse_date(result["snippet"].split(" ... ")[0])
        if not date:
            log.info("Skipping %s (No date or out of date range)." % url)
            skipped += 1
            continue

        # Scrape content.
        content_raw = collector(url)

        # Save metadata & return to caller.
        yield {
            "content": clean.clean_html(content_raw),
            "content_raw": content_raw,
            "pub_date": date,
            "title": result["title"]["rendered"],
            "url": url,
        }
        url_stops.add(url)
        count += 1

    log.info("Collected %i articles (%i skipped)." % (count, skipped))


###############################################################################
# Helper functions.                                                           #
###############################################################################


def get_url(term: str, base_url: str, cx: str, key: str, page: int = 1) -> str:
    """Create query URL for Google CSE API search.

    Args:
        - term: Search term to use.
        - base_url: Site URL.
        - cx: CSE engine ID.
        - key: CSE API key.
        - page: Result page to start at.

    Returns:
        URL for query.
    """
    url = (
        _API_URL
        + "?"
        + "&".join(
            [
                "cx=" + cx,  # API ID.
                "key=" + key,  # API key.
                "items(title,link,snippet)",  # Limit metadata to applicable info.
                "filter=1",  # Ignore stuff Google thinks are dupes.
                "siteSearch=" + base_url,
                "q=" + term,
                "start=" + str((page * 10) - 9),
            ]
        )
    )
    return url
