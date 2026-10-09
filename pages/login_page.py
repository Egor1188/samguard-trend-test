import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.locators import LoginPageLocators


class LoginPage(BasePage):
    def login(self, username: str, password: str) -> None:
        self.open()
        self.page.locator(LoginPageLocators.USERNAME_INPUT).fill(username)
        self.page.locator(LoginPageLocators.PASSWORD_INPUT).fill(password)
        self.page.get_by_role("button", name=LoginPageLocators.LOGIN_BUTTON_NAME).click()
        # After a successful login the app leaves the login route (lands on Active Alerts).
        expect(self.page).not_to_have_url(re.compile(r"#/login"))
