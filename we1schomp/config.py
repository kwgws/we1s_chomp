# -*- coding: utf-8 -*-
"""
"""

import os
from configparser import SafeConfigParser


def from_ini(filename):
    """
    """

    print(f'Loading settings from {filename}.')

    parser = SafeConfigParser()

    # TODO: Use default settings if file not found.
    if not parser.read(filename):
        raise FileNotFoundError(filename)

    # Fix common input errors.
    if parser['DEFAULT']['sleep_max'] < parser['DEFAULT']['sleep_min']:
        parser['DEFAULT']['sleep_max'] = parser['DEFAULT']['sleep_min']

    config = {
        'OUTPUT_FILENAME': parser['DEFAULT']['output_filename'],
        'OUTPUT_PATH': parser['DEFAULT']['output_path'],
        'WAIT_FOR_KEYPRESS': parser['DEFAULT'].getboolean('wait_for_keypress'),
        'SLEEP_MIN': parser['DEFAULT'].getfloat('sleep_min'),
        'SLEEP_MAX': parser['DEFAULT'].getfloat('sleep_max')
    }

    if not os.path.exists(config['OUTPUT_PATH']):
        os.makedirs(config['OUTPUT_PATH'])

    ###

    print(f'Loading sites from {filename}.')
    sites = []

    for section in parser.sections():

        print(f"> {parser[section]['name']}...", end='')

        if parser[section].getboolean('skip'):
            print('Skipping.')
            continue

        # Fix common input errors.
        url = parser[section]['url']
        url = url.replace('http://', '').replace('https://', '')

        # Update base filename for each site.
        filename = parser[section]['output_filename'].format(
            site=section,
            index='{index}', term='{term}', timestamp='{timestamp}')
        filename = os.path.join(parser[section]['output_path'], filename)

        sites.append({
            'name': parser[section]['name'],
            'url': url,
            'terms': parser[section]['terms'].strip(',').split(','),
            'urls_only': parser[section].getboolean('urls_only'),
            'short_name': section,
            'query_string': parser[section]['search_url'],
            'url_stops': parser[section]['url_stops'].strip(',').split(','),
            'content_tag': parser[section]['content_tag'],
            'length_min': parser[section].getint('length_min')
        })

        print('Ok!')

    return config, sites
