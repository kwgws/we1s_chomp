#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Tools to process raw content.

Todo:
    - Merge with the tools in the preprocessor Document class.
"""

import html
import string
from contextlib import suppress
from logging import getLogger
from typing import List

import bleach
import regex as re
from bs4 import BeautifulSoup
from unidecode import unidecode


# Internal configuration parameters.

_DEFAULT_CONTENT_LENGTH = 75
"""Default length of tag content to save."""

_DEFAULT_CONTENT_TAGS = ["p", "div", "span"]
"""Default ordered list of tags to check for content."""

REGEX_HTML_CLEAN = re.compile(r"http(.*?)\s|[^a-zA-Z0-9\s\.\,\!\"\'\-\:\;\p{Sc}]")
"""Regex string to remove unnecessary characters."""


# Function to "clean" an HTML document.
def clean_html(
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

    # Keep a stub version of the input for logging.
    stub = html_input[:75] + "..." if len(html_input) > 75 else html_input

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

        # Convert to UTF-8.
        content = unidecode(content)

        # Get rid of HTML tags.
        content = bleach.clean(content, tags=[], strip=True)

        # Get rid of &lt;, etc.
        content = html.unescape(content)

        # Get rid of URL strings (common in blog posts, etc.), irregular
        # punctuation, unescaped Markdown, bb-code, etc.
        content = re.sub(REGEX_HTML_CLEAN, "", content)

        # Get rid of non-printable characters (LF, CR, etc.)
        content = "".join([c for c in content if c in string.printable])

        # Final cleanup.
        content = " ".join(content.split())
        content = content.replace(" .", ".")  # ??

        if content != "":
            log.debug("Successfully cleaned HTML string: %s" % stub)
            return content

    log.warning("No content found in HTML string: %s" % stub)
    return ""
