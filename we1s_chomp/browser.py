# -*- coding: utf-8 -*-

"""Web browser wrapper.

Most websites either use SSL or attempt to block simple crawlers--bad news for
Python's programmatic HTTP request modules. We can (mostly) get around that by
using a Selenium Grid to control instances of Google Chrome.

Initialize the class by pointing it toward an active Selenium Grid hub. Use
Browser.get() to collect from one URL at a time or Browser.get_batch() to queue
up a larger collection task.

Todo:
    - Implement some form of security for the Selenium containers and make sure
        the Browser class is made aware of it (i.e. basicauth or equivalent).
    - Reinforce exception handling.
"""

import random
import time
from concurrent import futures
from logging import getLogger
from typing import Callable, List, Optional, Set, Tuple

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


###############################################################################
# Internal configuration parameters.                                          #
###############################################################################


_DEFAULT_BROWSER_TIMEOUT = 60.0
"""Default maximum time in seconds for the browser to await a response."""

_DEFAULT_BROWSER_SLEEP = (1.0, 3.0)
"""Default tuple with minimum and maximum random sleep time, in seconds."""

_DEFAULT_NUM_BATCH_WORKERS = 1
"""Default number of worker threads to use for batch collection."""

_HUB_URL_SUFFIX = "/wd/hub"
"""Suffix for Grid URL to get at JSON control interface."""

_HUB_STATUS_URL_SUFFIX = "/wd/hub/status"
"""Suffix for Grid URL to get at status report JSON."""


###############################################################################
# Browser class.                                                              #
###############################################################################


class Browser:
    """Web browser wrapper.

    Most websites either use SSL or attempt to block simple crawlers--bad news
    for Python's programmatic HTTP request modules. We can (mostly) get around
    that by using Selenium to control an actual copy of Chrome.
    """

    def __init__(
        self,
        hub_url: str,
        timeout: float = _DEFAULT_BROWSER_TIMEOUT,
        sleep_time: Tuple[float, float] = _DEFAULT_BROWSER_SLEEP,
    ):
        """Create a new Browser instance.

        Args:
            - hub_url: Raw Selenium Grid URL, with port number.
            - timeout: Maximum time in seconds for the browser to await a
                response.
            - sleep_time: Tuple with minimum and maximum random sleep time, in
                seconds.
        """
        self.hub_url = hub_url.rstrip("/")
        self.timeout = timeout
        self.sleep_time = sleep_time

    def is_grid_ready(self) -> bool:
        """Check if Selenium Grid is ready.

        Returns:
            True if ready, False if not ready.
        """
        log = getLogger(__name__)

        try:
            response = requests.get(self.hub_url + _HUB_STATUS_URL_SUFFIX).json()

        except requests.RequestException as e:
            log.error("Error querying Selenium Grid status: %s" % e.msg)
            response = False

        return response.get("value", False).get("ready", False)

    def get(self, url: str) -> Optional[str]:
        """Get page source from URL using Selenium Grid.

        Args:
            - url: URL of page to get.

        Returns:
            Raw text content of the response, None if error.
        """
        log = getLogger(__name__)

        # Check grid status before we make a request.
        time_elapsed = 0.0
        while not self.is_grid_ready():
            time_elapsed += sleep(self.sleep_time)
            if time_elapsed > self.timeout:
                log.error("Browser timed out waiting for open grid slot.")
                return None

        try:
            driver = webdriver.Remote(
                command_executor=self.hub_url + _HUB_URL_SUFFIX,
                desired_capabilities={"browserName": "chrome"},
            )
            driver.get(url)
            response = driver.page_source
            sleep(self.sleep_time)

        except WebDriverException as e:
            log.error('Error while trying to get URL "%s": %s' % (url, e.msg))
            response = None

        finally:
            driver.quit()

        return response

    def get_batch(
        self, urls: List[str], num_workers: int = _DEFAULT_NUM_BATCH_WORKERS
    ) -> Optional[List[Tuple[str, str]]]:
        """Get a batch of responses using Selenium Grid.

        Args:
            - urls: List of URLs get pages from.
            - num_workers: Threads to use. This should not exceed the number of
                nodes in the grid.

        Returns:
            List of tuples pairing the URLs and with their raw text responses,
            or None if error.
        """
        log = getLogger(__name__)

        responses = []

        try:
            with futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                future_to_url = {executor.submit(self.get, url): url for url in urls}
                for future in futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    response = url, future.result()
                    responses.append(response)

        except futures.TimeoutError or futures.CancelledError as e:
            log.error("Batch error: %s. Try using Browser.get()." % e.msg)
            return None

        return responses


###############################################################################
# Helper functions for Browser class.                                         #
###############################################################################


def sleep(sleep_time: Tuple[float, float] = _DEFAULT_BROWSER_SLEEP) -> float:
    """Sleep for a random amount of time.

    This is useful for pausing occasionally between requests.

    Returns:
        Time slept, in seconds.
    """
    sleep_time = random.uniform(*sleep_time)
    time.sleep(sleep_time)
    return sleep_time


def get(
    url: str, sleep_time: Tuple[float, float] = _DEFAULT_BROWSER_SLEEP
) -> Optional[str]:
    """Get page source from URL using the Requests module.

    N.b. some websites will attempt to block programmatic requests. Try Browser
    and Browser.get() or .get_batch() if you aren't getting good results.

    Args:
        - url: URL of page to get.

    Returns:
        Raw text content of the response, None if error.
    """
    log = getLogger(__name__)

    try:
        response = requests.get(url).text
        sleep(sleep_time)

    except requests.RequestException as e:
        log.error('Error while trying to get URL "%s": %s' % (url, e.msg))
        return None

    return response


def get_interface(browser: Optional[Browser] = None) -> Callable:
    """Switch collector interface."""
    if browser is not None and isinstance(browser, Browser):
        return browser.get
    return get


def is_url_ok(
    url: str, url_stops: Set[str] = {}, url_stop_words: Set[str] = {}
) -> bool:
    """Check URL against stop lists."""
    return not (
        url in url_stops or next([s for s in url_stop_words if s in url], False)
    )
