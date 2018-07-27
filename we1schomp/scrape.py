# -*- coding: utf-8 -*-
"""
"""

# import re
import logging
import bleach
from bs4 import BeautifulSoup
from we1schomp import data


def scrape(sites, settings, browser):
    """
    """

    log = logging.getLogger(__name__)

    queries = data.load_from_json(settings['OUTPUT_PATH'])
    log.info(f'Starting scrape, {len(queries)} URL(s) queued')

    for query in queries:

        browser.sleep()

        # Find the site configuration associated with the query.
        site = next(s for s in sites if s['short_name'] == query['article']['pub_short'])

        log.info(f"Scraping {query['article']['url']}")
        browser.go(query['article']['url'])
        soup = BeautifulSoup(browser.source, 'html5lib')

        content = []
        log.debug(f"Scraping <{site['content_tag']}> with {site['length_min']}+ chars")
        for tag in soup.find_all(site['content_tag']):
            if len(tag.text) > site['length_min']:
                content.append(tag.text)
        content = ' '.join(content)
        log.debug(f'Pre-clean: {content}')
        content = bleach.clean(content)
        log.debug(f'Post-clean: {content}')
        
        query['article']['content'] = content
        query['article']['length'] = f"{len(content.split(' '))} words"
        data.save_to_json(query['article'], settings, query['filename'])
    
    log.info(f'Scrapes complete')
    return [query['article'] for query in queries]
