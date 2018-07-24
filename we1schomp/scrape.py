"""
"""

from we1schomp import parse
from we1schomp.browser import Browser


def urls_from_google(term, site, schema_version, search_url,
                     url_stops=[], browser=None):
    """
    """

    if not browser:
        browser = Browser()

    print(f'\nSearching Google for "{term}" at {site}.')
    browser.go(search_url.format(term=term, site=site))

    data = []

    while True:

        browser.check_for_google_captcha()

        for url in parse.urls_from_google(browser.source, url_stops):
            data.append(url)

        if not browser.next_google_result():
            break

    return data


def content_from_url(url, content_tag='p', content_length_min=250,
                     browser=None):
    """
    """

    if not browser:
        browser = Browser()

    browser.go(url)

    content = parse.content_from_html(
        browser.source, content_tag, content_length_min)

    browser.sleep()

    return content
