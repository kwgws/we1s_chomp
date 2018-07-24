"""
"""

import random
import time
import atexit
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Browser():
    """
    """

    wait_for_keypress = False
    sleep_min = 1.0
    sleep_max = 5.0

    def __init__(self, browser_type='Chrome'):
        """
        """

        # print(f'Starting {browser_type}.')

        if browser_type == 'Chrome':

            browser_options = webdriver.ChromeOptions()
            browser_options.add_argument('--log-level=3')  # Suppress warnings.
            browser_options.add_argument('--incognito')

            driver = webdriver.Chrome(chrome_options=browser_options)
            driver.implicitly_wait(3)

            self._webdriver = driver
            atexit.register(self._webdriver.quit)

        # TODO: Additional browser implementations.
        else:
            raise NotImplementedError('Only Chrome is supported for now.')

        time.sleep(3)

    def go(self, url):
        """
        """

        time.sleep(1)

        if self.wait_for_keypress:
            input('Press "Enter" to continue...')

        return self._webdriver.get(url)

    def check_for_google_captcha(self):
        """
        """

        if '/sorry/' in self._webdriver.current_url:
            input(' ** CAPTCHA Detected. Press "Enter" when clear. **')

    @property
    def current_url(self):
        return self._webdriver.current_url

    @property
    def source(self):
        return self._webdriver.page_source

    def sleep(self):
        """
        """

        if self.sleep_max > 0.0:
                sleep_time = random.uniform(self.sleep_min, self.sleep_max)
                # print(f'Waiting for {sleep_time:.2f} seconds...')
                time.sleep(sleep_time)

    def next_google_result(self):
        """
        """

        try:
            next_page = self._webdriver.find_element_by_id('pnnext')

        except NoSuchElementException:
            # print('No additional results found.')
            return False

        self.sleep()

        next_page.click()
        return True

    def close(self):
        self._webdriver.quit()
