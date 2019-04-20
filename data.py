# -*- coding:utf-8 -*-
"""
"""

import csv
from datetime import datetime
import json
import os
from uuid import uuid4

import dateparser
from slugify import slugify

import config


def load_sites():
    """
    """

    sites = []
    with open(config.SITES, newline='') as csvfile:
        for site in csv.DictReader(csvfile):
            sites.append(dict(site))
    return sites


def save_sites(sites):
    """
    """

    with open(config.SITES, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, sites[0].keys())
        writer.writeheader()
        writer.writerows(sites)
    return sites


def load_queries():
    """
    """

    sites = load_sites()
    queries = []
    with open(config.QUERIES, newline='') as csvfile:
        for query in csv.DictReader(csvfile):
            query['startDate'] = dateparser.parse(query['startDate'])
            query['endDate'] = dateparser.parse(query['endDate'])
            query['site'] = next(s for s in sites if s['name'] == query['site'])
            queries.append(dict(query))
    return queries


def save_queries(queries):
    """
    """

    for query in queries:
        query['site'] = query['site']['name']
        query['startDate'] = query['startDate'].strftime('%Y-%m-%d')
        query['endDate'] = query['endDate'].strftime('%Y-%m-%d')
        query['chompDate'] = datetime.now().strftime('%Y-%m-%d')

    with open(config.QUERIES, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, queries[0].keys())
        writer.writeheader()
        writer.writerows(queries)
    return queries


def create_article(query, title, url, date, **kwargs):
    """
    """

    name = '_'.join([
        query['site']['name'],
        query['term'],
        query['startDate'].strftime('%Y-%m-%d'),
        query['endDate'].strftime('%Y-%m-%d')
    ])
    path = os.path.join(config.OUTPUT_PATH, name)
    if not os.path.exists(path):
        os.makedirs(path)
    i = 0
    while os.path.exists(os.path.join(path, name + '_' + str(i) + '.json')):
        i += 1
    name += '_' + str(i)
    
    article = {
        'doc_id': kwargs.get('doc_id', str(uuid4())),
        'attachment_id': '',
        'pub': query['site']['title'],
        'pub_short': query['site']['name'],
        'pub_date': date.strftime('%Y-%m-%d'),
        'chomp_date': datetime.now().strftime('%Y-%m-%d'),
        'length': len(kwargs.get('content', '')),
        'title': title,
        'content': kwargs.get('content', ''),
        'name': name,
        'url': url,
        'content_raw': kwargs.get('content_raw', ''),
        'namespace': config.NAMESPACE,
        'metapath': config.METAPATH.format(name=name)
    }

    with open(os.path.join(path, name + '.json'), 'w', encoding='utf-8') as jsonfile:
        json.dump(article, jsonfile, ensure_ascii=False, indent=2)
    return article


def load_articles():
    """
    """

    articles = []
    for (dirpath, dirnames, filenames) in os.walk(config.OUTPUT_PATH):
        for filename in filenames:
            if filename.endswith('.json'):
                filename = os.path.join(dirpath, filename)
                print('loading ' + filename)
                with open(filename, 'r', encoding='utf-8') as jsonfile:
                    article = json.load(jsonfile)
                article['filename'] = filename
                articles.append(article)
    return articles


def save_articles(articles):
    """
    """

    for article in articles:
        filename = article['filename']
        print('saving ' + filename)
        article.pop('filename')
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(article, jsonfile, ensure_ascii=False, indent=2)
