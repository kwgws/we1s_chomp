# -*- coding: utf-8 -*-
"""
"""

import json
import logging
import os
import string
import sys
from gettext import gettext as _
from time import localtime

from unidecode import unidecode


def save_article_to_json(article, settings):
    """
    """

    log = logging.getLogger(__name__)

    path = settings['OUTPUT_PATH']
    filename = get_filename(path, article, settings)
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(article, outfile, ensure_ascii=False, indent=2)

    log.info(_('we1schomp_log_article_save_%s'), filename)


def get_filename(path, article, settings):
    """
    """

    log = logging.getLogger(__name__)

    # Update queried files with content.
    for json_file, json_data in find_json_files_in_path(path):
        if json_data['doc_id'] == article['doc_id']:
            filename = json_file
            log.debug(_('we1schomp_log_filename_found_%s'), filename)
            return filename

    # Get a timestamp for use in the filename. This is the same format used
    # for zip files on the Mirrormask server.
    now = localtime()
    timestamp = '{y}{mo:02d}{d:02d}'.format(
        y=now.tm_year, mo=now.tm_mon, d=now.tm_mday
    )

    # We want to store the search term in the filename if we can.
    # There might be a better way to do this--especially if we eventually
    # have to consider boolean search strings.
    term = clean_str(article['search_term']).replace(' ', '-')

    filename = settings['OUTPUT_FILENAME'].format(
        index='{index}',
        timestamp=timestamp,
        site=article['pub_short'],
        term=term
    )

    # Increment filenames.
    for x in range(sys.maxsize):
        temp_filename = os.path.join(path, filename.format(index=x))
        if not os.path.exists(temp_filename):
            filename = temp_filename
            break

    log.debug(_('we1schomp_log_filename_new_%s'), filename)
    return filename


def load_articles_from_json(path, no_skip=False):
    """
    """

    log = logging.getLogger(__name__)

    log.info(_('we1schomp_log_file_search_start_%s'), path)
    articles = []
    count = 0

    for json_file, json_data in find_json_files_in_path(path):

        # If a file already has stuff in the "content" key, that implies
        # we've already scraped it, so we can safely skip it.
        if not no_skip and json_data['content'] is not None:
            log.warning(_('we1schomp_log_file_skip_%s'), json_file)
            continue

        log.warning(_('we1schomp_log_file_skip_%s'), json_file)
        count += 1
        articles.append(json_data)

    log.info(_('we1schomp_log_file_search_done_%d_%d'), count, len(articles) - count)
    return articles


def find_json_files_in_path(path):
    """
    """

    for filename in [f for f in os.listdir(path) if f.endswith('.json')]:

        filename = os.path.join(path, filename)
        with open(filename, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        yield filename, json_data


def clean_str(dirty_string):
    """
    """

    # Ideally we shouldn't need this since all the content is being handled
    # "safely," but the LexisNexis import script does it, so we'll do it too
    # in case some other part of the process is expecting ASCII-only text.
    # It also has the handy side-effect of compacting extra whitespace!
    ascii_string = unidecode(dirty_string)
    ascii_string = ''.join([x for x in ascii_string if x in string.printable])
    ascii_string = ' '.join(ascii_string.split())
    return ascii_string
