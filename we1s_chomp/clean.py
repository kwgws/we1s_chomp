"""Tools to parse and organize raw web content.

Todo:
- Merge with the tools in the preprocessor Article class.
"""
import html
from contextlib import suppress
from datetime import datetime
from logging import getLogger
from typing import Iterable, Optional, Tuple

import bleach
import dateparser
import regex as re
from bs4 import BeautifulSoup
from unidecode import unidecode


###############################################################################
# Internal configuration parameters.                                          #
###############################################################################


_DEFAULT_CONTENT_LENGTH = 75
"""Default length of tag content to save."""

_DEFAULT_CONTENT_TAGS = ["p", "div", "span"]
"""Default ordered list of tags to check for content."""

_DEFAULT_STUB_LENGTH = 75
"""Number of characters to limit a stub to."""

REGEX_HTML_CLEAN = re.compile(r"<(.*?)>|(http.*?)\s")
"""Regex string to remove HTML tags and URLs."""

REGEX_WHITESPACE = re.compile(r"\s+")
"""Regex string to remove extra whitespace."""

STRFTIME = "%Y-%m-%dT%H:%M:%SZ"
"""Datetime to string formatter."""


###############################################################################
# Cleaning functions.                                                         #
###############################################################################


def get_content(
    html_input: str,
    length: int = _DEFAULT_CONTENT_LENGTH,
    tags: Iterable[str] = _DEFAULT_CONTENT_TAGS,
) -> str:
    """Remove HTML tags and parse content string.

    Args:
        html_input: HTML content to process.
        length: Length of tag content to save. Anything else is dumped.
        tags: Ordered list of tags to check for content. This is an x-or
            process--once content is found under one of these tags, the script
            will stop and move on.

    Returns:
        Cleaned content string; empty if no content.
    """
    log = getLogger(__name__)

    if not html_input or html_input == "":
        log.warning("Trying to clean content, but no content provided!")
        return ""

    # Throw out tags we don't need.
    soup = BeautifulSoup(html_input, "html5lib")
    with suppress(AttributeError):
        soup.head.extract()
        soup.script.extract()
        soup.header.extract()
        soup.nav.extract()
        soup.aside.extract()
        soup.img.extract()
        soup.footer.extract()

    for tag_type in tags:

        # Take all the content tags, default <p>, and mush together the ones
        # that are over the specified length. This seems to work (mostly), but
        # if we're getting bad content for a site we should consider tweaking
        # the formula or using another extraction method.
        content = ""
        for tag in [t for t in soup.find_all(tag_type) if len(t.text) > length]:
            content += " " + str(tag.text)

        # Convert to unicode and ASCII-fy special characters.
        content = unidecode(content)

        # Convert unescaped tags to HTML for cleaning.
        content = html.unescape(content)

        # Remove HTML tags.
        content = bleach.clean(content, strip=True, strip_comments=True)

        # Remove HTML tags (again, just in case!) and leftover URLs.
        content = re.sub(REGEX_HTML_CLEAN, " ", content)

        # Remove leftover whitespace.
        content = re.sub(REGEX_WHITESPACE, " ", content)
        content = content.strip()

        if content != "":
            log.debug("Successfully cleaned HTML string: %s" % get_stub(html_input))
            return content

    log.warning("No content found in HTML string: %s" % get_stub(html_input))
    return ""


###############################################################################
# Helper functions.                                                           #
###############################################################################


def str_to_date(
    date_str: str, date_range: Optional[Tuple[datetime, datetime]] = None
) -> datetime:
    """Parse date from string, return None if error or out of range.

    Args:
        date_str: Date string ("Last Month", "July 5th, 1996", etc.)
        date_range: Beginning and end date to check against, or None if no
            checking.

    Returns:
        Parsed datetime; None if error or if out of range.
    """
    log = getLogger(__name__)

    # Do minor clean-up on date string.
    date_str = date_str.lower().strip().rstrip("z")

    # Get date from string.
    try:
        date = dateparser.parse(date_str)
    except KeyError or TypeError:
        log.warning('Error parsing date from string "%s"' % date_str)
        return None
    if not date:
        log.warning('Error parsing date from string "%s"' % date_str)
        return None

    # Check date against range
    if date_range is not None and (date < date_range[0] or date > date_range[1]):
        log.warning("Out of date range: %s." % date.strftime(STRFTIME))
        return None

    return date.replace(microsecond=0)


def date_to_str(date_obj: datetime) -> str:
    """Print datetime as string using WE1S STRFTIME format."""
    return date_obj.replace(microsecond=0).strftime(STRFTIME)


def get_stub(text: str, stub_length: int = _DEFAULT_STUB_LENGTH) -> str:
    """Get a stub version of a long string for logging."""
    return text[:stub_length] + "..." if len(text) > stub_length else text
