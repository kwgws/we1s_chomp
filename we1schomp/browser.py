# -*- coding: utf-8 -*-
"""
we1schomp/browser.py


WE1SCHOMP ©2018-19, licensed under MIT.
A Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says.
http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
import json
from logging import getLogger
from random import uniform as randfloat
import subprocess
from time import sleep
from typing import Dict, List, Tuple, Union

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


class Browser:
    """
    Web browser wrapper.

    Most websites either use SSL or attempt to block simple crawlers--bad news
    for Python's programmatic HTTP request modules. We can (mostly) get around
    that by either using Lynx, or, failing that, using Selenium to control an
    actual copy of Chrome.
    """

    ###
    def __init__(
        self,
        lynx_path: str = None,
        chrome_path: str = None,
        chrome_log_path: str = None,
        wait_time: Tuple[float, float] = (1.0, 3.0),
    ):
        """Create a new Browser instance."""
        self._log = getLogger(__name__)

        self.wait_time = wait_time

        self._lynx = lynx_path

        self._driver = self._actions = None
        if chrome_path is not None and chrome_path != "":
            self._log.info("Initializing Chrome with Selenium...")

            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")
            options.add_argument("--incognito")
            options.add_argument("--log-level=3")  # Suppress common warnings.
            options.add_argument("--incognito")  # Use incognito mode.
            options.add_experimental_option(  # Disable (most) images.
                "prefs", {"profile.managed_default_content_settings.images": 2}
            )
            self._driver = webdriver.Chrome(
                executable_path=chrome_path,
                service_log_path=chrome_log_path,
                chrome_options=options,
            )
            self._driver.implicitly_wait(wait_time[0])
            self._actions = ActionChains(self._driver)

    ###
    def __enter__(self):
        """Enter runtime context; used for "with" statement."""
        return self

    ###
    def __exit__(self, exc_type, exc_value, traceback):
        """Tear down runtime context; used for "with" statement."""
        if self._driver is not None:
            self._driver.quit()

    ###
    def stop(self, repeat: int = 3) -> None:
        """Stop browser."""
        if self._actions is not None:
            for i in range(0, repeat):
                sleep(0.5)
                self._actions.send_keys(Keys.ESCAPE)

    ###
    def get(self, url: str, get_json: bool = False) -> Union[Dict, List, str]:
        """Get the HTML result from a URL."""

        if "http://" not in url and "https://" not in url:
            url = f"http://{url}"
        self._log.info("Browser going to %s" % url)

        try:
            source = self.lynx_get(url, get_json)
        except json.JSONDecodeError:
            source = self.chrome_get(url, get_json)
        if not source:
            source = self.chrome_get(url, get_json)

        sleep(randfloat(*self.wait_time))
        return source

    ###
    def chrome_get(self, url: str, get_json: bool = False) -> Union[Dict, List, str]:
        """
        """
        source = None

        if self._driver is not None:
            try:
                self._driver.get(url)

                if get_json:
                    source = self._driver.find_element_by_tag_name("pre").text
                    source = json.loads(source)
                else:
                    self.stop()
                    source = str(self._driver.page_source)

            except WebDriverException as e:
                self._log.warning("Browser error: %s" % e.msg)
                source = None

        return source

    ###
    def lynx_get(self, url: str, get_json: bool = False) -> Union[Dict, List, str]:
        """
        """
        source = None

        if self._lynx is not None:
            args = [self._lynx, "--accept_all_cookies", "--source", url]
            output = subprocess.run(args, stdout=subprocess.PIPE).stdout
            try:
                source = output.decode("utf-8")
            except UnicodeDecodeError:
                return source

            if get_json:
                source = json.loads(source)

        return source
