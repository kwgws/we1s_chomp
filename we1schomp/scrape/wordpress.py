# -*- coding: utf-8 -*-
"""
"""

import json
import random
import time
from gettext import gettext as _
from logging import getLogger
from urllib.request import urlopen
from uuid import uuid4

from we1schomp import data


def check_for_api(site, config):
    """
    """

    log = getLogger(__name__)
    wp_url = ('http://' + site['url'].strip('/')
              + config['WORDPRESS_API_URL'])

    # Check for internal settings.
    log.debug(_('log wordpress api test start'))
    if (not site['wordpress_enable'] or
            (not site['wordpress_enable_pages']
             and not site['wordpress_enable_posts'])):
        log.info(_('log wordpress scrape disabled %s'), site['name'])
        return False

    # Check for API access.
    with urlopen(wp_url) as result:
        result = json.loads(result.read())
    if result['namespace'] != 'wp/v2':
        log.info(_('log wordpress no api %s'), site['name'])
        return False
    
    log.info(_('log wordpress api found %s'), site['name'])
    return True


def get_articles(site, config):
    """
    """

    log = getLogger(__name__)

    # Perform the API query.
    log.debug(_('log wordpress query start %s'), site['name'])
    wp_url = ('http://' + site['url'].strip('/')
              + config['WORDPRESS_API_URL'])
    scrape_results = []

    for term in site['terms']:
        json_results = []

        # Sleep for a bit, as a courtesy.
        sleep_time = random.uniform(
            config['SLEEP_MIN'], config['SLEEP_MAX'])
        log.info(_('log sleep %.2f'), sleep_time)
        time.sleep(sleep_time)

        # Collect WordPress pages.
        if site['wordpress_enable_pages']:
            wp_query = config['WORDPRESS_PAGES_QUERY_URL'].format(
                api_url=wp_url, terms='+'.join(term.split(' ')))
            log.info(_('log wordpress query page %s'), wp_query)
            with urlopen(wp_query) as result:
                json_results += json.loads(result.read())
        else:
            log.info(_('log wordpress pages disabled %s'), site['name'])

        # TODO: Move this into a function
        sleep_time = random.uniform(
            config['SLEEP_MIN'], config['SLEEP_MAX'])
        log.info(_('log sleep %.2f'), sleep_time)
        time.sleep(sleep_time)

        # Collect WordPress posts.
        if site['wordpress_enable_posts']:
            wp_query = config['WORDPRESS_POSTS_QUERY_URL'].format(
                api_url=wp_url, terms='+'.join(term.split(' ')))
            log.info(_('log wordpress query post %s'), wp_query)
            with urlopen(wp_query) as result:
                json_results += json.loads(result.read())
        else:
            log.info(_('log wordpress posts disabled %s'), site['name'])
        
        for json_result in json_results:
            scrape_results.append((json_result, term))
    
    if scrape_results == []:
        log.warning(_('log wordpress no results %s'), site['name'])
        return scrape_results

    # Process the results.
    for json_result, term in scrape_results:
        content = data.clean_string(json_result['content']['rendered'])
        article = {
            'doc_id': str(uuid4()),
            'attachment_id': '',
            'namespace': config['NAMESPACE'],
            'name': config['DB_NAME'].format(
                site=site['short_name'],
                term=data.slugify(term),
                slug=json_result['slug']),
            'metapath': config['METAPATH'].format(site=site['short_name']),
            'pub': site['name'],
            'pub_short': site['short_name'],
            'title': json_result['title']['rendered'],
            'url': json_result['link'],
            'content': content,
            'length': f"{len(content.split(' '))} words",
            'search_term': term
        }
        yield article

    log.info(_('log wordpress site done %s'), site)
