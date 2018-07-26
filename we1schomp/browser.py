# -*- coding: utf-8 -*-
"""
"""

import os
import atexit
import random
from time import sleep
from selenium import webdriver
from selenium.common import exceptions


class Browser(object):
    """
    """

    BROWSER_TYPE = 'Chrome'
    WAIT_FOR_KEYPRESS = False
    SANITY_SLEEP = 2.0  # Seconds to wait between each browser action.
    SLEEP_MIN = 1.0
    SLEEP_MAX = 1.0

    def __init__(self, browser_type='Chrome', settings=None):
        self.BROWSER_TYPE = browser_type
        self._driver = self.get_driver()

        # We need to guarantee the driver closes when we're done with it.
        # There's probably a better way to do this!
        atexit.register(self.close)

        if settings is not None:
            self.WAIT_FOR_KEYPRESS = settings['WAIT_FOR_KEYPRESS']
            self.SLEEP_MIN = settings['SLEEP_MIN']
            self.SLEEP_MAX = settings['SLEEP_MAX']

    @property
    def current_url(self):
        """
        """

        return self._driver.current_url

    @property
    def source(self):
        """
        """

        return self._driver.page_source

    def get_driver(self):
        """
        """

        if self.BROWSER_TYPE == 'Chrome':

            opts = webdriver.ChromeOptions()
            opts.add_argument('--log-level=3')  # Suppress warnings.
            opts.add_argument('--incognito')
            driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
            driver = webdriver.Chrome(
                executable_path=driver_path, chrome_options=opts)
            driver.implicitly_wait(self.SANITY_SLEEP)

            sleep(self.SANITY_SLEEP)

            return driver

        # TODO: Support for all Selenium-compatible browsers.
        raise NotImplementedError(f'"{self.BROWSER_TYPE}" is not supported.')

    def go(self, url):
        """
        """

        if self.WAIT_FOR_KEYPRESS:
            input('Press "Enter" to continue...')
        sleep(self.SANITY_SLEEP)

        return self._driver.get(url)

    def sleep(self):
        """
        """

        sleep_time = random.uniform(self.SLEEP_MIN, self.SLEEP_MAX)
        sleep(sleep_time)

    def captcha_check(self):
        """
        """

        msg_once = False

        while '/sorry/' in self._driver.current_url:
            if not msg_once:
                print('CAPTCHA detected...', end='')
                msg_once = True
            sleep(self.SANITY_SLEEP)

        if not '/sorry/' in self._driver.current_url and msg_once:
            print('Ok!')
            msg_once = False

    def click_on_id(self, tag_id):
        """
        """

        try:
            item = self._driver.find_element_by_id(tag_id)
        except exceptions.NoSuchElementException:
            print(f'No element found with id "{tag_id}".')
            return False

        item.click()
        sleep(self.SANITY_SLEEP)

        return True

    def close(self):
        """
        """

        self._driver.quit()
