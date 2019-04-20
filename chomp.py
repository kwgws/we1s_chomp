# -*- coding:utf-8 -*-
"""
"""

import bleach
from bs4 import BeautifulSoup
import html
import regex as re
import string
from unidecode import unidecode

from browser import Browser
import config
import data
from datetime import datetime
import google
import wordpress


def update_wp_uris():
    """
    """

    sites = data.load_sites()
    with Browser() as browser:
        for site in sites:
            site = wordpress.get_uri(site, browser)
    sites = data.save_sites(sites)
    return sites


def chomp_wordpress():
    """
    """

    queries = data.load_queries()
    results = []

    with Browser() as browser:
        for query in queries:
            if query['count'] != '' or query['site']['wordpressUri'] == '':
                continue
            articles = list(wordpress.yield_articles(query, browser))
            query['count'] = len(articles)
            results += articles

    data.save_queries(queries)
    return results


def clean_articles():
    """
    """

    articles = data.load_articles()

    for article in articles:

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
        content = content.replace(' .', '.') # ??

        article['content'] = content
        article['length'] = len(content.split(' '))

    data.save_articles(articles)
        
