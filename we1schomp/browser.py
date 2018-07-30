# -*- coding: utf-8 -*-
"""
"""

import logging
import os
import random
from gettext import gettext as _
from time import sleep

from selenium import webdriver
from selenium.common import exceptions


class Browser:
    """
    """

    BROWSER_TYPE = 'Chrome'
    WAIT_FOR_KEYPRESS = False
    SANITY_SLEEP = 1.0  # Seconds to wait between each browser action.
    SLEEP_MIN = 1.0
    SLEEP_MAX = 1.0

    def __init__(self, browser_type='Chrome', settings=None):
        """
        """

        self._log = logging.getLogger(__name__)

        self.BROWSER_TYPE = browser_type
        if settings is not None:
            self.WAIT_FOR_KEYPRESS = settings['WAIT_FOR_KEYPRESS']
            self.SLEEP_MIN = settings['SLEEP_MIN']
            self.SLEEP_MAX = settings['SLEEP_MAX']
            self.SANITY_SLEEP = settings['SANITY_SLEEP']
        
        self._driver = self.get_driver()

        # We need to guarantee the driver closes when we're done with it.
        # There's probably a better way to do this!
        # atexit.register(self.close)
        
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

        self._log.info(_('Starting %s.'), self.BROWSER_TYPE)

        if self.BROWSER_TYPE == 'Chrome':

            opts = webdriver.ChromeOptions()
            opts.add_argument('--log-level=3')  # Suppress warnings.
            opts.add_argument('--incognito')

            driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
            self._log.debug(_('Using WebDriver at %s.'), driver_path)

            driver = webdriver.Chrome(
                executable_path=driver_path,
                service_log_path='selenium.log',
                chrome_options=opts)
            driver.implicitly_wait(self.SANITY_SLEEP)

            self.sleep(self.SANITY_SLEEP)

            return driver

        # TODO: Support for all Selenium-compatible browsers.
        raise NotImplementedError(
            _('%s is not a supported browser type.' % self.BROWSER_TYPE))

    def go(self, url):
        """
        """
        
        if self.WAIT_FOR_KEYPRESS:
            input(_('Press "Enter" to continue...'))

        self._log.info(_('%s going to: %s'), self.BROWSER_TYPE, url)
        return self._driver.get(url)

    def sleep(self, sleep_time=None):
        """
        """

        if not sleep_time:
            sleep_time = random.uniform(self.SLEEP_MIN, self.SLEEP_MAX)

        self._log.debug(_('Sleeping for %.2f seconds.'), sleep_time)
        sleep(sleep_time)

    def captcha_check(self):
        """
        """

        if '/sorry/' in self._driver.current_url:
            self._log.error(_('CAPTCHA detected! Waiting for human...'))
            while '/sorry/' in self._driver.current_url:
                sleep(self.SANITY_SLEEP)
            self._log.info(_('Ok!'))
            self.sleep()

    def click_on_id(self, tag_id):
        """
        """

        try:
            item = self._driver.find_element_by_id(tag_id)
        except exceptions.NoSuchElementException:
            return False

        item.click()

        return True

    def close(self):
        """
        """

        self._log.info(_('Closing %s.'), self.BROWSER_TYPE)
        self._driver.quit()
