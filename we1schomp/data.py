# -*- coding: utf-8 -*-
"""
"""

import os
import json
from time import localtime
from uuid import uuid4


def save_to_json(query, settings, filename=None):
    """
    """

    # Generate a unique document id with the UUID library. This can be made
    # more unique/secure if necessary.
    doc_id = str(uuid4())
    now = localtime()

    query['doc_id'] = doc_id
    query['attachment_id'] = ''
    query['namespace'] = 'we1sv2.0'
    query['name'] = f"we1schomp_{query['pub_short']}_{doc_id}"
    query['metapath'] = f"Corpus,{query['pub_short']},Rawquery"

    if not filename:

        timestamp = '{y}{mo:02d}{d:02d}'.format(
            y=now.tm_year, mo=now.tm_mon, d=now.tm_mday)
        filename = settings['OUTPUT_FILENAME'].format(
            index='{index}',
            timestamp=timestamp,
            site=query['pub_short'],
            term=query['search_term'].replace(' ', '-')
        )

        file_index = 0
        while True:
            if not os.path.exists(os.path.join(
              settings['OUTPUT_PATH'], filename.format(index=file_index))):
                filename = filename.format(index=file_index)
                break
            file_index += 1

    filename = os.path.join(settings['OUTPUT_PATH'], filename)

    print(f'Saving: {filename}...', end='')

    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(query, outfile, ensure_ascii=False, indent=2)

    print('Ok!')


def load_from_json(path):
    """
    """

    print(f'Searching for JSON files: {path}')

    queries = []

    for filename in [f for f in os.listdir(path) if f.endswith('.json')]:

        fullpath = os.path.join(path, filename)

        print(f'> {fullpath}...', end='')

        with open(fullpath, 'r', encoding='utf-8') as json_file:
            article = json.load(json_file)
            if article['content'] == '':
                queries.append({
                    'filename': filename,
                    'article': article
                })
                print('Ok!')
            else:
                print('Skipping.')

    return queries
