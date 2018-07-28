# -*- coding: utf-8 -*-
"""
"""

import logging
from gettext import gettext as _
from uuid import uuid4

from bs4 import BeautifulSoup


def find_urls(sites, settings, browser):
    """
    """

    log = logging.getLogger(__name__)

    if not sites:
        count = 0
        for site in sites:
            count += len(site['terms'])
        log.info(_('we1schomp_log_queries_start_%d_%d'), count, len(sites))

    for site in sites:
        for term in site['terms']:
            yield find_urls_from_google(site, term, settings, browser)

    log.info(_('we1schomp_log_queries_done'))


def find_urls_from_google(site, term, settings, browser):
    """
    """

    log = logging.getLogger(__name__)

    log.info(_('we1schomp_log_query_start_%s_%s'), term, site['url'])
    query_string = site['query_string'].format(url=site['url'], term=term)
    browser.go(query_string)

    while True:

        browser.sleep()
        browser.captcha_check()

        soup = BeautifulSoup(browser.source, 'html5lib')
        for rc in soup.find_all('div', {'class': 'rc'}):

            link = rc.find('a')
            url = str(link.get('href'))

            # Drop results that include stop words.
            if [stop for stop in site['url_stops'] if stop in url] is not None:
                log.warning(_('we1schomp_log_query_skip_%s_%s'), url)
                continue                   

            # Create metadata.
            doc_id = uuid4()  # Use UUID4 library to get unique id.
            pub_short = site['short_name']

            # Sometimes the link's URL gets mushed in with the text. (Why?)
            title = str(link.text).split('http')[0]

            # Parse date from result. This is much more consistant than doing
            # it from the articles themselves, but it can be a little spotty.
            # TODO: Refactor this to catch relative dates: "Yesterday," etc.
            try:
                date = str(rc.find('span', {'class': 'f'}).text)
                date = date.replace(' - ', '')
                log.info(_('we1schomp_log_query_ok_%s'), url)
            except AttributeError:
                date = 'N.D.'
                log.warning(_('we1schomp_log_query_no_date_%s'), url)
            
            article = {
                'doc_id': doc_id,
                'attachment_id': '',
                'namespace': settings['NAMESPACE'],
                'name': site['db_name'].format(pub_short, doc_id),
                'metapatch': site['metapath'].format(pub_short),
                'pub': site['name'],
                'pub_short': site['short_name'],
                'pub_url': site['url'],
                'pub_date': date,
                'title': title,
                'url': url,
                'content': '',
                'length': '',
                'search_term': term
            }
            yield article
                
        if not browser.click_on_id('pnnext'):
            log.info(_('we1schomp_log_query_next_page_%s'))
            break
