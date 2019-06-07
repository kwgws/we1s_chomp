WE1S Chomp, by Sean Gilleran and WhatEvery1Says
===============================================

- http://we1s.ucsb.edu
- http://github.com/seangilleran/we1schomp

Chomp is a digital humanities web scraper designed to work at scale. It is
capable of collecting thousands or tens of thousands of articles without
relying on site-specific settings by making strategic assumptions about how
content is arranged within HTML documents.

**NB1** Before doing a Google Chomp, you need to load the following variables
into memory:
1. CHOMP_GOOGLE_CX - Custom search engine ID.
2. CHOMP_GOOGLE_KEY - Custom search engine API key.

Usage
----------------------------------------------

```
usage: chomp.py [-h] [-r] [-a] [-c] [--no-disable] [--tags TAG [TAG ...]]    
                [--length L] [--db DB_PATH] [--log LOG_PATH] [--min-wait MIN]
                [--max-wait MAX] [--lynx LYNX_PATH] [--chrome CHROME_PATH]   
                [--chrome-log CHROME_LOG_PATH] [--debug] [-iS SOURCE_IN_FILE]
                [-iQ QUERY_IN_FILE] [-iR RESPONSE_IN_PATH]
                [-iA ARTICLE_IN_PATH] [-dA ARTICLE_OUT_PATH]
                [-dR RESPONSE_OUT_PATH] [-dQ QUERY_OUT_FILE]
                [-dS SOURCE_OUT_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -r, --search          collect search results
  -a, --articles        collect articles
  -c, --clean           clean article content

configuration arguments:
  --no-disable          do not disable completed queries
  --tags TAG [TAG ...]  content tags to check (def: [p])
  --length L            content tag length to check (def: 75)
  --db DB_PATH          database path (def: ...\chomp.sqlite)
  --log LOG_PATH        logfile path (def: ...\chomp.log)
  --min-wait MIN        min browser wait time
  --max-wait MAX        max browser wait time
  --lynx LYNX_PATH      lynx path
  --chrome CHROME_PATH  chome driver path
  --chrome-log CHROME_LOG_PATH
                        chrome logfile path (def: ...\chrome.log)
  --debug               debug mode, extra logging

file input arguments:
  -iS SOURCE_IN_FILE, --import-sources SOURCE_IN_FILE
                        import sources from csv
  -iQ QUERY_IN_FILE, --import-queries QUERY_IN_FILE
                        import queries from csv
  -iR RESPONSE_IN_PATH, --import-responses RESPONSE_IN_PATH
                        import json responses
  -iA ARTICLE_IN_PATH, --import-articles ARTICLE_IN_PATH
                        import json articles

file output arguments:
  -dA ARTICLE_OUT_PATH, --dump-articles ARTICLE_OUT_PATH
                        export json articles
  -dR RESPONSE_OUT_PATH, --dump-responses RESPONSE_OUT_PATH
                        export json responses
  -dQ QUERY_OUT_FILE, --dump-queries QUERY_OUT_FILE
                        export queries to csv
  -dS SOURCE_OUT_FILE, --dump-sources SOURCE_OUT_FILE
                        export sources to csv
```
