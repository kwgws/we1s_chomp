# -*- coding: utf-8 -*-
"""
we1schomp/actions.py
Scraping utility interfaces.

WE1SCHOMP ©2018-19, licensed under MIT.
A Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says.
http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
import html
import json
import string
from contextlib import suppress
from logging import getLogger
import regex as re
from typing import List
from uuid import uuid4

import bleach
from bs4 import BeautifulSoup
from sqlalchemy import orm
from unidecode import unidecode

from we1schomp.browser import Browser
from we1schomp.data import Article, Query, Response
from we1schomp.platforms import google, wordpress


def get_responses(session: orm.Session, cx: str, key: str, browser: Browser) -> None:
    """Collect response content from query."""

    log = getLogger(__name__)

    for i, query in enumerate(session.query(Query).filter_by(enabled=True)):

        print(
            f'Getting responses for "{query.term}" at {query.source_name}'
            # f' for {query.start_date.strftime("%Y-%m-%d")}'
            # f' to {query.end_date.strftime("%Y-%m-%d")}'
        )

        # Assemble URL and name stops.
        index = 0
        name_stops = set()
        url_stops = set()
        for response in session.query(Response).filter_by(query_id=query.query_id):
            name_stops.add(response.name)
            url_stops.add(response.url)

        # Choose a metadata handler.
        if wordpress.is_wp_uri(query.source.wordpress_uri):
            data = wordpress.get_responses(
                query.source.wordpress_uri, query.term, browser, url_stops
            )
        else:
            data = google.get_responses(
                query.source.url, query.term, cx, key, browser, url_stops
            )

        # Save the response along with appropriate metadata.
        for url, result in data:

            name = "_".join(
                [
                    "chomp-response",
                    query.source_name,
                    query.term,
                    query.start_date.strftime("%Y-%m-%d"),
                    query.end_date.strftime("%Y-%m-%d"),
                ]
            )
            while f"{name}_{index}" in name_stops:
                index += 1
            name = f"{name}_{index}"
            name_stops.add(name)

            response = Response(query=query, name=name, url=url, content_raw=result)
            session.add(response)
            session.commit()
            log.info("Saved response: %s" % response.name)


def get_articles(session: orm.Session, browser: Browser) -> None:
    """Collect raw article content from responses."""

    log = getLogger(__name__)

    for i, query in enumerate(session.query(Query).filter_by(enabled=True)):

        print(
            f'Getting articles for "{query.term}" at {query.source_name}'
            # f' for {query.start_date.strftime("%Y-%m-%d")}'
            # f' to {query.end_date.strftime("%Y-%m-%d")}'
        )

        # Assemble URL and name stops.
        name_stops = set()
        url_stops = set()
        for article in session.query(Article).filter_by(query_id=query.query_id):
            name_stops.add(article.name)
            url_stops.add(article.url)

        count = 0
        skipped = 0
        for response in session.query(Response).filter_by(query_id=query.query_id):

            # Some results are stored as a list, some as a dict.
            items = json.loads(response.content_raw)
            if not isinstance(items, list):
                items = items["items"]

            print("Collecting...", end="\r", flush=True)
            for item in items:

                # Choose a metadata handler.
                if wordpress.is_wp_uri(query.source.wordpress_uri):
                    item = wordpress.parse_metadata(item)
                else:
                    item = google.parse_metadata(item)

                # If None, that usually means no date or out of date range.
                if not item or item["url"] in url_stops:
                    skipped += 1
                    print(
                        f"Collecting...{count} ({skipped} skipped)",
                        end="\r",
                        flush=True,
                    )
                    continue

                # Scrape content if necessary.
                if not item.get("content_raw", None) or item["content_raw"] == "":
                    item["content_raw"] = browser.get(item["url"])

                # Check for no-match. Since this will affect the name, it's important to get
                # it out of the way as early as possible.
                no_match = query.term not in item["content_raw"]

                name = "_".join(
                    [
                        "chomp",
                        query.source_name,
                        query.term,
                        query.start_date.strftime("%Y-%m-%d"),
                        query.end_date.strftime("%Y-%m-%d"),
                    ]
                )
                if no_match:
                    name += "_no-exact-match"
                index = 0
                while f"{name}_{index}" in name_stops:
                    index += 1
                name = f"{name}_{index}"

                name_stops.add(name)
                url_stops.add(item["url"])
                query.article_count += 1

                session.add(
                    Article(
                        article_uuid=str(uuid4()),
                        name=name,
                        date=item["pub_date"],
                        title=item["title"],
                        url=item["url"],
                        content_raw=str(item["content_raw"]),
                        no_match=no_match,
                        query_id=query.query_id,
                        metapath=f"Corpus,{name},RawData",
                    )
                )
                session.commit()

                count += 1
                print(f"Collecting...{count} ({skipped} skipped)", end="\r", flush=True)
                log.info("Saved response: %s" % response.name)

        print(f"Collecting...{count} ({skipped} skipped) [\u001b[32mOK\u001b[0m]")


def clean_articles(
    session: orm.Session, tags: List[str], length: int = 75, ensure_ascii: bool = True
) -> None:
    """Process raw HTML content into plain text.

    This is the essential "meat" of Chomp and will probably require a lot of
    fine-tuning. Here's how it works:
    1. Trimp out any tags we don't need--script, nav, etc.
    2. Look for tags likely to contain important text content and save anything
       in those longer than a certain character length.
    3. Get rid of anything in there that isn't raw ASCII text (if specified).
    4. Repeat the process with each tag in the tag list until we get content.

    Args:
    - session: Database session.
    - tags: List of tag names to check for content. Will proceed down the list
      looking for content.
    - length: Length of tag content to save. Anything else is dumped.
    - ensure_ascii: Get rid of non-ASCII content.
    """
    log = getLogger(__name__)

    print("Cleaning articles")
    count = 0
    no_content = 0
    for article in session.query(Article):

        if "RawData" not in article.metapath:
            metapath = article.metapath.split(",")
            metapath[0] = "Corpus"
            metapath[1] = "RawData"
            article.metapath = ",".join(metapath)
            session.commit()
            log.info("Fixed metapath: %s" % article.name)

        if article.content != "":
            continue

        soup = BeautifulSoup(article.content_raw, "html5lib")

        with suppress(AttributeError):
            soup.script.extract()
            soup.nav.extract()
            soup.header.extract()
            soup.footer.extract()
            soup.img.extract()
            soup.caption.extract()

        # Take all the content tags, default <p>, and mush together the ones
        # that are over the specified length. This seems to work (mostly), but
        # if we're getting bad content for a site we should consider tweaking
        # the formula or using another extraction method.
        for tag_type in tags:

            content = ""
            for tag in [t for t in soup.find_all(tag_type) if len(t.text) > length]:
                content += f" {tag.text}"

            content = bleach.clean(content, tags=[], strip=True)
            content = html.unescape(content)  # get rid of &lt;, etc.

            if ensure_ascii:
                content = unidecode(content)

                # This looks for:
                # - URL strings, common in blog posts, etc., and not useful.
                # - Irregular punctuation, i.e. punctuation left over from
                #   Markdown, bb-code, HTML, or any symbols Bleach misses.
                regex_string = r"http(.*?)\s|[^a-zA-Z0-9\s\.\,\!\"\'\-\:\;\p{Sc}]"
                content = re.sub(re.compile(regex_string, 0), "", content)

            # Final cleanup.
            content = "".join([x for x in content if x in string.printable])
            content = " ".join(content.split())
            content = content.replace(" .", ".")  # ??

            if content != "":
                article.content = content
                session.commit()
                count += 1
                print(
                    f"Cleaning...{count} ({no_content} with no content)",
                    end="\r",
                    flush=True,
                )
                log.info("Cleaned article using <%s>: %s" % (tag_type, article.name))
                break

        if content == "":
            no_content += 1
            print(
                f"Cleaning...{count} ({no_content} with no content)",
                end="\r",
                flush=True,
            )
            log.warning("No content found in article: %s" % article.name)

    print(f"Cleaning...{count} ({no_content} with no content) [\u001b[32mOK\u001b[0m]")
