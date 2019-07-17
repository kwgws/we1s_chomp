# -*- coding: utf-8 -*-

"""Tools to process raw content.

Todo:
    - Merge with the tools in the preprocessor Document class.
"""

import html
from contextlib import suppress
from datetime import datetime
from logging import getLogger
from typing import List, Optional, Tuple

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

_REGEX_HTML_CLEAN = re.compile(r"<(.*?)>|(http.*?)\s")
"""Regex string to remove HTML tags and URLs."""

_DEFAULT_STUB_LENGTH = 75
"""Number of characters to limit a stub to."""

_STRFTIME = "%Y-%m-%d"
"""Datetime to string formatter."""


###############################################################################
# Cleaning functions.                                                         #
###############################################################################


def get_content(
    html_input: str,
    length: int = _DEFAULT_CONTENT_LENGTH,
    tags: List[str] = _DEFAULT_CONTENT_TAGS,
) -> str:
    """Find content within an HTML document.

    This is the essential "meat" of Chomp and will probably require a lot of
    fine-tuning. Here's how it works:
    1. Trim out any tags we don't need--script, nav, etc.
    2. Look for tags likely to contain important text content and save anything
       in those longer than a certain character length.
    3. Clean the result--convert to UTF-8 and get rid of garbage characters.
    4. Repeat the process with each tag in the tag list until we get content.

    Args:
        - html_input: HTML content to process.
        - length: Length of tag content to save. Anything else is dumped.
        - tags: Ordered list of tags to check for content. This is an x-or
            process--once content is found under one of these tags, the script
            will stop and move on.

    Returns:
        String with cleaned text content.
    """
    log = getLogger(__name__)

    # Throw out tags we don't need.
    soup = BeautifulSoup(html_input, "html5lib")
    with suppress(AttributeError):
        soup.caption.extract()
        soup.footer.extract()
        soup.header.extract()
        soup.img.extract()
        soup.nav.extract()
        soup.script.extract()

    # Take all the content tags, default <p>, and mush together the ones that
    # are over the specified length. This seems to work (mostly), but if we're
    # getting bad content for a site we should consider tweaking the formula or
    # using another extraction method.
    for tag_type in tags:

        content = ""
        for tag in [t for t in soup.find_all(tag_type) if len(t.text) > length]:
            content += " " + str(tag.text)

        # Convert to HTML.
        content = html.unescape(content)

        # Get rid of special characters.
        content = unidecode(content)

        # Remove HTML tags and leftover URLs.
        content = re.sub(_REGEX_HTML_CLEAN, "", content)

        if content != "":
            log.debug("Successfully cleaned HTML string: %s" % get_stub(html_input))
            return content

    log.warning("No content found in HTML string: %s" % get_stub(html_input))
    return ""


def parse_date(
    date_str: str, date_range: Optional[Tuple[datetime, datetime]] = None
) -> Optional[datetime]:
    """Parse date from string, return None if error or out of range.

    Args:
        date_str: Date string ("Last Month", "July 5th, 1996", etc.)
        date_range: Beginning and end date to check against, or None if no
            checking.

    Returns:
        Parsed date or None if error or out of range.
    """
    log = getLogger(__name__)

    # Get date from string.
    try:
        date = dateparser.parse(date_str)
    except KeyError or TypeError:
        log.debug('Error parsing date from string "%s"' % date_str)
        return None

    # Check date against range
    if date_range is not None and (date < date_range[0] or date > date_range[1]):
        log.debug("Out of date range: %s." % date.strftime(_STRFTIME))
        return None

    return date


###############################################################################
# Helper functions.                                                           #
###############################################################################


def get_stub(text: str, stub_length: int = _DEFAULT_STUB_LENGTH) -> str:
    """Get a stub version of input for logging."""
    return text[:stub_length] + "..." if len(text) > stub_length else text
