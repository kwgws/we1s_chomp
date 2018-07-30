# -*- coding: utf-8 -*-
"""
"""

import json
from gettext import gettext as _
from logging import getLogger
from urllib.request import urlopen

from we1schomp import data


def get_articles(sites, config, browser, articles=None):
    """
    """

    log = getLogger(__name__)
    if not articles:
        articles = data.load_article_list_from_json(config['OUTPUT_PATH'])

    log.info(_('log wordpress scrape start'))
    for site in sites:

        # Test if url is a WordPress site.
        log.debug(_('log wordpress api test start'))
        if (not site['wordpress_enable_pages'] 
                and not site['wordpress_enable_posts']):
            log.info(_('log wordpress scrape disabled %s'), site['name'])

        wp_url = site['url'].strip('/') + config['WORDPRESS_API_URL']
        with urlopen(wp_url) as result:
            result = json.loads(result.read())
        if result['namespace'] != 'wp/v2':
            log.warning(_('log wordpress no api %s'), site['name'])
            continue
        
        # Perform the API query.
        log.debug(_('log wordpress query start %s'), site['name'])
        scrape_results = []
        for term in site['terms']:

            if site['enable_wordpress_pages']:
                browser.sleep()
                wp_query = config['WORDPRESS_PAGES_QUERY_URL'].format(
                    api_url=wp_url, terms='+'.join(term.split(' ')))
                browser.go(wp_query)
                scrape_results += json.loads(browser.source), term

            if site['enable_wordpress_posts']:
                browser.sleep()
                wp_query = config['WORDPRESS_POSTS_QUERY_URL'].format(
                    api_url=wp_url, terms='+'.join(term.split(' ')))
                browser.go(wp_query)
                scrape_results += json.loads(browser.source), term
        
        if scrape_results == []:
            log.warning(_('log wordpress no results %s'), site['name'])
            continue

        # Save our results.
        for json_data, term in scrape_results:
            article = data.update_article(
                site=site, term=term, title=json_data['title']['rendered'],
                name=json_data['slug'], url=json_data['link'],
                content=json_data['content'],
                articles=articles, config=config)
            yield article

    log.info(_('log wordpress scrape done'))
