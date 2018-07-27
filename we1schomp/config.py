# -*- coding: utf-8 -*-
"""
"""

import os
import logging
from configparser import SafeConfigParser


def from_ini(filename):
    """
    """

    parser = SafeConfigParser()
    if not parser.read(filename):  # TODO: Use default settings if file not found.
        raise FileNotFoundError(filename)

    log_file = logging.FileHandler(parser['DEFAULT']['log_file'])
    log_file.setFormatter(logging.Formatter(parser['DEFAULT']['log_file_format']))
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(parser['DEFAULT']['console_format']))
    logging.basicConfig(level=logging.INFO, handlers=[log_file, console])
    log = logging.getLogger(__name__)
    log.info(f'Using settings from {filename}')

    # Fix common input errors.
    if parser['DEFAULT']['sleep_max'] < parser['DEFAULT']['sleep_min']:
        log.warning(f'sleep_max < sleep_min, fixing')
        parser['DEFAULT']['sleep_max'] = parser['DEFAULT']['sleep_min']

    config = {
        'OUTPUT_FILENAME': parser['DEFAULT']['output_filename'],
        'OUTPUT_PATH': parser['DEFAULT']['output_path'],
        'LOG_FILE': parser['DEFAULT']['log_file'],
        'WAIT_FOR_KEYPRESS': parser['DEFAULT'].getboolean('wait_for_keypress'),
        'SANITY_SLEEP': parser['DEFAULT'].getfloat('sanity_sleep'),
        'SLEEP_MIN': parser['DEFAULT'].getfloat('sleep_min'),
        'SLEEP_MAX': parser['DEFAULT'].getfloat('sleep_max')
    }
    if not os.path.exists(config['OUTPUT_PATH']):
        log.info(f"Creating output directory {config['OUTPUT_PATH']}")
        os.makedirs(config['OUTPUT_PATH'])

    ###

    sites = []
    for section in parser.sections():  # Each section() is one site.

        if parser[section].getboolean('skip'):
            log.warning(f'Skipping {section}')
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

        log.info(f'OK {section}')

    return config, sites
