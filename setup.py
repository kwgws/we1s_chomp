#!/usr/bin/env python
# -*- coding: utf-8 -*-


###############################################################################
# Package metadata.                                                           #
###############################################################################


NAME = "we1s_chomp"
DESCRIPTION = "A digital humanities web scraper."
URL = "http://we1s.ucsb.edu"
EMAIL = "sgilleran@ucsb.edu"
AUTHOR = "Sean Gilleran & WhatEvery1Says"
REQUIRES_PYTHON = ">=3.7.0"
VERSION = "0.3.0"

REQUIRED = [
    "requests",
    "dateparser",
    "beautifulsoup4",
    "unidecode",
    "selenium",
    "html5lib",
]
