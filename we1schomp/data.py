# -*- coding: utf-8 -*-
"""
"""

import os
import json
import logging
from time import localtime
from uuid import uuid4


def save_to_json(query, settings, filename=None):
    """
    """

    log = logging.getLogger(__name__)

    doc_id = str(uuid4())  # Use UUID4 library to generate unique id.
    query['doc_id'] = doc_id
    query['attachment_id'] = ''
    query['namespace'] = 'we1sv2.0'
    query['name'] = f"we1schomp_{query['pub_short']}_{doc_id}"
    query['metapath'] = f"Corpus,{query['pub_short']},Rawquery"
    log.debug(f'{query}')

    if not filename:
        now = localtime()
        timestamp = '{y}{mo:02d}{d:02d}'.format(
            y=now.tm_year, mo=now.tm_mon, d=now.tm_mday
        )
        filename = settings['OUTPUT_FILENAME'].format(
            index='{index}',
            timestamp=timestamp,
            site=query['pub_short'],
            term=query['search_term'].replace(' ', '-')
        )
        file_index = 0  # Increment filenames.
        while True:
            if not os.path.exists(os.path.join(
              settings['OUTPUT_PATH'], filename.format(index=file_index))):
                filename = filename.format(index=file_index)
                break
            file_index += 1

    filename = os.path.join(settings['OUTPUT_PATH'], filename)
    log.info(f'Saving to {filename}')
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(query, outfile, ensure_ascii=False, indent=2)


def load_from_json(path):
    """
    """

    log = logging.getLogger(__name__)

    log.info(f'Searching for JSON data in {path}')

    queries = []
    for filename in [f for f in os.listdir(path) if f.endswith('.json')]:
        fullpath = os.path.join(path, filename)
        with open(fullpath, 'r', encoding='utf-8') as json_file:
            article = json.load(json_file)
            if article['content'] == '':
                queries.append({
                    'filename': filename,
                    'article': article
                })
                log.info(f'OK {fullpath}')
            else:
                log.warning(f'Skipping {fullpath} (already scraped)')

    return queries
