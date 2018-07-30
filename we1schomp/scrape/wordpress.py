# -*- coding: utf-8 -*-
"""
"""

import json
import random
import time
from gettext import gettext as _
from logging import getLogger
from urllib.request import urlopen

from we1schomp import data


def get_articles(sites, config, articles=None):
    """
    """

    log = getLogger(__name__)
    if not articles:
        articles = data.load_article_list_from_json(config['OUTPUT_PATH'])

    log.info(_('log wordpress scrape start'))
    wp_sites = []
    for site in [s for s in sites if s['wordpress_enable']]:
        
        # Perform the API query.
        log.debug(_('log wordpress query start %s'), site['name'])
        scrape_results = []
        for term in site['terms']:

            json_results = []
            wp_url = ('http://' + site['url'].strip('/')
                      + config['WORDPRESS_API_URL'])

            # Check for WordPress API
            log.debug(_('log wordpress api test start'))
            if (not site['wordpress_enable_pages'] 
                    and not site['wordpress_enable_posts']):
                log.info(_('log wordpress scrape disabled %s'), site['name'])
                continue

            with urlopen(wp_url) as result:
                result = json.loads(result.read())
            if result['namespace'] != 'wp/v2':
                log.info(_('log wordpress no api %s'), site['name'])
                continue
            
            log.info(_('log wordpress api found %s'), site['name'])

            # Sleep for a bit, as a courtesy.
            sleep_time = random.uniform(
                config['SLEEP_MIN'], config['SLEEP_MAX'])
            log.info(_('log sleep %.2f'), sleep_time)
            time.sleep(sleep_time)

            if site['wordpress_enable_pages']:
                wp_query = config['WORDPRESS_PAGES_QUERY_URL'].format(
                    api_url=wp_url, terms='+'.join(term.split(' ')))
                log.info(_('log wordpress query page %s'), wp_query)
                with urlopen(wp_query) as result:
                    json_results += json.loads(result.read())

            # Sleep for a bit, as a courtesy.
            # TODO: Move this into a function
            sleep_time = random.uniform(
                config['SLEEP_MIN'], config['SLEEP_MAX'])
            log.info(_('log sleep %.2f'), sleep_time)
            time.sleep(sleep_time)

            if site['wordpress_enable_posts']:
                wp_query = config['WORDPRESS_POSTS_QUERY_URL'].format(
                    api_url=wp_url, terms='+'.join(term.split(' ')))
                log.info(_('log wordpress query post %s'), wp_query)
                with urlopen(wp_query) as result:
                    json_results += json.loads(result.read())
            
            for json_result in json_results:
                scrape_results.append((json_result, term))
        
        if scrape_results == []:
            log.warning(_('log wordpress no results %s'), site['name'])
            continue

        wp_sites.append(site)

        # Save our results.
        for json_data, term in scrape_results:
            article = data.update_article(
                site=site, term=term,
                title=json_data['title']['rendered'],
                name=json_data['slug'],
                url=json_data['link'],
                content=json_data['content']['rendered'],
                articles=articles, config=config)
            yield article
    
    # Remove WordPress sites from the queue.
    for site in wp_sites:
        log.info(_('log wordpress removed site %s'), site['name'])
        sites.remove(site)

    log.info(_('log wordpress scrape done'))
