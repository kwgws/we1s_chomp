# -*- coding:utf-8 -*-
""" WE1S Chomp, by Sean Gilleran and WhatEvery1Says

http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""

from copy import deepcopy
import csv
from datetime import datetime
from gettext import gettext as _
import json
from logging import getLogger
import os
from uuid import uuid4

import dateparser

import config


class Data:
    """Database-like wrapper for file handling."""

    def __init__(self):
        self.load_all()

    def load_all(self):
        self.load_sites()
        self.load_queries()
        self.load_articles()

    def load_sites(self):
        log = getLogger(__name__)

        log.info(_('Loading sites from %s...'), config.SITES)
        self.sites = []
        with open(config.SITES, newline='') as csvfile:
            for site in csv.DictReader(csvfile):
                self.sites.append(dict(site))
                log.debug(_('...%s ok.'), site['title'])
        log.info(_('Done!'))

    def load_queries(self):
        log = getLogger(__name__)

        log.info(_('Loading queries from %s...'), config.QUERIES)
        self.queries = []
        with open(config.QUERIES, newline='') as csvfile:
            for query in csv.DictReader(csvfile):
                query['startDate'] = dateparser.parse(query['startDate'])
                query['endDate'] = dateparser.parse(query['endDate'])
                if query['chompDate'] != '':
                    query['chompDate'] = dateparser.parse(query['chompDate'])
                if query['count'] == '':
                    query['count'] = 0
                else:
                    query['count'] = int(query['count'])
                query['site'] = next(s for s in self.sites if s['name'] == query['site'])
                self.queries.append(query)
                log.debug(_('..."%s" at %s ok.'), query['term'], query['site']['name'])
        log.info(_('Done!'))

    def load_articles(self):
        log = getLogger(__name__)

        log.info(_('Loading articles from %s...'), config.OUTPUT_PATH)
        self.articles = []
        for (dirpath, dirnames, filenames) in os.walk(config.OUTPUT_PATH):
            for filename in filenames:
                if filename.endswith('.json'):
                    filename = os.path.join(dirpath, filename)
                    with open(filename, 'r', encoding='utf-8') as jsonfile:
                        article = json.load(jsonfile)
                        article['site'] = next(s for s in self.sites if s['name'] == article['pub_short'])
                        article['filename'] = filename
                        self.articles.append(article)
                        log.debug(_('...%s ok.'), article['filename'])
        log.info(_('Done!'))

    def save_all(self):
        self.save_articles()
        self.save_queries()
        self.save_sites()

    def save_sites(self):
        log = getLogger(__name__)

        log.info(_('Saving %i sites to %s...'), len(self.sites), config.SITES)
        with open(config.SITES, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, self.sites[0].keys())
            writer.writeheader()
            writer.writerows(self.sites)
        log.info(_('Done!'))

    def save_queries(self):
        log = getLogger(__name__)

        log.info(_('Saving %i queries to %s...'), len(self.queries), config.QUERIES)
        safe_queries = deepcopy(self.queries)
        for query in safe_queries:
            query['site'] = query['site']['name']
            query['startDate'] = query['startDate'].strftime('%Y-%m-%d')
            query['endDate'] = query['endDate'].strftime('%Y-%m-%d')
            if query['chompDate'] != '':
                query['chompDate'] = query['chompDate'].strftime('%Y-%m-%d')
            if query['count'] == 0:
                query['count'] = ''
        with open(config.QUERIES, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, safe_queries[0].keys())
            writer.writeheader()
            writer.writerows(safe_queries)
        log.info(_('Done!'))

    def create_article(self, query, title, url, date, **kwargs):
        log = getLogger(__name__)

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

        filename = os.path.join(path, name + '.json')
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(article, jsonfile, ensure_ascii=False, indent=2)
        log.debug(_('Article created at %s'), filename)

        article['filename'] = os.path.join(path, name + '.json')
        article['site'] = next(s for s in self.sites if s['name'] == article['pub_short'])
        self.articles.append(article)
        return article

    def save_articles(self):
        log = getLogger(__name__)

        log.info(_('Saving %i articles to %s...'), len(self.articles), config.OUTPUT_PATH)
        for article in self.articles:
            safe_article = deepcopy(article)
            filename = article['filename']
            safe_article.pop('filename')
            safe_article.pop('site')
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(safe_article, jsonfile, ensure_ascii=False, indent=2)
            log.debug(_('...%s ok.'), filename)
        log.info(_('Done!'))
