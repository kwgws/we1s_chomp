"""
"""

import os
from configparser import SafeConfigParser


def load_defaults(parser=None):
    """
    """
    if not parser:
        parser = SafeConfigParser()

    parser['DEFAULT'] = {
        'terms': (
            'humanities,'
            'liberal arts'),
        'url_stops': (
            '/author,'
            '/writer,'
            '/biography,'
            '/contributor,'
            '/tag,'
            '/tool,'
            '/page/,'
            'forum.,'
            'forums.,'
            '/el/,'
            '/de/,'
            '/fr/,'
            '.pdf'),
        'schema_version': 'we1schomp_2',
        'output_filename': '{site}_{term}_urls_{timestamp}.json',
        'output_path': 'output',
        'search_url': 'http://google.com/search?q="{term}"+site%%3A{site}&safe=off&filter=0',  # noqa
        'wait_for_keypress': False,
        'sleep_min': 1.0,
        'sleep_max': 5.0}
    parser['we1s.ucsb.edu'] = {}

    return parser


def load_from_file(filename='settings.ini'):
    """
    """

    print(f'Loading settings from {filename}.')
    parser = SafeConfigParser()

    if not parser.read(filename):
        print('File not found! Loading defaults.')
        parser = load_defaults(parser)
        save_to_file(parser)

    # Parse & fix common input errors.
    for site in parser.sections():
        if not os.path.exists(parser[site]['output_path']):
            os.makedirs(parser[site]['output_path'])
        if not os.path.exists(os.path.join(parser[site]['output_path'], 'urls')):  # noqa
            os.makedirs(os.path.join(parser[site]['output_path'], 'urls'))
        if parser[site]['sleep_max'] < parser[site]['sleep_min']:
            parser[site]['sleep_max'] = parser[site]['sleep_min']

    return parser


def save_to_file(parser, filename='settings.ini'):
    """
    """

    print(f'Saving settings to {filename}.')

    with open(filename, 'w') as configfile:
        parser.write(configfile)
