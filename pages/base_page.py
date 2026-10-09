import time
from typing import Callable, Union

from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, url: str, timeout: int = 20):
        self.page = page
        self.url = url
        # тайм-аут по умолчанию для ожиданий (в секундах)
        self.timeout = timeout
        self.page.set_default_timeout(timeout * 1000)

    def open(self):
        self.page.goto(self.url)

    def reload(self):
        self.page.reload()

    @staticmethod
    def wait_until(
        condition: Callable[[], bool],
        timeout: float = 10.0,
        interval: float = 0.25,
        message: Union[str, Callable[[], str]] = "Condition was not met in time",
    ) -> None:
        """Poll `condition` until it is true (for values that Playwright's expect() cannot poll)."""
        deadline = time.monotonic() + timeout
        while not condition():
            if time.monotonic() >= deadline:
                raise AssertionError(message() if callable(message) else message)
            time.sleep(interval)
