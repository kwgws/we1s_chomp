# -*- coding: utf-8 -*-
"""
"""

import time
from argparse import ArgumentParser
from gettext import gettext as _

import we1schomp
from we1schomp import settings


def run():
    """
    """

    # Parse command-line arguments
    parser = ArgumentParser(description=_('arg help app description'))

    parser.add_argument('--settings-file', type=str, 
                        help=_('arg help settings file'),
                        default='settings.ini')
    parser.add_argument('--urls-only', action='store_true',
                        help=_('arg help urls only'))
    parser.add_argument('--articles-only', action='store_true',
                        help=_('arg help articles only'))

    args = parser.parse_args()

    # Start the app
    print(_('hello'))
    time.sleep(2.0)

    config, sites = settings.from_ini(args.settings_file)
    we1schomp.scrape_all(config=config, sites=sites)

    print(_('goodbye'))
