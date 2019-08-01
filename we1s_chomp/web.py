"""Web browser wrapper.

Most websites either use SSL or attempt to block simple crawlers--bad news for
Python's programmatic HTTP request modules. We can (mostly) get around that by
using a Selenium Grid to control instances of Google Chrome.
Initialize the class by pointing it toward an active Selenium Grid hub. Use
Browser.get() to collect from one URL at a time or Browser.get_batch() to queue
up a larger collection task.

Todo:
- Implement some form of security for the Selenium containers and make sure the
    Browser class is made aware of it (i.e. basicauth or equivalent).
- Reinforce exception handling.
"""
import random
from logging import getLogger
from time import sleep  # noqa
from typing import Callable, Optional, Set, Tuple

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException

###############################################################################
# Internal configuration parameters.                                          #
###############################################################################


_DEFAULT_BROWSER_SLEEP = (1.0, 3.0)
"""Default tuple with minimum and maximum random sleep time, in seconds."""

_DEFAULT_BROWSER_TIMEOUT = 60.0
"""Default maximum time in seconds for the browser to await a response."""

_DEFAULT_BROWSER_TYPE = "chrome"
"""Default browser node type for which to ask Selenium hub."""

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
        browser_type: str = _DEFAULT_BROWSER_TYPE,
        timeout: float = _DEFAULT_BROWSER_TIMEOUT,
        sleep_range: Tuple[float, float] = _DEFAULT_BROWSER_SLEEP,
    ):
        """Create a new Browser instance.

        Args:
            hub_url: Raw Selenium Grid URL, with port number.
            timeout: Maximum time in seconds for the browser to await a
                response.
            sleep_range: Tuple with minimum and maximum random sleep time, in
                seconds.
        """
        self.hub_url = hub_url.rstrip("/")
        self.timeout = timeout
        self.sleep_range = sleep_range

    def is_grid_ready(self) -> bool:
        """Check if Selenium Grid is ready."""
        log = getLogger(__name__)

        try:
            response = requests.get(self.hub_url + _HUB_STATUS_URL_SUFFIX).json()

        except requests.RequestException as e:
            log.error("Error querying Selenium Grid status: %s" % e)
            return False

        return response.get("value", False).get("ready", False)

    def get(
        self,
        url: str,
        sleep_range: Optional[Tuple[float, float]] = None,
        is_expecting_json: bool = False,
    ) -> str:
        """Get page source from URL using Selenium Grid, None if error.

        Args:
            url: URL of page to get.
            sleep_range: Min. and max. time to sleep after request.

        Returns:
            Raw text content of the response, None if error.
        """
        log = getLogger(__name__)

        if not sleep_range:
            sleep_range = self.sleep_range

        if "http://" not in url and "https://" not in url:
            url = "http://" + url

        # Check grid status before we make a request.
        time_elapsed = 0.0
        while not self.is_grid_ready():
            time_elapsed += random_sleep(sleep_range)
            if time_elapsed > self.timeout:
                log.error("Browser timed out waiting for open grid slot.")
                return None

        try:
            driver = webdriver.Remote(
                command_executor=self.hub_url + _HUB_URL_SUFFIX,
                desired_capabilities={"browserName": "chrome"},
            )
            driver.get(url)
            response = (
                driver.find_element_by_tag_name("pre").text
                if is_expecting_json
                else driver.page_source
            )

        except (NoSuchElementException, WebDriverException) as e:
            log.info('Error while trying to get URL "%s": %s' % (url, e))
            response = None

        finally:
            random_sleep(sleep_range)
            driver.quit()

        return response


def get(
    url: str,
    sleep_range: Tuple[float, float] = _DEFAULT_BROWSER_SLEEP,
    is_expecting_json: bool = False,
) -> str:
    """Get page source from URL using the Requests module.

    N.b. some websites will attempt to block programmatic requests. Try Browser
    and Browser.get() or .get_batch() if you aren't getting good results.

    Args:
        url: URL of page to get.
        sleep_range: Min. and max. time to sleep after request.

    Returns:
        Raw text content of the response, None if error.
    """
    log = getLogger(__name__)

    if "http://" not in url and "https://" not in url:
        url = "http://" + url

    try:
        response = requests.get(url).text
        random_sleep(sleep_range)

    except requests.RequestException as e:
        log.info('Error while trying to get URL "%s": %s' % (url, e))
        return None

    return response


###############################################################################
# Helper functions for Browser class.                                         #
###############################################################################


def get_interface(browser: Optional[Browser] = None) -> Callable:
    """Switch collector interface."""
    if browser is not None and isinstance(browser, Browser):
        return browser.get
    return get


def is_url_ok(
    url: str, url_stops: Set[str] = {}, url_stopwords: Set[str] = {}
) -> bool:
    """Check URL against stop lists."""
    return not (
        url in url_stops or next((s for s in url_stopwords if s in url), False)
    )


def random_sleep(sleep_range: Tuple[float, float] = _DEFAULT_BROWSER_SLEEP) -> float:
    """Sleep for a random amount of time.

    This is useful for pausing occasionally between requests.

    Returns:
        Time slept, in seconds.
    """
    sleep_time = random.uniform(*sleep_range)
    sleep(sleep_time)
    return sleep_time
