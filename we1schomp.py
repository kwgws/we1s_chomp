# -*- coding: utf-8 -*-
"""
"""

from uuid import uuid1
from argparse import ArgumentParser
from we1schomp import config, scrape, parse, save
from we1schomp.browser import Browser


def scrape_urls_from_google(settings='settings.ini'):
    """
    """

    settings = config.load_from_file(settings)

    browser = Browser('Chrome')

    for site in settings.sections():

        browser.wait_for_keypress = settings[site].getboolean(
            'wait_for_keypress')
        browser.sleep_min = settings[site].getfloat('sleep_min')
        browser.sleep_max = settings[site].getfloat('sleep_max')

        for term in settings[site]['terms'].split(','):

            save.urls_to_file(
                site=site, term=term,
                data=scrape.urls_from_google(
                    term=term, site=site, browser=browser,
                    schema_version=settings[site]['schema_version'],
                    search_url=settings[site]['search_url'],
                    url_stops=settings[site]['url_stops'].split(',')),
                filename=settings[site]['output_filename'],
                output_path=settings[site]['output_path'])
    
    browser.close()


def scrape_content_from_sites(settings='settings.ini'):
    """
    """

    settings = config.load_from_file(settings)

    browser = Browser('Chrome')

    for site in settings.sections():

        if settings[site].getboolean('urls_only'):
            print(f'Skipping {site}.')
            continue

        browser.wait_for_keypress = settings[site].getboolean(
            'wait_for_keypress')
        browser.sleep_min = settings[site].getfloat('sleep_min')
        browser.sleep_max = settings[site].getfloat('sleep_max')

        for term in settings[site]['terms'].split(','):

            articles = parse.urls_from_file(
                filename=settings[site]['output_filename'].format(
                    site=site.replace('.', '-').replace('/', '-'),
                    term=term.replace(' ', '-'),
                    timestamp='').split('.')[0].strip('_'),
                path=settings[site]['output_path'])

            count = 0

            for article in articles:

                content = scrape.content_from_url(
                    url=article['url'], browser=browser,
                    content_tag=settings[site]['content_tag'],
                    content_length_min=settings[site].getint('content_length_min'))  # noqa

                name = settings[site]['output_filename'].format(
                    site=site.replace('.', '-').replace('/', '-'),
                    term=term.replace(' ', '-'),
                    timestamp=''
                ).replace('urls', f'{count:003d}').split('.')[0].strip('_')

                save.article_to_file(
                    data={
                        'doc_id': str(uuid1()),
                        'term': term,
                        'site': site,
                        'url': article['url'],
                        'attachment_id': '',
                        'pub': settings[site]['name'],
                        'pub_date': article['date'],
                        'length': f'{len(content.split(" "))} words',
                        'title': article['title'],
                        'content': content,
                        'name': name,
                        'namespace': 'we1sv2.0',
                        'metapath': f'Corpus,{name},Rawdata'},
                    filename=settings[site]['output_filename'].replace(
                        'urls', f'{count:003d}'),
                    output_path=settings[site]['output_path'])

                count += 1

    browser.close()
    print('Done!')


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument(
        '--settings_file', type=str, metavar='S',
        help='Settings file to use (default: "settings.ini").',
        default='settings.ini')
    parser.add_argument(
        '--urls_only', action='store_true',
        help='Only scrape Google, not individual results.')
    parser.add_argument(
        '--articles_only', action='store_true',
        help='Only get artiles, not Google results.')
    args = parser.parse_args()

    if args.urls_only and not args.articlesl_only:
        scrape_urls_from_google(args.settings_file)
        exit()

    if args.articles_only and not args.urls_only:
        scrape_content_from_sites(args.settings_file)
        exit()

    scrape_urls_from_google(args.settings_file)

    print('\n')

    scrape_content_from_sites(args.settings_file)
    exit()
