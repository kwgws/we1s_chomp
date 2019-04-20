# -*- coding: utf-8 -*-
"""
"""

import config
import json
import random
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions


class Browser:
    """
    """

    def __init__(self):
        """
        """

        if config.SELENIUM_BROWSER != 'Chrome':
            raise NotImplementedError('%s is not a supported browser type.', config.SELENIUM_BROWSER)
            exit()

        options = webdriver.ChromeOptions()
        options.add_argument('--log-level=3')   # Suppress warnings.
        options.add_argument('--incognito')

        self._driver = webdriver.Chrome(
            executable_path=config.SELENIUM_DRIVER,
            service_log_path=config.SELENIUM_LOG,
            chrome_options=options
        )
        self._driver.implicitly_wait(config.SLEEP_TIME[0])
    
    def __enter__(self):
        return self

    def get_html(self, url):
        """
        """

        if config.SELENIUM_WAIT_FOR_KEYPRESS:
            input('Press "Enter" to continue...')
        self._driver.get(url)
        return self._driver.page_source

    def get_json(self, url):
        """
        """

        soup = BeautifulSoup(self.get_html(url), 'html5lib')
        return json.loads(soup.find('pre').text)

    def sleep(self):
        sleep(random.uniform(*config.SLEEP_TIME))

    def __exit__(self, exc_type, exc_value, traceback):
        self._driver.quit()
