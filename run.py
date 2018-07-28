# -*- coding: utf-8 -*-
"""
"""

from argparse import ArgumentParser
from gettext import gettext as _
from time import sleep

from we1schomp import config, data, query, scrape
from we1schomp.browser import Browser


def main():
    """
    """

    print(_('we1schomp_hello'))
    sleep(2.0)

    args = get_arguments()

    settings, sites = config.from_ini(args.settings_file)
    browser = Browser('Chrome', settings)
    articles = []

    # Part 1: URL scraping (from Google). Disable with --articles-only.
    if not args.articles_only:
        urls = query.find_urls(sites=sites, settings=settings, browser=browser)
        for article in urls:
            data.save_article_to_json(article=article, settings=settings)
            articles.append(article)

    # Part 2: Article scraping. Disable with --urls-only.
    if not args.urls_only:
        if not articles:
            queries = data.load_articles_from_json(settings['OUTPUT_PATH'])
        articles = scrape.find_content(articles=queries, browser=browser)
        for article in articles:
            data.save_article_to_json(article=article, settings=settings)

    browser.close()
    print(_('we1schomp_goodbye'))


def get_arguments():
    """
    """

    parser = ArgumentParser(description=_('we1schomp_description'))

    parser.add_argument('--settings-file', type=str, 
                        help=_('we1schomp_arg_settings_file'),
                        default='settings.ini')
    parser.add_argument('--urls-only', action='store_true',
                        help=_('we1schomp_arg_urls_only'))
    parser.add_argument('--articles-only', action='store_true',
                        help=_('we1schomp_arg_articles_only'))

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
