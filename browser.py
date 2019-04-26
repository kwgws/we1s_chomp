# -*- coding: utf-8 -*-
""" WE1S Chomp, by Sean Gilleran and WhatEvery1Says

http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
from gettext import gettext as _
import json
from logging import getLogger
import random
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import config


class Browser:
    """Selenium wrapper.

    Most websites either use SSL or try to block crawlers--bad news for Python's
    programmatic HTTP request modules. We can get around that by using Selenium
    to control an actual copy of Chrome.
    """

    def __init__(self):
        if config.SELENIUM_BROWSER != 'Chrome':
            raise NotImplementedError('%s is not a supported browser type.', config.SELENIUM_BROWSER)
            exit()

        options = webdriver.ChromeOptions()
        options.add_argument('--log-level=3')   # Suppress warnings.
        options.add_argument('--incognito')     # In case we hit paywalls.

        # Disable images.
        options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})

        self._driver = webdriver.Chrome(
            executable_path=config.SELENIUM_DRIVER,
            service_log_path=config.SELENIUM_LOG,
            chrome_options=options
        )
        self._driver.implicitly_wait(config.SLEEP_TIME[0])

    def __enter__(self):
        return self

    def get_html(self, url):
        if config.SELENIUM_WAIT_FOR_KEYPRESS:
            input(_('Press "Enter" to continue...'))
        else:
            sleep(random.uniform(*config.SLEEP_TIME))
        self._driver.get(url)
        return self._driver.page_source

    def get_json(self, url):
        log = getLogger(__name__)

        soup = BeautifulSoup(self.get_html(url), 'html5lib')
        data = soup.find('pre').text    # Chrome-specific.
        if data is None:
            log.info(_('Could not find JSON at URL: %s'), url)
            return None
        return json.loads(data)

    def new_tab(self):
        # TODO: At the moment this only works in Windows. Needs to be CMD for Mac.
        body = self._driver.find_element_by_tag_name('body')
        body.send_keys(Keys.CONTROL + Keys.SHIFT + 'n')

    def close_tab(self):
        # TODO: At the moment this only works in Windows. Needs to be CMD for Mac.
        body = self._driver.find_element_by_tag_name('body')
        body.send_keys(Keys.CONTROL + 'w')

    def __exit__(self, exc_type, exc_value, traceback):
        self._driver.quit()
