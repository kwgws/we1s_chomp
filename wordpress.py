# -*- coding:utf-8 -*-
""" WE1S Chomp, by Sean Gilleran and WhatEvery1Says

http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""

from datetime import datetime
from gettext import gettext as _
from logging import getLogger

import dateparser

import config


def update_uris(db, browser):
    log = getLogger(__name__)

    log.info(_('Updating WordPress URIs...'))
    count = 0
    for site in db.sites:
        uri = site['url'] + config.WORDPRESS_URI
        log.debug(_('...trying %s...'), uri)
        try:
            result = browser.get_json(uri)
            if result['namespace'] != 'wp/v2':
                site['wordpressUri'] = ''
                log.debug(_('...not found.'))
                continue
        except:  # noqa: E722 (TODO: Be specific about exceptions here.)
            site['wordpressUri'] = ''
            log.debug(_('...not found.'))
            continue
        log.info(_('...WordPress URI found at %s.'), uri)
        site['wordpressUri'] = uri
        count += 1
    log.info(_('Done! Found %i URI(s).'), count)
    if count > 0:
        db.save_sites()


def yield_articles(query, db, browser):
    log = getLogger(__name__)

    if query['site']['wordpressUri'] == '':
        log.debug(_('No URI found for %s.'), query['site']['title'])
        return None

    log.info(_('Chomping "%s" at %s.'), query['term'], query['site']['title'])
    wp_uri = query['site']['wordpressUri']
    for wp_query in config.WORDPRESS_URI_QUERIES:

        page = 1
        while True:
            query_uri = wp_uri + wp_query.format(
                term='+'.join(query['term'].split(' ')),
                page=page
            )
            response = browser.get_json(query_uri)

            # No more pages or no content for query term.
            if not isinstance(response, (list,)) or len(response) == 0:
                break

            for article in response:
                date = dateparser.parse(article['date'])
                if date < query['startDate'] or date > query['endDate']:
                    log.info(_('...skipping %s, out of date range.'), article['link'])
                    continue
                if query['term'] not in article['content']['rendered']:
                    log.info(_('...skipping %s, does not contain term.'), article['link'])
                    continue

                log.info(_('...collecting %s'), article['link'])
                query['count'] += 1
                query['chompDate'] = datetime.now()
                yield {
                    'query': query,
                    'title': article['title']['rendered'],
                    'url': article['link'],
                    'date': date,
                    'content_raw': article['content']['rendered']
                }

            page += 1


def chomp(db, browser):
    log = getLogger(__name__)

    log.info(_('Starting WordPress Chomp...'))
    # update_uris(db, browser)
    count = 0
    for query in db.queries:
        for article in yield_articles(query, db, browser):
            db.create_article(**article)
        db.save_queries()
        count += 1
    log.info(_('Done! Finished %i queries.'), count)
