import allure
from playwright.sync_api import Page


class BasePage:
    """Shared behaviour for all page objects."""

    path = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.path}"

    def open(self):
        with allure.step(f"Open {self.__class__.__name__} ({self.path})"):
            self.page.goto(self.url)
        return self

    def title(self) -> str:
        return self.page.title()
