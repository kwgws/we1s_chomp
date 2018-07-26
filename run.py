# -*- coding: utf-8 -*-
"""
"""

from argparse import ArgumentParser
import we1schomp
from we1schomp import config


def _main():
    """
    """

    print('\n\nWE1S Chomp, version Alpha 3')
    print('by the WhatEvery1Says Team <http://we1s.ucsb.edu>\n')

    parser = ArgumentParser()
    parser.add_argument(
        '--settings-file', type=str, metavar='S',
        help='Settings file to use (default: "./settings.ini")',
        default='settings.ini'
    )
    parser.add_argument(
        '--urls-only', action='store_true',
        help='Only scrape Google, do not scrape individual results.'
    )
    parser.add_argument(
        '--articles-only', action='store_true',
        help='Only scrape individual results, do not scrape Google.'
    )
    args = parser.parse_args()

    settings, sites = config.from_ini(args.settings_file)
    browser = we1schomp.Browser('Chrome', settings)
    if not args.articles_only:
        we1schomp.query(sites, settings, browser)
    if not args.urls_only:
        we1schomp.scrape(sites, settings, browser)
    browser.close()

    print('\nQueue finished. Have a nice day!\n\n')


if __name__ == '__main__':
    _main()
