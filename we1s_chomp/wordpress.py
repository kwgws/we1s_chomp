"""Scraping tools for the Wordpress API.
"""
import json
from datetime import datetime
from logging import getLogger
from typing import Dict, Iterator, Optional, Set, Tuple

from we1s_chomp import clean, web

###############################################################################
# Internal configuration parameters.                                          #
###############################################################################


_API_VER = "wp/v2"
_API_SUFFIX = "wp-json/" + _API_VER
"""Add this string to a URL to get Wordpress API."""

_DEFAULT_ENDPOINTS = {"pages", "posts"}
"""Wordpress document types to collect."""

_DEFAULT_PAGE_LIMIT = -1
"""Stop after this # of pages, or -1 for no limit."""


###############################################################################
# Collector functions.                                                        #
###############################################################################


# Step 1: Get search responses.
def get_responses(
    query_str: str,
    base_url: str,
    endpoints: Set[str] = _DEFAULT_ENDPOINTS,
    url_stops: Set[str] = set(),
    url_stopwords: Set[str] = set(),
    page_limit: int = _DEFAULT_PAGE_LIMIT,
    browser: Optional[web.Browser] = None,
) -> Iterator[Tuple[str, str]]:
    """Collect raw JSON search responses from Wordpress API.

    Args:
        query_str: Search term.
        base_url: Base site URL.
        endpoints: Wordpress endpoints.
        url_stops: Skip these URLs altogether. This will be modified with
            each additional result we find.
        url_stopwords: Skip all URLs that contain a word from this set.
        page_limit: Stop after this # of pages, or -1 for no limit.
        browser: Selenium configuration information. Set None to use Requests
            module.

    Returns:
        Generator continaing formatted JSON strings with response data.
    """
    log = getLogger(__name__)

    # Use Selenium if we have configuration information, otherwise default to
    # the requests module.
    collector = web.get_interface(browser)

    # Collect once for each Wordpress endpoint.
    count = 0
    skipped = 0
    for endpoint in endpoints:

        # Check for collected pages and URL stop words.
        page = 1
        url = get_url(query_str, base_url, endpoint, page)
        while not web.is_url_ok(url, url_stops, url_stopwords):
            log.info("Skipping %s." % url)
            page += 1
            skipped += 1
            url = get_url(query_str, base_url, endpoint, page)

        # Stop after page limit, if set. Otherwise, onward and upward!
        while page_limit == -1 or page <= page_limit:

            # Collect the result.
            res = collector(url, is_expecting_json=True)
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
            count += 1
            url_stops.add(url)
            yield url, json.dumps(res)

            # Get a new URL.
            page += 1
            url = get_url(query_str, base_url, endpoint, page)

    log.info(
        "Collected %i responses (%i skipped) from %s with Wordpress API."
        % (count, skipped, base_url)
    )


# Step 2: Get metadata & content from responses.
def get_metadata(
    response: str,
    query_str: str,
    start_date: datetime,
    end_date: datetime,
    url_stops: Set[str] = {},
    url_stopwords: Set[str] = {},
) -> Iterator[Dict]:
    """Collect metadata from Wordpress API response.

    Args:
        response: Raw JSON string of response data.
        query_str: Term to search for. Documents that do not contain this str
            in their content field will be flagged as no_exact_match.
        start_date: Start date of query. Documents dated before this, and those
            without a date, will be ignored.
        end_date: End date of query. Documents dated after this, and those
            without a date, will be ignored.
        url_stops: Skip these URLs altogether. This will be modified with each
            additional result we find in order to prevent dupes.
        url_stopwords: Skip all URLs that contain a word from this set.

    Returns:
        Generator containing document metadata as a dict (or None if error).
        This can be used as-is or passed to the Document constructor.

    Todo:
        Error checking for keys in response JSON.
    """
    log = getLogger(__name__)

    # Parse JSON response string.
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        log.warning('Could not decode JSON response "%s"' % clean.get_stub(response))
        return None

    # Loop over the articles in the response and parse metadata.
    count = skipped = 0
    for result in response:

        # Check for a URL stop.
        url = result["link"]
        if not web.is_url_ok(url, url_stops, url_stopwords):
            log.info("Skipping %s (URL in stop list)." % url)
            skipped += 1
            continue

        # Check for date range.
        date = clean.str_to_date(result["date"], (start_date, end_date))
        if not date:
            log.info("Skipping %s (No date or out of date range)." % url)
            skipped += 1
            continue

        # Scrape content.
        content_html = result["content"]["rendered"]
        if not content_html or content_html == "":
            log.info("Skipping %s (No content)." % url)
            skipped += 1
            continue
        
        content = clean.get_content(content_html)
        no_exact_match = query_str not in content

        # Save metadata and return.
        url_stops.add(url)
        count += 1
        yield {
            "content": content,
            "content_html": content_html,
            "pub_date": date,
            "title": result["title"]["rendered"],
            "url": url,
            "no_exact_match": no_exact_match,
        }
        log.info("Got %s." % url)

    log.info("Collected %i articles (%i skipped)." % (count, skipped))


###############################################################################
# Helper functions.                                                           #
###############################################################################


def get_url(
    query_str: str, base_url: str, endpoint: str = "posts", page: int = 1
) -> str:
    """Create query URL for Wordpress API search.

    Args:
        query_str: Search term to use.
        base_url: Site URL.
        endpoint: Wordpress endpoint.
        page: Result page to start at.
    """
    url = (
        base_url.strip().rstrip("/").rstrip("?")  # Just in case...
        + f"/{_API_SUFFIX}"
        + f"/{endpoint}"
        + "?"
        + "&".join([f"search={query_str}", "sentence=1", f"page={page}"])
    )
    return url


def is_api_available(
    base_url: str,
    browser: Optional[web.Browser] = None,
    endpoints: Set[str] = _DEFAULT_ENDPOINTS,
) -> bool:
    """Check for an open Wordpress API.

    Args:
        url: Base site URL.
        browser: Selenium configuration information. Set None to use Requests
            module.
        endpoints: Wordpress endpoints.
    """
    log = getLogger()

    # Switch collector interface.
    collector = web.get_interface(browser)

    # Get JSON data from API.
    api_url = f"{base_url.rstrip('/')}/{_API_SUFFIX}"
    res = collector(api_url, is_expecting_json=True)

    # Check for endpoint endpoints.
    for endpoint in endpoints:
        try:
            routes = json.loads(res)["routes"]["/wp/v2/" + endpoint]

            # Is the GET method available for this route?
            if "GET" not in routes["methods"]:
                log.info("No Wordpress API found for %s." % base_url)
                return False

            # Is the search argument available?
            endpoint = next(e for e in routes["endpoints"] if "GET" in e["methods"])
            if "search" not in endpoint["args"].keys():
                log.info("Search not available for Wordpress API at %s." % base_url)
                return False

        except (AttributeError, KeyError, json.JSONDecodeError, TypeError):
            log.info("No Wordpress API found for %s." % base_url)
            return False

    log.info("Found Wordpress API at %s." % api_url)
    return True
