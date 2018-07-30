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
    parser = ArgumentParser(description=_(
        'A Digital Humanities Web Scraper by WhatEvery1Says (we1s.ucsb.edu).'))

    parser.add_argument('--settings-file', type=str, 
                        help=_('Specify the settings file to use.'),
                        default='settings.ini')
    parser.add_argument('--no-wordpress', action='store_true',
                        help=_('Do not use the WordPress scraper.'))
    parser.add_argument('--no-google-search', action='store_true',
                        help=_('Do not use the Google scraper. Articles '
                               'with empty content will still be collected.'))

    args = parser.parse_args()

    # Start the app
    print(_('\n\nWE1S Chomp --- A Digital Humanities Web Scraper'
            '\n2018 by the WhatEvery1Says Team <we1s.ucsb.edu>.'))
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
    print(_('\nQueue completed. Goodbye!\n\n'))
