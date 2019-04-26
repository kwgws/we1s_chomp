WE1S Chomp, by Sean Gilleran and WhatEvery1Says
---------------------------------------------

- http://we1s.ucsb.edu
- http://github.com/seangilleran/we1schomp

Chomp is a digital humanities web scraper designed to work at scale. It is
capable of collecting thousands or tens of thousands of articles without
relying on site-specific settings by making strategic assumptions about how
content is arranged within HTML documents.

See config.py for configuration details. Make sure query and source csv files
are in place before running.

**NB1:** Set up for Windows; will require some tweaking to work on Mac.

**NB2:** Before doing a Google Chomp, you need to load the following variables
into memory:
1. CHOMP_GOOGLE_CX - Custom search engine ID.
2. CHOMP_GOOGLE_KEY - Custom search engine API key.
