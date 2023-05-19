"""
Selenium tools
"""

import contextlib

import click
from RPA.Browser import Selenium
from selenium.webdriver.common.by import By

from .exceptions import WayFailed


class SeleniumWrapMixin:
    """Useful tools for selenium"""

    br: Selenium

    @contextlib.contextmanager
    def wait_driver_to_change_url(self) -> None:
        """Use this if you expect driver to change its url."""
        total_wait_time, tick = 60, 0.1
        url = self.br.driver.current_url
        yield
        for _ in range(int(total_wait_time / tick)):
            if url != self.br.driver.current_url:
                break
            self.br.driver.implicitly_wait(tick)

    def open_webpage(self, url: str) -> None:
        """
        Browser page managing.
        Args:
            url: url to open
        """
        if not self.br.get_browser_ids():
            self.br.open_available_browser()
        self.br.go_to(url)

    def assert_page_correctness(self, scientist: str) -> None:
        """
        Assert, whether tha page is one that user needs.
        Args:
            scientist: scientist name
        Raises:
            WayFailed if assertion fails
        """
        if self.br.does_page_contain("Wikipedia does not have an article with this exact name."):
            raise WayFailed
        element = self.br.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/main/header/h1/span")  # page name
        if scientist not in element.text:
            if click.prompt(f'Are you looking for this web page "{element.text}"?', type=bool, default="n"):
                return
            raise WayFailed
