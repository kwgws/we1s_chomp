# -*- coding: utf-8 -*-
"""
"""

# import re
import bleach
from bs4 import BeautifulSoup
from we1schomp import data


def scrape(sites, settings, browser):
    """
    """

    queries = data.load_from_json(settings['OUTPUT_PATH'])

    print(f'Starting scrape for {len(queries)} URLs.')

    for query in queries:

        browser.sleep()

        # Find the site configuration associated with the query.
        site = next(s for s in sites if s['short_name'] == query['article']['pub_short'])

        print(f"Scraping: {query['article']['url']}")
        browser.go(query['article']['url'])
        soup = BeautifulSoup(browser.source, 'html5lib')
        content = []
        for tag in soup.find_all(site['content_tag']):
            if len(tag.text) > site['length_min']:
                content.append(tag.text)
        content = ' '.join(content)
        content = bleach.clean(content)

        query['article']['content'] = content
        query['article']['length'] = len(content.split(' '))

        data.save_to_json(query['article'], settings, query['filename'])
    
    return [query['article'] for query in queries]
