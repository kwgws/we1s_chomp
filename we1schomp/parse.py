"""
"""

import os
import json
import bleach
from bs4 import BeautifulSoup


def urls_from_google(html, url_stops=None):
    """
    """

    soup = BeautifulSoup(html, 'html5lib')

    urls = []

    for div in soup.find_all('div', {'class': 'rc'}):

        link = div.find('a')

        href = str(link.get('href'))

        # Drop results that include stop words.
        stop_flag = False
        for stop in url_stops:
            if stop in href:
                stop_flag = True
                break
        if stop_flag:
            continue

        # TODO: Refactor this to catch relative dates; "Just now," etc.
        try:
            date = str(div.find('span', {'class': 'f'}).text)
            date = date.replace(' - ', '')
        except AttributeError:
            date = 'N.D.'

        urls.append({
            'title': str(link.text).split('http')[0],
            'url': href,
            'date': date})

    return urls


def urls_from_file(filename, path):
    """
    """

    for item in os.listdir(os.path.join(path, 'urls')):

        if filename in str(item):

            with open(os.path.join(path, 'urls', item)) as url_file:
                data = json.load(url_file)

            return data

    raise FileNotFoundError(os.path.join(path, 'urls', filename))


def content_from_html(html, content_tag='p', content_length_min=250):

    soup = BeautifulSoup(html, 'html5lib')

    content = soup.find_all(content_tag)

    result = ''
    
    for item in content:
        if len(item.text) > content_length_min:
            result += item.text

    return bleach.clean(result).strip()
