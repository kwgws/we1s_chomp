#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Scraping tools.
"""

from logging import getLogger
from typing import List, Dict

from we1s_chomp.browser import Browser


def get_responses(
    browser: Browser,
    query: str,
    url: str,
    google_cx: str = None,
    google_key: str = None,
    allow_wordpress_search: bool = True,
) -> List[Dict]:
    """Collect search responses from query and url.

    We can force WordPress by setting Google CX and key to None. N.b. at least
    one option must be available for the function to return anything!

    Args:
        - browser: Browser class initialized with configuration information.
        - query: Query term.
        - url: URL to search at.
        - google_cx: Google CSE API ID.
        - google_key: Google CSE API key.
        - allow_wordpress_search: Use the WordPress API, if available.
    
    Returns:
        List of dicts with URLs, terms, and raw text results. 
    """
    log = getLogger(__name__)

