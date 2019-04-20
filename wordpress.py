# -*- coding:utf-8 -*-
"""
"""

import dateparser

import config
import data


def get_uri(site, browser):
    """
    """

    uri = site['url'] + config.WORDPRESS_URI
    
    try:
        result = browser.get_json(uri)
        browser.sleep()
        if result['namespace'] != 'wp/v2':
            site['wordpressUri'] = ''
            return site
    except:
        site['wordpressUri'] = ''
        return site

    site['wordpressUri'] = uri
    return site


def yield_articles(query, browser):
    """
    """

    if query['site']['wordpressUri'] == '':
        return None
    
    print(f'Using WordPress API to Chomp {query["site"]["title"]}')

    wp_uri = query['site']['wordpressUri']
    for wp_query in config.WORDPRESS_URI_QUERIES:
        page = 1
        while True:
            query_uri = wp_uri + wp_query.format(term='+'.join(query['term'].split(' ')), page=page)
            response = browser.get_json(query_uri)
            if not isinstance(response, (list,)) or len(response) == 0:
                break
            for article in response:

                date = dateparser.parse(article['date'])
                if date < query['startDate'] or date > query['endDate']:
                    continue
                if query['term'] not in article['content']['rendered']:
                    continue

                print(f'Chomping article at {article["link"]}')
                yield data.create_article(
                    query=query,
                    title=article['title']['rendered'],
                    url=article['link'],
                    date=date,
                    content_raw=article['content']['rendered']
                )
            page += 1
            browser.sleep()
