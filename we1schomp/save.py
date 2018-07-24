"""
"""

import os
import json
import time


def timestamp():
    # Use date format from Mirrormask projects
    now = time.localtime()
    return '{y}{mo:02d}{d:02d}_{h:02d}{mn:02d}'.format(
        y=now.tm_year, mo=now.tm_mon, d=now.tm_mday,
        h=now.tm_hour, mn=now.tm_min)


def urls_to_file(data, site, term, filename, output_path='output'):
    """
    """

    filename = filename.format(
        site=site.replace('.', '-').replace('/', '-'),
        term=term.replace(' ', '-'),
        timestamp=timestamp())
    output_path = os.path.join(output_path, 'urls')
    filename = os.path.join(output_path, filename)

    print(f'Saving data to {filename}.')

    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)


def article_to_file(data, filename, output_path='output'):
    """
    """

    filename = filename.format(
        site=data['site'].replace('.', '-').replace('/', '-'),
        term=data['term'].replace(' ', '-'),
        timestamp=timestamp())
    filename = os.path.join(output_path, filename)

    print(f'Saving data to {filename}.')

    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)
