# -*- coding: utf-8 -*-
"""
"""

import random
import time
from gettext import gettext as _
from logging import getLogger
from urllib.error import HTTPError
from urllib.request import urlopen
from uuid import uuid4

from bs4 import BeautifulSoup

from we1schomp import data


def get_urls(site, config, browser):
    """
    """

    log = getLogger(__name__)

    if not site['google_enable']:
        log.warning(_('Google disabled for %s.'), site['name'])
        return []

    for term in site['terms']:

        log.info(
            _('Starting Google search for "%s" at %s.'), term, site['name'])

        # Start the query.
        browser.go(config['GOOGLE_QUERY_URL'].format(
            site=site['url'], term=term))

        # Start the page loop. Each page has multiple results, so we'll have
        # a lot of nested loops here.
        while True:

            browser.captcha_check()

            soup = BeautifulSoup(browser.source, 'html5lib')
            for rc in soup.find_all('div', {'class': 'rc'}):

                link = rc.find('a')
                url = str(link.get('href')).lower()

                # Drop results that include stop words.
                stop_flag = False
                for stop in site['google_stopwords']:
                    if stop in url:
                        log.warning(
                            _('Skipping (stopword "%s"): %s'), stop, url)
                        stop_flag = True
                        break
                if stop_flag:
                    continue

                # Sometimes the link's URL gets mushed in with the text.
                title = data.clean_string(str(link.text).split('http')[0])

                # Parse date from result. This is much more consistant than
                # doing it from the articles themselves, but it can be a little
                # spotty. TODO: Refactor this to catch relative dates.
                try:
                    date = str(rc.find('span', {'class': 'f'}).text)
                    date = date.replace(' - ', '')
                    log.info(_('Ok: %s'), url)
                except AttributeError:
                    date = 'N.D.'
                    log.warning(_('Ok (no date): %s'), url)
                
                article = {
                    'doc_id': str(uuid4()),
                    'attachment_id': '',
                    'namespace': config['NAMESPACE'],
                    'name': config['DB_NAME'].format(
                        site=site['short_name'],
                        term=data.slugify(term),
                        slug=data.slugify(title)),
                    'metapath': config['METAPATH'].format(
                        site=site['short_name']),
                    'pub': site['name'],
                    'pub_short': site['short_name'],
                    'title': title,
                    'url': url,
                    'content': '',
                    'length': '',
                    'search_term': term
                }
                yield article

            browser.sleep()
            if browser.click_on_id('pnnext'):
                log.info(_('Going to next page.'))
            else:
                log.info(_('No more result pages.'))
                break

    log.info(_('Google search complete.'))


def get_content(site, config, browser):
    """
    """

    log = getLogger(__name__)

    # Get all the articles associated with this site.
    articles = [a for a in data.load_articles(config['OUTPUT_PATH'])
                if a['pub_short'] == site['short_name']]
    if articles == []:
        log.warning(_('No articles found for %s.'), site['name'])
    else:
        log.info(_('Beginning scrape of %s.'), site['name'])

    for article in articles:

        # Drop results that include stop words.
        stop_flag = False
        for stop in site['google_stopwords']:
            if stop in article['url'].lower():
                log.warning(
                    _('Skipping (stopword "%s"): %s'), stop, article['url'])
                stop_flag = True
                break
        if stop_flag:
            continue
        
        browser.sleep()

        try:
            with urlopen(article['url']) as result:
                soup = BeautifulSoup(result.read(), 'html5lib')
        except HTTPError:
            browser.go(article['url'])
            soup = BeautifulSoup(browser.source, 'html5lib')
        
        # Start by getting rid of JavaScript--Bleach will "neuter" this but
        # has trouble removing it.
        try:
            soup.script.extract()
        except AttributeError:
            log.debug(_('No <script> tags found.'))

        # Now focus in on the content. We can't guarantee they've used the
        # <article> tag, but it's a safe bet they won't put an article in the
        # <header> or <footer>.
        try:
            soup.header.extract()
            soup.footer.extract()
        except AttributeError:
            log.debug(_('No <header>/<footer> tags found.'))

        # Finally, take all the content tags, default <p>, and mush together
        # any that are over a certain length of characters. This can be very
        # imprecise, but it seems to work for the most part. If we're getting
        # particularly bad content for a site, we can tweak the config and
        # try again or switch to a more advanced web-scraping tool.
        content = ''
        for tag in soup.find_all(site['content_tag']):
            if len(tag.text) > site['content_length_min']:
                content += ' ' + tag.text
        content = data.clean_string(content)

        article.update({
            'content': content,
            'length': f"{len(content.split(' '))} words"
        })
        yield article

    log.info(_('Scrape complete.'))
