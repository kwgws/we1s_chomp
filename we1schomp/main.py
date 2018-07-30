# -*- coding: utf-8 -*-
"""
"""

from gettext import gettext as _
from logging import getLogger

from we1schomp import data
from we1schomp.browser import Browser
from we1schomp.scrape import google, urls, wordpress


def scrape_all(config, sites, articles=None, browser=None):
    """
    """

    log = getLogger(__name__)

    # Add everything up before we get going.
    count = 0
    for site in sites:
        count += len(site['terms'])
    log.info(_('log scrape all start %d %d'), count, len(sites))
    
    # Load previous articles.
    if not articles:
        articles = data.load_article_list_from_json(
            config['OUTPUT_PATH'], no_skip=True)

    # Start a browser if we don't already have one.
    browser = Browser('Chrome', settings=config)

    # Pass WordPress articles to the WordPress scraper.
    if config['WORDPRESS_ENABLE_SCRAPE']:
        for article in wordpress.get_articles(
                sites=sites, browser=browser,
                config=config, articles=articles):
            data.save_article_to_json(article, config)
    
    # Otherwise get metadata from Google...
    if config['GOOGLE_ENABLE_SCRAPE']:
        for article in google.get_articles(
                sites=sites, browser=browser,
                config=config, articles=articles):
            data.save_article_to_json(article, config)

    # ...and then parse the content directly.
    if config['DIRECT_ENABLE_SCRAPE']:
        for article in urls.get_articles(
                sites=sites, browser=browser,
                config=config, articles=articles):
            data.save_article_to_json(article, config)

    log.info(_('log scrape all done'))
    browser.close()
    return articles
