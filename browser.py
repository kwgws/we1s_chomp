# -*- coding: utf-8 -*-
""" WE1S Chomp, by Sean Gilleran and WhatEvery1Says

http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""

import config
import json
import random
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys


class Browser:
    """Selenium wrapper.

    Most websites either use SSL or try to block crawlers--bad news for Python's
    programmatic HTTP request modules. We can get around that by using Selenium
    to control an actual copy of Chrome.
    """

    def __init__(self):
        """Start browser and initialize Selenium driver."""

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
        """Go to a URL and collect the HTML from the response."""

        if config.SELENIUM_WAIT_FOR_KEYPRESS:
            input('Press "Enter" to continue...')
        else:
            sleep(random.uniform(*config.SLEEP_TIME))
        self._driver.get(url)
        return self._driver.page_source

    def get_json(self, url):
        """Go to a URL and collect the JSON from the response."""

        soup = BeautifulSoup(self.get_html(url), 'html5lib')
        return json.loads(soup.find('pre').text)    # Chrome-specific.

    def new_tab(self):
        """Open a new browser tab.
        
       TODO: At the moment this only works in Windows. Needs to be CMD for Mac.
        """

        body = self._driver.find_element_by_tag_name('body')
        body.send_keys(Keys.CONTROL + Keys.SHIFT + 'n')

    def close_tab(self):
        """Close current browser tab.
        
        TODO: At the moment this only works in Windows. Needs to be CMD for Mac.
        """

        body = self._driver.find_element_by_tag_name('body')
        body.send_keys(Keys.CONTROL + 'w')

    def __exit__(self, exc_type, exc_value, traceback):
        self._driver.quit()
