# -*- coding: utf-8 -*-
"""
"""

import logging
import os
from configparser import SafeConfigParser
from gettext import gettext as _


def from_ini(filename):
    """
    """

    parser = SafeConfigParser()
    if not parser.read(filename):
        # TODO: Use default settings if not found.
        raise FileNotFoundError(filename)

    settings = get_settings(parser)
    log = get_logger(parser)
    sites = [site for site in get_sites(parser)]
    print(sites)

    # Create the output path if it doesn't exist yet.
    if not os.path.exists(settings['OUTPUT_PATH']):
        log.info(_('we1schomp_log_dir_create_%s'), settings['OUTPUT_PATH'])
        os.makedirs(settings['OUTPUT_PATH'])

    return settings, sites


def get_settings(config):
    """
    """

    # Make the function call a little shorter.
    config = config['DEFAULT']

    settings = {
        'WAIT_FOR_KEYPRESS': config.getboolean('wait_for_keypress'),
        'SANITY_SLEEP': config.getfloat('sanity_sleep'),
        'SLEEP_MIN': config.getfloat('sleep_min'),
        'SLEEP_MAX':
            max([config.getfloat('sleep_min'), config.getfloat('sleep_max')]),
        'OUTPUT_FILENAME': config['output_filename'],
        'OUTPUT_PATH': config['output_path']
    }

    return settings


def get_sites(config):
    """
    """

    log = logging.getLogger(__name__)

    for name in config.sections():

        site = config[name]

        # Skip any sites flagged with "skip=true".
        if site.getboolean('skip'):
            log.warning(_('we1schomp_log_file_skip_%s'), name)
            continue
        
        site = {
            'short_name': name,
            'name': site['name'],
            'url': site['site'].replace('http://', '').replace('https://', ''),
            'terms': site['terms'].strip(',').split(','),
            'url_stops': site['url_stops'].strip(',').split(','),
            'query_string': site['search_url'],
            'content_tag': site['content_tag'],
            'length_min': site.getint('length_min'),
            'wp_pages': site.getboolean('wp_search_pages'),
            'wp_posts': site.getboolean('wp_search_posts'),
        }

        log.info(_('we1schomp_log_file_load_%s'), name)
        yield site


def get_logger(config, log_level='info'):
    """
    """

    config = config['DEFAULT']
    
    log_file = logging.FileHandler(config['log_file'])
    log_file.setFormatter(logging.Formatter(config['log_file_format']))

    console_log = logging.StreamHandler()
    console_log.setFormatter(logging.Formatter(config['console_format']))

    log_level = getattr(logging, log_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(_('we1schomp_err_invalid_log_level_%s'), log_level)
    logging.basicConfig(level=log_level, handlers=[log_file, console_log])

    log = logging.getLogger(__name__)
    log.debug(_('we1schomp_log_start'))
    return log
