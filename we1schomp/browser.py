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
    that by using Selenium to control an actual copy of Chrome.
    """

    ###
    def __init__(
        self,
        selenium_url: str,
        wait_time: Tuple[float, float] = (1.0, 3.0),
    ):
        """Create a new Browser instance."""
        self._log = getLogger(__name__)

        self.wait_time = wait_time
        self._driver = webdriver.Remote(
            command_executor=selenium_url,
            desired_capabilities={"browserName": "chrome"}
        )

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
    
        self._driver.get(url)

        if get_json:
            source = self._driver.find_element_by_tag_name("pre").text
            source = json.loads(source)
        else:
            self.stop()
            source = str(self._driver.page_source)

        sleep(randfloat(*self.wait_time))

        return source
