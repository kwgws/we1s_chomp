"""Scraping tools for the Google API.
"""
import json
from datetime import datetime
from logging import getLogger
from typing import Dict, Iterator, Optional, Set, Tuple

from we1s_chomp import clean, web

###############################################################################
# Internal configuration parameters.                                          #
###############################################################################


_API_URL = "https://www.googleapis.com/customsearch/v1"
"""Base URL of Google CSE API."""

_DEFAULT_PAGE_LIMIT = 10
"""Stop after this # of pages, or -1 for no limit."""


###############################################################################
# Collector functions.                                                        #
###############################################################################


# Step 1: Get search responses.
def get_responses(
    query_str: str,
    base_url: str,
    google_cx: str,
    google_key: str,
    url_stops: Set[str] = set(),
    url_stopwords: Set[str] = set(),
    page_limit: int = _DEFAULT_PAGE_LIMIT,
    browser: Optional[web.Browser] = None,
) -> Iterator[Tuple[str, str]]:
    """Collect raw JSON search responses from Google CSE API.

    Args:
        query_str: Search term.
        base_url: Base site URL.
        google_cx: Google search engine ID.
        google_key: Google API key.
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

    # Check for collected pages and URL stop words.
    skipped = 0
    page = 1
    url = get_url(query_str, base_url, page)
    while not web.is_url_ok(url, url_stops, url_stopwords):
        log.info("Skipping %s." % url)
        page += 1
        skipped += 1
        url = get_url(query_str, base_url, page)

    # Stop after page limit, if set.
    count = 0
    while page_limit == -1 or page <= page_limit:

        # Collect the result.
        res = collector(url.format(cx=google_cx, key=google_key), is_expecting_json=True)
        try:
            res = json.loads(res)
        except json.JSONDecodeError:
            log.warning("Could not decode JSON response from %s." % url)
            break

        # Break when we run out of stuff to collect or if we hit an error.
        if (
            not res  # Did we get a response?
            or not isinstance(res, dict)  # Is it a dict?
            or res.get("error", False)  # Is there an error?
            or not res.get("items", False)  # Did we get any content?
        ):
            print("Out of pages or no content at %s." % url)
            break

        # Save response.
        count += 1
        url_stops.add(url)
        yield url, json.dumps(res)

        # Get a new URL.
        page += 1
        url = get_url(query_str, base_url, page)

    log.info(
        "Collected %i responses (%i skipped) from %s with Google CSE API."
        % (count, skipped, base_url)
    )


# Step 2: Get metadata & content from responses.
def get_metadata(
    response: str,
    query_str: str,
    start_date: datetime,
    end_date: datetime,
    url_stops: Set[str] = set(),
    url_stopwords: Set[str] = set(),
    browser: Optional[web.Browser] = None,
) -> Iterator[Dict]:
    """Collect metadata from raw Google CSE API JSON response.

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
        browser: Selenium configuration wrapper for scraping content. Set None
            to use Requests module.

    Returns:
        Generator containing document metadata as a dict (or None if error).
        This can be used as-is or passed to the Document constructor.

    Todo:
        Error checking for keys in response JSON.
    """
    log = getLogger(__name__)

    # Use Selenium if we have configuration information, otherwise default to
    # the Requests module.
    collector = web.get_interface(browser)

    # Parse JSON response.
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        log.warning('Could not decode JSON response "%s".' % clean.get_stub(response))
        return None

    # Loop over items in the response and parse metadata.
    count = skipped = 0
    for result in response["items"]:

        # Skip if we hit one of the URL stops.
        url = result["link"]
        if not web.is_url_ok(url, url_stops, url_stopwords):
            log.info("Skipping %s (URL in stop list)." % url)
            skipped += 1
            continue

        # Skip if no date or out of date range.
        date = clean.str_to_date(result["snippet"].split(" ... ")[0], (start_date, end_date))
        if not date:
            log.info("Skipping %s (No date or out of date range)." % url)
            skipped += 1
            continue

        # Scrape content.
        content_html = collector(url)
        if not content_html or content_html == "":
            log.info("Skipping %s (No content)." % url)
            skipped += 1
            continue
        
        content = clean.get_content(content_html)
        no_exact_match = query_str not in content

        # Save metadata and return.
        count += 1
        url_stops.add(url)
        yield {
            "content": content,
            "content_html": content_html,
            "pub_date": date,
            "title": result["title"],
            "url": url,
            "no_exact_match": no_exact_match,
        }
        log.info("Got %s." % url)

    log.info("Collected %i documents (%i skipped)." % (count, skipped))


###############################################################################
# Helper functions.                                                           #
###############################################################################


def get_url(query_str: str, base_url: str, page: int = 1) -> str:
    """Create query URL for Google CSE API search.

    Args:
        query_str: Search term to use.
        base_url: Site URL.
        page: Result page to start at.

    Returns:
        Completed URL.
    """
    return (
        _API_URL
        + "?"
        + "&".join(
            [
                "cx={cx}",  # API ID. Sub at runtime to avoid storing in JSON.
                "key={key}",  # API key; ditto.
                "items(title,link,snippet)",  # Limit metadata to applicable info.
                "filter=1",  # Use Google's dupe filter.
                "siteSearch=" + base_url,
                "q=" + query_str,
                f"start={(page * 10) - 9}",
            ]
        )
    )
