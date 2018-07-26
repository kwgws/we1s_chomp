# -*- coding: utf-8 -*-
"""
"""

from bs4 import BeautifulSoup
from we1schomp import data


def query(sites, settings, browser):
    """
    """

    count = 0
    for site in sites:
        count += len(site['terms'])
    print(f'Running {count} queries from {len(sites)} sites...')

    articles = []
    for site in sites:
        for term in site['terms']:
            article_data = _scrape_from_google(
                site=site,
                term=term,
                browser=browser
            )
            for article in article_data:
                articles.append(article)
                data.save_to_json(article, settings)

    return articles


def _scrape_from_google(site, term, browser):
    """
    """

    query_string = site['query_string'].format(url=site['url'], term=term)
    print(f'Starting query: {query_string}')

    browser.go(query_string)

    articles = []
    while True:

        browser.sleep()
        print(f'> {browser.current_url}')

        browser.captcha_check()
        soup = BeautifulSoup(browser.source, 'html5lib')
        for rc in soup.find_all('div', {'class': 'rc'}):

            link = rc.find('a')
            href = str(link.get('href'))

            # Drop results that include stop words. (Is there an easier way to
            # do this?)
            stop_flag = False
            for stop in site['url_stops']:
                if stop in href:
                    stop_flag = True
                    break
            if stop_flag:
                continue

            # Sometimes the link's URL gets mushed in with the text. (Why?)
            title = str(link.text).split('http')[0]

            # Parse date from result. This is much more consistant than doing
            # it from the articles themselves, but it can be a little spotty.
            # TODO: Refactor this to catch relative dates: "Yesterday," etc.
            try:
                date = str(rc.find('span', {'class': 'f'}).text)
                date = date.replace(' - ', '')
            except AttributeError:
                date = 'N.D.'

            article = {
                'pub': site['name'],
                'pub_short': site['short_name'],
                'pub_url': site['url'],
                'pub_date': date,
                'title': title,
                'url': href,
                'content': '',
                'length': '',
                'search_term': term
            }
            articles.append(article)

        if not browser.click_on_id('pnnext'):
            break

    return articles
