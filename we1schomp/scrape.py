"""
"""

from uuid import uuid1
from we1schomp import parse, save
from we1schomp.browser import Browser


def urls_from_google(settings, browser=None):
    """
    """

    if not browser:
        browser = Browser('Chrome')

    for site in settings.sections():

        browser.wait_for_keypress = settings[site].getboolean(
            'wait_for_keypress')
        browser.sleep_min = settings[site].getfloat('sleep_min')
        browser.sleep_max = settings[site].getfloat('sleep_max')

        for term in settings[site]['terms'].split(','):

            print(f'\nSearching Google for "{term}" at {site}.')
            browser.go(settings[site]['search_url'].format(term=term, site=site))  # noqa

            data = []

            while True:

                browser.check_for_google_captcha()

                for url in parse.urls_from_google(
                  browser.source, settings[site]['url_stops'].split(',')):
                    data.append(url)

                if not browser.next_google_result():
                    break

        save.urls_to_file(
            site=site, term=term, data=data,
            filename=settings[site]['output_filename'],
            output_path=settings[site]['output_path'])

    browser.close()
    print('Done!')


def content_from_sites(settings, browser=None):
    """
    """

    if not browser:
        browser = Browser('Chrome')

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

                browser.sleep()
                browser.go(article['url'])

                content = parse.content_from_html(
                    browser.source,
                    content_tag=settings[site]['content_tag'],
                    content_length_min=settings[site].get_int('content_length_min')) # noqa

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
