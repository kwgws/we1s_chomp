# -*- coding:utf-8 -*-
""" WE1S Chomp, by Sean Gilleran and WhatEvery1Says

http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp

Chomp is a digital humanities web scraper designed to work at scale. It is
capable of collecting thousands or tens of thousands of articles without
relying on site-specific settings by making strategic assumptions about how
content is arranged within HTML documents.

See config.py for configuration details.
"""

from gettext import gettext as _
import html
import logging
import string

import bleach
from bs4 import BeautifulSoup
import regex as re
from unidecode import unidecode

from browser import Browser
import config
from data import Data
import google
import wordpress


def full_run():
    """Do a full run-through of Chomp."""

    db = Data()
    with Browser() as browser:
        wordpress.chomp(db, browser)
        google.chomp(db, browser)
    clean_articles(db)


def clean_articles(db):
    """ Process raw HTML content into plain text.

    This is the essential "meat" of Chomp and will probably require a lot of
    fine-tuning. Important parameters are stored in config.py. Here's how it
    works:
    1. Trim out any tags we absolutely don't need--stuff like script, nav, etc.
    2. Look for tags likely to contain actual text content and save anything
       in those longer than a certain character length.
    3. Get rid of anything that isn't raw ASCII text--escape codes, links, etc.

    Args:
        db (data.Data): Database singleton.
    """

    for article in db.articles:

        print('fixin ' + article['filename'])

        soup = BeautifulSoup(article['content_raw'], 'html5lib')

        # Start by getting rid of JavaScript--Bleach will "neuter" this but
        # has trouble removing it.
        try:
            soup.script.extract()
        except AttributeError:
            pass

        # Now focus in on the content. We can't guarantee they've used the
        # <article> tag, but it's a safe bet they won't put an article in the
        # <header> or <footer>.
        try:
            soup.header.extract()
        except AttributeError:
            pass
        try:
            soup.footer.extract()
        except AttributeError:
            pass

        # Finally, take all the content tags, default <p>, and mush together
        # any that are over a certain length of characters. This can be very
        # imprecise, but it seems to work for the most part. If we're getting
        # particularly bad content for a site, we can tweak the config and
        # try again or switch to a more advanced web-scraping tool.
        content = ''
        for tag_type in config.CONTENT_TAGS:
            for tag in soup.find_all(tag_type):
                if len(tag.text) > config.CONTENT_LENGTH:
                    content += ' ' + tag.text

        # Now that we've got what we want, let's start getting rid of HTML.
        content = bleach.clean(content, tags=[], strip=True)
        content = html.unescape(content)    # Get rid of &lt;, etc.

        # Ideally we shouldn't need this since all the content is being handled
        # "safely," but the LexisNexis import script does it, so we'll do it too
        # in case some other part of the process is expecting ASCII-only text.
        content = unidecode(content)

        # Regex processing. Experimental!
        # This looks for:
        # - URL strings, common in blog posts, etc., and probably not useful for
        #   topic modelling.
        # - Irregular punctuation, i.e. punctuation left over from formatting
        #   or HTML symbols that Bleach missed.
        regex_string = r'http(.*?)\s|[^a-zA-Z0-9\s\.\,\!\"\'\-\:\;\p{Sc}]'
        content = re.sub(re.compile(regex_string), ' ', content)

        # Final cleanup.
        content = ''.join([x for x in content if x in string.printable])
        content = ' '.join(content.split())
        content = content.replace(' .', '.')  # ??

        article['content'] = content
        article['length'] = len(content.split(' '))

    db.save_articles()


def start_log():
    log_file = logging.FileHandler(config.LOGFILE)
    log_file.setFormatter(logging.Formatter(config.LOGFILE_FORMAT))
    console_log = logging.StreamHandler()
    console_log.setFormatter(logging.Formatter(config.CONSOLE_FORMAT))
    log_level = getattr(logging, config.LOG_LEVEL.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(_('Invalid log level "%s".'), log_level)
    logging.basicConfig(level=log_level, handlers=[log_file, console_log])


if __name__ == '__main__':
    start_log()
    full_run()
