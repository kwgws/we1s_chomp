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


def chomp(db, browser):
    """ Chomp queries using Google.

    This will run all active queries in the CSV through Google and collect
    relevant results, which should save us some work in terms of finding titles,
    dates, etc. (Also, anything without a date will be skipped.)

    NB: The CSE API can be very weird and returns slightly less information than
    the "real" web search. Expect work-arounds!

    Args:
        db (Data): Database singleton.
        browser (Browser): Browser singleton.
    """
    log = getLogger(__name__)

    log.info(_('Starting Google Chomp...'))
    count = 0
    for query in db.queries:
        for article in yield_articles(query, db, browser):
            db.create_article(**article)
        db.save_queries()
        count += 1
    log.info(_('Done! Finished %i queries.'), count)


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
        if response is None or 'items' not in response:
            break

        for article in response['items']:

            # Google's CSE API puts the date in the "Snippet" preview, separated
            # by an elipsis.
            date = dateparser.parse(article['snippet'].split(' ... ')[0])
            if date is None or date < query['startDate'] or date > query['endDate']:
                log.info(_('...skipping %s, out of date range.'), article['link'])
                continue

            # Get content from link.
            browser.new_tab()
            content = browser.get_html(article['link'])
            browser.close_tab()

            # Check if term is actually in the article.
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

        # We have two page-checks here because sometimes the API gets upset (?)
        if 'nextPage' not in response['queries']:
            break
        page += 1
