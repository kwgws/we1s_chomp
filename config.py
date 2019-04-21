# -*- coding:utf-8 -*-
""" WE1S Chomp, by Sean Gilleran and WhatEvery1Says

http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""

import os


CONTENT_TAGS = ['p']
CONTENT_LENGTH = 75

SITES = os.path.join(os.getcwd(), 'sources.csv')
QUERIES = os.path.join(os.getcwd(), 'queries.csv')
OUTPUT_PATH = os.path.join(os.getcwd(), 'output')
NAMESPACE = 'we1sv2.0'
METAPATH = 'Corpus,{name},Rawdata'

LOGFILE = os.path.join(os.getcwd(), 'chomp.log')
LOG_LEVEL = 'INFO'
LOGFILE_FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
CONSOLE_FORMAT = 'Chomp [%(levelname)s]: %(message)s'

SLEEP_TIME = (1.0, 3.0)
SELENIUM_BROWSER = 'Chrome'
SELENIUM_DRIVER = os.path.join(os.getcwd(), 'chromedriver.exe')
SELENIUM_LOG = os.path.join(os.getcwd(), 'selenium.log')
SELENIUM_WAIT_FOR_KEYPRESS = False

GOOGLE_URI = 'https://www.googleapis.com/customsearch/v1?cx={cx}&key={key}&fields=queries,items(title,link,snippet)&filter=1'
GOOGLE_URI_QUERY = '&q={term}&siteSearch={url}&start={page}'
GOOGLE_CX = os.environ['CHOMP_GOOGLE_CX']
GOOGLE_KEY = os.environ['CHOMP_GOOGLE_KEY']

WORDPRESS_URI = '/wp-json/wp/v2/'
WORDPRESS_URI_QUERIES = [
    'posts?search={term}&sentence=1&page={page}',
    'pages?search={term}&sentence=1&page={page}'
]
