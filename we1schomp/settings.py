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

    # Create the output path if it doesn't exist yet.
    if not os.path.exists(settings['OUTPUT_PATH']):
        log.info(_('log dir create %s'), settings['OUTPUT_PATH'])
        os.makedirs(settings['OUTPUT_PATH'])

    return settings, sites


def get_settings(config):
    """
    """

    # Make the function call a little shorter.
    config = config['DEFAULT']

    settings = {
        # Common metadata
        'DB_NAME': config['dbName'], 'METAPATH': config['metapath'],
        'NAMESPACE': config['namespace'],
        'OUTPUT_FILENAME': config['outputFilename'],
        'OUTPUT_PATH': config['outputPath'],

        # Browser settings
        'WAIT_FOR_KEYPRESS': config.getboolean('browserWaitForKeypress'),
        'SANITY_SLEEP': config.getfloat('browserSanitySleep'),
        'SLEEP_MIN': config.getfloat('browserSleepMin'),
        'SLEEP_MAX':
            max([config.getfloat('browserSleepMin'),
                 config.getfloat('browserSleepMax')]),
        
        # Scrape settings
        'WORDPRESS_ENABLE_SCRAPE':
            config.getboolean('wpEnable'),
        'WORDPRESS_API_URL': config['wpApiUrl'],
        'WORDPRESS_PAGES_QUERY_URL': config['wpPagesQueryUrl'],
        'WORDPRESS_POSTS_QUERY_URL': config['wpPostsQueryUrl'],

        'GOOGLE_ENABLE_SCRAPE':
            config.getboolean('googleEnable'),
        'GOOGLE_QUERY_URL': config['googleQueryUrl'],

        'DIRECT_ENABLE_SCRAPE':
            config.getboolean('urlScrapeEnable')
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
            log.warning(_('log file skip %s'), name)
            continue

        # Remove unnecessary protocol information from URLs.
        url = site['site'].replace('http://', '').replace('https://', '')
        url = url.strip('/')

        # Split comma-separated values into Python lists.
        terms = site['terms'].strip(',').split(',')
        google_stopwords = site['googleStopwords'].strip(',').split(',')
        
        site = {
            # Basic metadata
            'name': site['name'], 'short_name': name,
            'terms': terms, 'url': url,

            # Wordpress scrape settings
            'wordpress_enable_pages': site.getboolean('wpGetPages'),
            'wordpress_enable_posts': site.getboolean('wpGetPosts'),

            # Google scrape settings
            'google_stopwords': google_stopwords,
            'content_tag': site['urlScrapeContentTag'],
            'content_length_min': site.getint('urlScrapeContentLengthMin')
        }

        log.info(_('log file load %s'), name)
        yield site


def get_logger(config, log_level='info'):
    """
    """

    config = config['DEFAULT']
    
    log_file = logging.FileHandler(config['logfile'])
    log_file.setFormatter(logging.Formatter(config['logfileFormat']))

    console_log = logging.StreamHandler()
    console_log.setFormatter(logging.Formatter(config['consoleFormat']))

    log_level = getattr(logging, log_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(_('err invalid log level %s'), log_level)
    logging.basicConfig(level=log_level, handlers=[log_file, console_log])

    log = logging.getLogger(__name__)
    log.debug(_('log start %s'), log_file)
    return log
