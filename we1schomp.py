# -*- coding: utf-8 -*-
"""
"""

from argparse import ArgumentParser
from we1schomp import config, scrape


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument(
        '--settings_file', type=str, metavar='S',
        help='Settings file to use (default: "settings.ini").',
        default='settings.ini')
    parser.add_argument(
        '--urls_only', action='store_true',
        help='Only scrape Google, not individual results.')
    parser.add_argument(
        '--articles_only', action='store_true',
        help='Only get artiles, not Google results.')
    args = parser.parse_args()

    settings = config.load_from_file(args.settings_file)

    if args.urls_only and not args.articlesl_only:
        scrape.urls_from_google(settings)
        exit()

    if args.articles_only and not args.urls_only:
        scrape.content_from_sites(settings)
        exit()

    scrape.urls_from_google(settings)

    print('\n')

    scrape.content_from_sites(settings)
    exit()
