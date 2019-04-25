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


def yield_articles(query, db, browser):
    log = getLogger(__name__)

    log.info(_('Chomping "%s" at %s.'), query['term'], query['site']['title'])
    g_uri = config.GOOGLE_URI.format(cx=config.GOOGLE_CX, key=config.GOOGLE_KEY)

    page = 1
    while True:
        query_uri = g_uri + config.GOOGLE_URI_QUERY.format(
            term=query['term'],
            url=query['site']['url'],
            page=(page * 10) - 9
        )
        response = browser.get_json(query_uri)

        # Something happend--probably ran out of content.
        if 'items' not in response:
            break

        for article in response['items']:
            date = dateparser.parse(article['snippet'].split(' ... ')[0])
            if date is None or date < query['startDate'] or date > query['endDate']:
                log.info(_('...skipping %s, out of date range.'), article['link'])
                continue

            # Get content from link.
            browser.new_tab()
            content = browser.get_html(article['link'])
            browser.close_tab()
            match = True
            if query['term'] not in content:
                match = False

            log.info(_('...collecting %s'), article['link'])
            query['count'] += 1
            query['chompDate'] = datetime.now()
            yield {
                'query': query,
                'title': article['title'],
                'url': article['link'],
                'date': date,
                'content_raw': content,
                'is_match': match
            }

        if 'nextPage' not in response['queries']:
            break
        page += 1


def chomp(db, browser):
    log = getLogger(__name__)

    log.info(_('Starting Google Chomp...'))
    count = 0
    for query in db.queries:
        for article in yield_articles(query, db, browser):
            db.create_article(**article)
        db.save_queries()
        count += 1
    log.info(_('Done! Finished %i queries.'), count)
