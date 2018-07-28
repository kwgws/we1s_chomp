# -*- coding: utf-8 -*-
"""
"""

import html
import logging
from gettext import gettext as _

import bleach

import regex as re
from bs4 import BeautifulSoup
from we1schomp.data import clean_str, get_site_from_article


def find_content(articles, sites, browser):
    """
    """

    log = logging.getLogger(__name__)
    log.info(_('we1schomp_log_scrapes_start_%d'), len(articles))

    for article in articles:

        browser.sleep()

        site = get_site_from_article(article, sites)
        content, length = get_content_from_url(
            url=article['url'],
            content_tag=site['content_tag'],
            length_min=site['length_min'],
            browser=browser)
        article.update({'content': content, 'length': length})

        yield article
    
    log.info(_('we1schomp_log_scrapes_done'))


def get_content_from_url(url, content_tag, length_min, browser):
    """
    """

    log = logging.getLogger(__name__)

    log.debug(_('we1schomp_log_scrape_start_%s_%s'), content_tag, length_min)
    browser.go(url)
    soup = BeautifulSoup(browser.source, 'html5lib')

    content = str()
    for tag in soup.find_all(content_tag):
        if len(tag.text) > length_min:
            content += html.unescape(bleach.clean(tag.text)) + ' '
    content = clean_str(content)

    # Regex processing. Experimental!
    # This looks for:
    # - URL strings, common in blog posts, etc., and probably not useful for
    #   topic modelling.
    # - Irregular punctuation, i.e. punctuation left over from formatting
    #   or HTML symbols that Bleach missed.
    rex = re.compile(r'http(.*?)\s|[^a-zA-Z0-9\s\.\,\!\"\'\-\p{Sc}]')
    content = re.sub(rex, ' ', content)
    content = content.replace(' .', '.')  # Hmm.
    content = clean_str(content)

    length = f"{len(content.split(' '))} words"
    return content, length
