#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Scraping tools for the Google CSE API.
"""

from logging import getLogger
from typing import Dict, List, Set, Tuple

from we1s_chomp.browser import Browser

_API_URL = "http://googleapis.com/customsearch/v1"


def get_responses(
    url: str,
    term: str,
    cx: str,
    key: str,
    url_stop_words: Set[str] = str(),
    browser: Browser = None,
) -> List[Dict]:
    pass
