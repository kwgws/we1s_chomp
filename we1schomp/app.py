# -*- coding: utf-8 -*-
"""
"""

import time
from argparse import ArgumentParser
from gettext import gettext as _

from we1schomp import data, settings
from we1schomp.browser import Browser
from we1schomp.scrape import google, wordpress


def run():
    """
    """

    # Parse command-line arguments
    parser = ArgumentParser(description=_('arg help app description'))

    parser.add_argument('--settings-file', type=str, 
                        help=_('arg help settings file'),
                        default='settings.ini')
    parser.add_argument('--no-wordpress', action='store_true',
                        help=_('arg help no wordpress'))
    parser.add_argument('--no-google-search', action='store_true',
                        help=_('arg help no google'))

    args = parser.parse_args()

    # Start the app
    print(_('hello'))
    time.sleep(2.0)

    config, sites = settings.from_ini(args.settings_file)
    browser = Browser('Chrome', config)

    # Start scraping!
    for site in sites:

        # Do WordPress scrapes.
        if not args.no_wordpress and wordpress.check_for_api(site, config):
            for article in wordpress.get_articles(site, config):
                data.save_article(article, config)
        
        # Do Google scrapes.
        else:
            if not args.no_google_search:
                for article in google.get_urls(site, config, browser):
                    data.save_article(article, config)
            for article in google.get_content(site, config, browser):
                data.save_article(article, config)

    browser.close()
    print(_('goodbye'))
