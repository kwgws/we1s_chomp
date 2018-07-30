# -*- coding: utf-8 -*-
"""
"""

import html
import json
import os
import string
import sys
import time
from gettext import gettext as _
from logging import getLogger
from uuid import uuid4

import bleach
import regex as re
from unidecode import unidecode


def load_article_list_from_json(path, no_skip=False):
    """
    """

    log = getLogger(__name__)
    articles = []
    count = 0

    log.info(_('log search path %s'), path)
    for json_data, json_file in load_json_files_from_path(path):

        # If a file already has stuff in the "content" key, that implies
        # we've already scraped it, so we can safely skip it here.
        if not no_skip and json_data['content'] != '':
            log.warning(_('log file load %s'), json_file)
            continue

        # Keep track of how many files we've loaded so we can report how many
        # we've skipped.
        log.info(_('log file load %s'), json_file)
        count += 1
        articles.append(json_data)

    log.info(_('log search done %s %s'), count, len(articles) - count)
    return articles


def load_json_files_from_path(path):
    """
    """

    for json_file in [f for f in os.listdir(path) if f.endswith('.json')]:

        filename = os.path.join(path, json_file)
        with open(filename, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        yield json_data, json_file


def update_article(articles, config, overwrite=True, **kwargs):
    """
    """

    log = getLogger(__name__)

    name = config['DB_NAME'].format(
        site=kwargs['site']['short_name'], 
        term=kwargs['term'], slug=kwargs['name'])
    metapath = config['METAPATH'].format(
        site=kwargs['site']['short_name'],
        term=kwargs['term'], slug=kwargs['name'])

    try:  # Are we updating an old entry or starting a new one?
        article = next(a for a in articles if a['name'] == name)

        if not overwrite:
            log.info(_('log skipping article %s'), article['name'])
            return article

        log.info(_('li updating article %s'), article['name'])

    except StopIteration:
        article = {
            'doc_id': uuid4(),
            'attachment_id': '',
            'namespace': config['NAMESPACE'],
            'name': name,
            'metapath': metapath,
            'pub': kwargs['site']['name'],
            'pub_short': kwargs['site']['short_name'],
        }
        articles.append(article)
        log.info(_('li creating new article %s'), article['name'])
    
    content = clean_string(kwargs['content'])
    length = f"{len(content.split(' '))} words" if content != '' else ''
    article.update({
        'title': kwargs['title'],
        'url': kwargs['url'],
        'content': content,
        'length': length,
        'search_term': kwargs['term']
    })

    return article


def save_article_to_json(article, config):
    """
    """

    log = getLogger(__name__)

    path = config['OUTPUT_PATH']
    log.info(_('log saving article to path %s %s'), article['name'], path)

    # Update existing files first.
    for json_file, json_data in load_json_files_from_path(path):
        if json_data['doc_id'] == article['doc_id']:
            filename = json_file
            log.info(_('log overwriting file %s'), filename)

    # Otherwise make a new file.
    if not filename:

        # Use Mirrormask timestamp format.
        now = time.localtime()
        timestamp = '{y}{m:02d}{d:02d}'.format(
            y=now.tm_year, m=now.tm_mon, d=now.tm_mday)

        # We want to store the search term in the filename if possible.
        # There might be a better way to do this--especially if we eventually
        # have to consider complex boolean search strings.
        term = slugify(article['search_term'])

        filename = config['OUTPUT_FILENAME'].format(
            index='{index}',
            timestamp=timestamp,
            site=article['pub_short'],
            term=term
        )

        # Increment filenames.
        for x in range(sys.maxsize):
            temp_filename = filename.format(index=x)
            if not os.path.exists(os.path.join(path, temp_filename)):
                filename = temp_filename
                break
        
        log.info(_('log saving new file %s'), filename)

    filename = os.path.join(path, filename)
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(article, outfile, ensure_ascii=False, indent=2)


def clean_string(dirty_string, regex_string=None):
    """
    """

    # Start by Bleaching out the HTML.
    dirty_string = bleach.clean(dirty_string, tags=[], strip=True)
    dirty_string = html.unescape(dirty_string)  # Get rid of &lt;, etc.

    # Ideally we shouldn't need this since all the content is being handled
    # "safely," but the LexisNexis import script does it, so we'll do it too
    # in case some other part of the process is expecting ASCII-only text.
    ascii_string = unidecode(dirty_string)

    # Regex processing. Experimental!
    # This looks for:
    # - URL strings, common in blog posts, etc., and probably not useful for
    #   topic modelling.
    # - Irregular punctuation, i.e. punctuation left over from formatting
    #   or HTML symbols that Bleach missed.
    if not regex_string:
        regex_string = r'http(.*?)\s|[^a-zA-Z0-9\s\.\,\!\"\'\-\:\;\p{Sc}]'
    ascii_string = re.sub(re.compile(regex_string), ' ', ascii_string)

    ascii_string = ''.join([x for x in ascii_string if x in string.printable])
    ascii_string = ' '.join(ascii_string.split())
    ascii_string = ascii_string.replace(' .', '.')  # ??

    return ascii_string


def slugify(title_string):
    """
    """

    title_string = clean_string(title_string, r'[^a-zA-Z0-9]')
    title_string = title_string.replace(' ', '_').lower()
    return title_string
