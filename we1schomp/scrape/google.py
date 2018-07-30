# -*- coding: utf-8 -*-
"""
"""

from gettext import gettext as _
from logging import getLogger

from bs4 import BeautifulSoup

from we1schomp import data


def get_articles(sites, browser, config, articles=None):
    """
    """

    log = getLogger(__name__)
    if not articles:
        articles = data.load_article_list_from_json(config['OUTPUT_PATH'])

    log.info(_('log google start'))
    for site in sites:
        for term in site['terms']:

            log.info(_('log google query %s %s'), term, site['url'])
            g_query = config['GOOGLE_QUERY_URL'].format(
                site=site['url'], term=term)
            
            # Start the page loop. Each page has multiple results, so we'll
            # have a lot of nested loops here.
            browser.go(g_query)
            while True:

                browser.sleep()
                browser.captcha_check()

                soup = BeautifulSoup(browser.source, 'html5lib')
                for rc in soup.find_all('div', {'class': 'rc'}):

                    link = rc.find('a')
                    url = str(link.get('href'))

                    # Drop results that include stop words.
                    log.debug(_('log google stop start'))
                    try:
                        stop = next(s for s in site['google_stopwords']
                                    if s in url)
                        log.warning(_('log google stop skip %s %s'), url, stop)
                        continue
                    except StopIteration:
                        log.debug(_('log google stop ok'))                      
                    
                    # Sometimes the link's URL gets mushed in with the text.
                    title = str(link.text).split('http')[0]

                    # Parse date from result. This is much more consistant
                    # than doing it from the articles themselves, but it can
                    # be a little spotty.
                    # TODO: Refactor this to catch relative dates.
                    try:
                        date = str(rc.find('span', {'class': 'f'}).text)
                        date = date.replace(' - ', '')
                        log.info(_('log google query ok %s'), url)
                    except AttributeError:
                        date = 'N.D.'
                        log.warning(_('log google query no date %s'), url)
                    
                    article = data.update_article(
                        site=site, term=term, title=title,
                        name=data.slugify(title), url=url,
                        content='',
                        articles=articles, config=config,
                        overwrite=False)  # Google can only give us metadata.
                    yield article

                if not browser.click_on_id('pnnext'):
                    log.info(_('log google next page'))
                    break

    log.info(_('log google done'))
