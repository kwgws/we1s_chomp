# -*- coding: utf-8 -*-

"""Generic internal utility & helper functions for various parts of Chomp.
"""

from datetime import datetime
from logging import getLogger
from typing import Callable, Optional, Tuple

import dateparser

from we1s_chomp.browser import Browser, get


################################################################################
# Internal configuration parameters.                                           #
################################################################################


DEFAULT_STUB_LENGTH = 75
"""Number of characters to limit a stub to."""

STRFTIME = "%Y-%m-%d"
"""Datetime to string formatter."""


################################################################################
# Functions.                                                                   #
################################################################################


def get_interface(browser: Optional[Browser] = None) -> Callable:
    """Switch collector interface."""
    if browser is not None and isinstance(browser, Browser):
        return browser.get
    return get


def get_stub(text: str, stub_length: int = DEFAULT_STUB_LENGTH) -> str:
    """Get a stub version of input for logging."""
    return text[:stub_length] + "..." if len(text) > stub_length else text


def is_url_ok(
    url: str, url_stops: Set[str] = {}, url_stop_words: Set[str] = {}
) -> bool:
    """Check URL against stop lists."""
    return not (
        url in url_stops or next([s for s in url_stop_words if s in url], False)
    )


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
        log.debug("Out of date range: %s." % date.strftime(STRFTIME))
        return None

    return date
