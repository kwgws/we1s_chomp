# -*- coding:utf-8 -*-
"""
"""

import config
import data


def yield_articles(site, term, browser):
    """
    """

    print(f'Using Google to Chomp {site["title"]}')

    g_uri = config.GOOGLE_URI.format(cx=config.GOOGLE_CX, key=config.GOOGLE_KEY)
    page = 1
    while True:
        query = g_uri + config.GOOGLE_URI_QUERY.format(term=term, url=site['url'], page=(page*10)-9)
        response = browser.get_json(query)

        for article in response['items']:
            print(f'Chomping article at {article["link"]}')
            yield data.create_article(
                name='temp',
                title=article['title'],
                url=article['link'],
                date=article['snippet'].split(' ... ')[0],
                pub=site['title'],
                pub_short=site['name']
            )

        if not 'nextPage' in response['queries']:
            break
        browser.sleep()
