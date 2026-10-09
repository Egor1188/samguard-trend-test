import os

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from pages.locators import LoginPageLocators, TrendPageLocators
from pages.login_page import LoginPage
from pages.trend_page import MAX_SECTIONS, Section, TrendPage

load_dotenv()
expect.set_options(timeout=15_000)  # the shared demo server is sometimes slow

DEFAULT_BASE_URL = "https://demo-3.client.samguard.co"
VIEWPORT = {"width": 1440, "height": 900}  # all four sections fit on screen


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": os.getenv("BASE_URL", DEFAULT_BASE_URL),
        "viewport": VIEWPORT,
        "record_video_size": VIEWPORT,
    }


@pytest.fixture(scope="session")
def credentials():
    username = os.getenv("SAMGUARD_USER", "demo@samguard.co")
    password = os.getenv("SAMGUARD_PASSWORD")
    if not password:
        pytest.skip("SAMGUARD_PASSWORD is not set: copy .env.example to .env and add the demo password")
    return username, password


@pytest.fixture
def trend_page(page: Page, credentials) -> TrendPage:
    """Logged-in user on Dashboard -> Trend. Each test logs in on its own (independent tests)."""
    LoginPage(page, LoginPageLocators.URL).login(*credentials)
    trend = TrendPage(page, TrendPageLocators.URL)
    trend.open()
    return trend


@pytest.fixture
def editable_section(trend_page: TrendPage):
    """A section that can take at least one more tag.

    The demo account is shared, so the fixture remembers the section's name and tags and
    puts them back after the test, whether the test passed or failed. If no section has a
    free tag slot, it creates one (and removes it again afterward).
    """
    section = trend_page.first_section_with_free_tag_slot()
    created_by_test = False
    if section is None:
        if trend_page.sections.count() >= MAX_SECTIONS:
            pytest.skip("All sections already have 5 tags and there is no free section slot")
        section = trend_page.add_section()
        created_by_test = True

    original_name = section.name()
    original_tags = section.tag_names()

    yield section

    trend_page.reload()  # start the clean-up from a fresh page (no open dropdowns)
    if created_by_test:
        trend_page.remove_section(section)
        return
    for tag in section.tag_names():
        if tag not in original_tags:
            section.remove_tag(tag)
    if section.name() != original_name:
        section.rename(original_name)
