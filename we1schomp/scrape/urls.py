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

    log.info(_('log urls scrape start'))
    for article in articles:

        # We need to associate this article with a site to get the appropriate
        # settings for it.
        site = next(s for s in sites 
                    if s['short_name'] == article['pub_short'])
        
        log.info(_('log urls query %s %s'), article['url'], site['name'])
        browser.sleep()
        browser.go(article['url'])
        soup = BeautifulSoup(browser.source, 'html5lib')
        
        # Start by getting rid of JavaScript--Bleach will "neuter" this but
        # has trouble removing it.
        soup.script.extract()

        # Now focus in on the content. We can't guarantee they've used the
        # <article> tag, but it's a safe bet they won't put an article in the
        # <header> or <footer>.
        soup.header.extract()
        soup.footer.extract()

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

        article = data.update_article(
            site=site, term=article['search_term'], title=article['title'],
            name=article['name'], url=article['url'],
            content=content, articles=articles, config=config)
        yield article

    log.info(_('log urls scrape done'))
