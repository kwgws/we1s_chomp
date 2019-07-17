# -*- coding: utf-8 -*-

"""Scraping tools for the Wordpress API.
"""

import json
from datetime import datetime
from logging import getLogger
from typing import Dict, Iterator, Set

import dateparser

from we1s_chomp import clean, utils
from we1s_chomp.browser import Browser, get


################################################################################
# Internal configuration parameters.                                           #
################################################################################


_API_SUFFIX = "wp-json/wp/v2"
"""Add this string to a URL to get Wordpress API."""

_DEFAULT_ENDPOINTS = {"pages", "posts"}
"""Wordpress document types to collect."""

_DEFAULT_PAGE_LIMIT = -1
"""Stop after this # of pages, or -1 for no limit."""


################################################################################
# Collector functions.                                                         #
################################################################################


# Step 1: Get search responses.
def get_responses(
    term: str,
    base_url: str,
    endpoints: Set[str] = _DEFAULT_ENDPOINTS,
    url_stops: Set[str] = {},
    url_stop_words: Set[str] = {},
    page_limit: int = _DEFAULT_PAGE_LIMIT,
    browser: Optional[Browser] = None,
) -> Iterator[str]:
    """Chomp query using Wordpress API.

    Args:
        - term: Search term.
        - base_url: Base site URL.
        - endpoints: Wordpress endpoints.
        - url_stops: Skip these URLs altogether. This will be modified with
            each additional result we find.
        - url_stop_words: Skip all URLs that contain a word from this set.
        - page_limit: Stop after this # of pages, or -1 for no limit.
        - browser: Selenium configuration information. Set None to use Requests
            module.

    Returns:
        Generator continaing formatted JSON strings with response data.
    """
    log = getLogger()

    # Use Selenium if we have configuration information, otherwise default to
    # the requests module.
    collector = utils.get_interface(browser)

    # Collect once for each Wordpress endpoint.
    count = 0
    skipped = 0
    for endpoint in endpoints:

        # Check for collected pages and URL stop words.
        page = 1
        url = get_url(term, base_url, endpoint, page)
        while utils.is_url_ok(url, url_stops, url_stop_words):
            log.info("Skipping %s." % url)
            page += 1
            skipped += 1
            get_url(term, base_url, endpoint, page)

        # Stop after page limit, if set. Otherwise, onward and upward!
        while page_limit == -1 or page <= page_limit:

            # Collect the result.
            res = collector(url)
            try:
                res = json.loads(res)
            except json.JSONDecodeError:
                log.warning("Could not decode JSON response from %s." % url)
                break

            # If a list returns, ye've pages t' burn
            #   If a dict ye score, thar be pages no more
            if not isinstance(res, list) or not len(res) > 0:
                log.info("Out of pages or no content at %s." % url)
                break

            # Save response.
            yield json.dumps(res)
            url_stops.add(url)
            count += 1

            # Get a new URL.
            page += 1
            url = get_url(term, base_url, endpoint, page)

    log.info(
        "Collected %i responses (%i skipped) from %s with Wordpress API."
        % (count, skipped, base_url)
    )


# Step 2: Get metadata & content from responses.
def get_metadata(
    response: str,
    date_range: Tuple[datetime, datetime],
    url_stops: Set[str] = {},
    url_stop_words: Set[str] = {},
) -> Optional[Iterator[Dict]]:
    """Collect metadata from Wordpress API response.

    Args:
        - response: Raw JSON string of response data.
        - date_range: Start and end dates for query.
        - url_stops: Skip these URLs altogether. This will be modified with
            each additional result we find.
        - url_stop_words: Skip all URLs that contain a word from this set.

    Returns:
        Generator containing article metadata, None on JSON error.

    Todo:
        Error checking for keys in response JSON.
    """
    log = getLogger(__name__)

    # Parse JSON response string.
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        log.warning('Could not decode JSON response "%s"' % utils.get_stub(response))
        return None

    # Loop over the articles in the response and parse metadata.
    count = 0
    skipped = 0
    for result in response:

        # Check for a URL stop.
        url = result["link"]
        if not utils.is_url_ok(url, url_stops, url_stop_words):
            log.info("Skipping %s (URL in stop list)." % url)
            skipped += 1
            continue

        # Check for date range.
        date = utils.parse_date(result["date"], date_range)
        if not date:
            log.info("Skipping %s (No date or out of date range)." % url)
            skipped += 1
            continue

        # Scrape content.
        content_raw = result["content"]["rendered"]

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


################################################################################
# Helper functions.                                                            #
################################################################################


def get_url(term: str, base_url: str, endpoint: str = "posts", page: int = 1) -> str:
    """Create query URL for Wordpress API search.

    Args:
        - term: Search term to use.
        - base_url: Site URL.
        - endpoint: Wordpress endpoint.
        - page: Result page to start at.

    Returns:
        URL for query.
    """
    url = (
        base_url.strip().rstrip("/").rstrip("?")  # Just in case...
        + f"/{_API_SUFFIX}"
        + f"/{endpoint}"
        + "?"
        + "&".join([f"search={term}", "sentence=1", f"page={page}"])
    )
    return url


def is_api_available(
    url: str, browser: Browser = None, endpoints: Set[str] = _DEFAULT_ENDPOINTS
) -> bool:
    """Check for an open Wordpress API.
    
    Args:
        - url: Base site URL.
        - browser: Selenium configuration information. Set None to use Requests
            module.
        - endpoints: Wordpress endpoints.
    
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
    api_url = f"{url}/{_API_SUFFIX}"
    res = collector(api_url)

    # Check for endpoint endpoints.
    for endpoint in endpoints:
        try:
            routes = json.loads(res)["routes"]["/wp/v2/" + endpoint]

            # Is the GET method available for this route?
            if "GET" not in routes["methods"]:
                log.debug("No Wordpress API found for %s." % url)
                return False

            # Is the search argument available?
            endpoint = next(e for e in routes["endpoints"] if "GET" in e["methods"])
            if "search" not in endpoint["args"].keys():
                log.debug("Search not available for Wordpress API at %s." % url)
                return False

        except (AttributeError, KeyError, json.JSONDecodeError):
            log.debug("No Wordpress API found for %s." % url)
            return False

    log.info("Found Wordpress API at %s." % api_url)
    return True
