#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Script example for using WE1S Chomp.
"""

import csv
import logging
import os
from concurrent import futures
from typing import Dict, List, Set, Tuple

from we1s_chomp import wordpress
from we1s_chomp.browser import Browser


###############################################################################
# Internal configuration parameters.                                          #
###############################################################################


BROWSER_URL = "http://harbor.english.ucsb.edu:4444/"
"""Selenium Grid hub URL."""

NUM_WORKERS = 3
"""Number of workers to use. This should reflect the # of Selenium Nodes."""

QUERIES_FILENAME = os.path.join(os.getcwd(), "queries.csv")
"""CSV file with queries."""

SOURCES_FILENAME = os.path.join(os.getcwd(), "sources.csv")
"""CSV file with sources."""

STOP_WORDS_FILENAME = os.path.join(os.getcwd(), "url_stop_words.txt")
"""URL stop words file."""


###############################################################################
# Program loop.                                                               #
###############################################################################


def run():
    start_logging("chomp.log")

    # Load sources & queries.
    sources = load_sources(SOURCES_FILENAME)
    queries = load_queries(QUERIES_FILENAME, sources)

    # Load stop words.
    url_stop_words = load_url_stop_words(STOP_WORDS_FILENAME)

    browser = Browser(BROWSER_URL)

    # Look for Wordpress sites and scrape those first.
    wp_sources, google_sources = filter_wp_sources(sources, browser)
    collect_wp_responses([q for q in queries if q["source"] in wp_sources], browser)


###############################################################################
# Wordpress functions.                                                        #
###############################################################################


def collect_wp_responses(
    queries: List[Dict], browser: Browser, output_path: str, num_workers: int = NUM_WORKERS
) -> List[Dict]:
    """Collect Wordpress sources."""
    responses = []

    print(
        f"Getting Wordpress responses for {len(queries)} queries with {num_workers} workers."
    )

    print(f"Chomping...", end="\r", flush=True)
    with futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_res = {
            executor.submit(
                wordpress.get_responses,
                term=query["term"],
                base_url=query["url"],
                browser_config=browser,
            ): query
            for query in queries
        }
        for future in futures.as_completed(future_to_res):
            query = future_to_res[future]
            response = future.result()


def filter_wp_sources(
    sources: List[Dict], browser: Browser, num_workers: int = NUM_WORKERS
) -> Tuple[List[Dict], List[Dict]]:
    """Filter sources into Wordpress & Non-Wordpress."""
    wp_sources = []
    google_sources = []
    found = 0
    checked = 0

    print(f"Looking for Wordpress sources with {num_workers} workers.")

    print(f"Checking...", end="\r", flush=True)
    with futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_source = {
            executor.submit(
                wordpress.is_api_available, url=source["url"], browser_config=browser
            ): source
            for source in sources
        }
        for future in futures.as_completed(future_to_source):
            source = future_to_source[future]
            is_wordpress = future.result()
            if is_wordpress:
                wp_sources.append(source)
                found += 1
                checked += 1
                print(
                    f"Scanning...{found} found, {checked} checked", end="\r", flush=True
                )
            else:
                google_sources.append(source)
                checked += 1
                print(
                    f"Scanning...{found} found, {checked} checked", end="\r", flush=True
                )

    print(f"Scanning...{found} found, {checked} checked [Done!]", end="\r", flush=True)
    return wp_sources, google_sources


###############################################################################
# Google functions.                                                           #
###############################################################################


pass


###############################################################################
# File handling functions.                                                    #
###############################################################################


def load_sources(filename: str) -> List[Dict]:
    """Load sources from CSV file."""
    log = logging.getLogger(__name__)
    print(f"Importing sources from {filename}.")

    i = 0
    sources = []
    print("Loading...", end="\r", flush=True)
    with open(filename, newline="", encoding="utf-8") as csvfile:

        for i, source in enumerate(csv.DictReader(csvfile)):
            sources.append(source)
            log.info('Loaded source "%s".' % source["name"])
            print(f"Loading...{i + 1}", end="\r", flush=True)

    print(f"Loading...{i + 1} [Done!]")
    return sources


def load_queries(filename: str, sources: List[Dict]) -> List[Dict]:
    """Load queries from a CSV file."""
    log = logging.getLogger(__name__)
    print(f"Importing queries from {filename}.")

    i = 0
    queries = []
    print("Loading...", end="\r", flush=True)
    with open(filename, newline="", encoding="utf-8") as csvfile:

        for i, query in enumerate(csv.DictReader(csvfile)):
            source = next(s for s in sources if s["name"] == query["source"])
            query["source"] = source
            log.info('Loaded query "%s" at "%s".' % (query["term"], source["name"]))
            print(f"Loading...{i + 1}", end="\r", flush=True)

    print(f"Loading...{i + 1} [Done!]")
    return queries


def load_url_stop_words(filename: str) -> Set[str]:
    "Load URL stop words from a txt file."
    log = logging.getLogger(__name__)
    print(f"Importing URL stop words from {filename}.")

    i = 0
    stop_words = set()
    print("Loading...", end="\r", flush=True)
    with open(filename, encoding="utf-8") as txtfile:

        for i, line in enumerate(txtfile.readlines()):
            stop_word = line.strip()
            stop_words.add(stop_word)
            log.info('Added URL stop word "%s".' % stop_word)
            print(f"Loading...{i + 1}", end="\r", flush=True)

    print(f"Loading...{i + 1} [Done!]")
    return stop_words


###############################################################################
# Helper functions.                                                           #
###############################################################################


def start_logging(path: str, debug: bool = False) -> None:
    """Start a simple logger."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(filename=path, level=log_level)


if __name__ == "__main__":
    run()
