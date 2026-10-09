"""Page objects for SAM GUARD -> Dashboard -> Trend (Section & Tag Management).

Every action that changes data waits for the matching API call instead of sleeping:
    GET    /vp_server/dae/rest/investigation/trends?userIds=...   load the user's sections
    POST   /vp_server/dae/rest/investigation/trend                create a section
    PUT    /vp_server/dae/rest/investigation/trend                update name / tags / period
    DELETE /vp_server/dae/rest/investigation/trends?trendIds=...  remove a section
"""
from __future__ import annotations

import re
from typing import Callable, List, Optional, Sequence

from playwright.sync_api import Locator, Page, Response, expect

from pages.base_page import BasePage
from pages.locators import SectionLocators, TagPickerLocators, TrendPageLocators

TRENDS_API = "/vp_server/dae/rest/investigation/trends"
TREND_API = "/vp_server/dae/rest/investigation/trend"
MAX_SECTIONS = 4
MAX_TAGS = 5


def api_call(method: str, path: str) -> Callable[[Response], bool]:
    """Predicate for page.expect_response(): HTTP method + exact API path (query ignored)."""

    def matches(response: Response) -> bool:
        return response.request.method == method and response.url.split("?")[0].endswith(path)

    return matches


class TagPicker:
    """Dropdown opened by the '+' (Add Sensor) button: search, multi-select, Cancel / Confirm (N)."""

    def __init__(self, page: Page, root: Locator):
        self.page = page
        self.root = root
        self.search_input = root.locator(TagPickerLocators.SEARCH_INPUT)
        self.options = root.locator(TagPickerLocators.OPTIONS)
        self.confirm_button = root.locator(TagPickerLocators.CONFIRM_BUTTON)
        self.cancel_button = root.locator(TagPickerLocators.CANCEL_BUTTON)
        self.limit_alert = root.locator(TagPickerLocators.LIMIT_ALERT)

    def option(self, tag: str) -> Locator:
        """Search result whose tag name is exactly `tag` ('FI8903' must not match 'FI8903A')."""
        exact_name = re.compile(rf"^\s*{re.escape(tag)}\s*$")
        return self.options.filter(
            has=self.page.locator(TagPickerLocators.OPTION_NAME, has_text=exact_name)
        )

    def _click_option(self, tag: str) -> Locator:
        option = self.option(tag)
        if not option.is_visible():
            self.search_input.fill(tag)  # search needs at least 3 characters
        option.locator(TagPickerLocators.OPTION_NAME).click()
        return option

    def select(self, tag: str) -> None:
        option = self._click_option(tag)
        expect(option.locator(TagPickerLocators.OPTION_CHECKBOX)).to_be_checked()

    def unselect(self, tag: str) -> None:
        option = self._click_option(tag)
        expect(option.locator(TagPickerLocators.OPTION_CHECKBOX)).not_to_be_checked()

    def select_tags(self, tags: Sequence[str]) -> None:
        for tag in tags:
            self.select(tag)

    def hover_limit_alert(self) -> None:
        """The tag-limit error text is shown as a tooltip of the alert icon."""
        self.limit_alert.hover()

    def check_confirm_is_enabled(self, selected_count: Optional[int] = None) -> None:
        """Confirm is enabled; with `selected_count` it also shows "(N)" and no limit alert."""
        expect(self.confirm_button).to_be_enabled()
        if selected_count is not None:
            expect(self.confirm_button).to_contain_text(f"({selected_count})")
            expect(self.limit_alert).to_be_hidden()

    def check_limit_error_is_shown(self, message: str) -> None:
        """Over the tag limit: Confirm is blocked and the alert icon explains why."""
        expect(self.confirm_button).to_be_disabled()
        expect(self.limit_alert).to_be_visible()
        self.hover_limit_alert()
        tooltip = self.page.locator(TrendPageLocators.TOOLTIP).filter(has_text=message)
        expect(tooltip).to_be_visible()

    def confirm(self) -> List[str]:
        """Click Confirm, wait until the section is saved and return the saved tag names."""
        with self.page.expect_response(api_call("PUT", TREND_API)) as saved:
            self.confirm_button.click()
        response = saved.value
        assert response.ok, f"Saving tags failed: HTTP {response.status}"
        expect(self.root).to_be_hidden()
        return [column["name"] for column in response.json()["data"]["columns"]]


class Section:
    """One trend section (card) in the Trend View."""

    def __init__(self, page: Page, root: Locator):
        self.page = page
        self.root = root
        self.name_input = root.locator(SectionLocators.NAME_INPUT)
        self.tag_chips = root.locator(SectionLocators.TAG_CHIPS)
        self.overflow_chip = root.locator(SectionLocators.OVERFLOW_CHIP)
        self.overflow_list = root.locator(SectionLocators.OVERFLOW_LIST)
        self.add_tag_button = root.locator(SectionLocators.ADD_TAG_BUTTON)
        self.add_tag_hint_trigger = root.locator(SectionLocators.ADD_TAG_HINT_TRIGGER)
        self.remove_button = root.locator(SectionLocators.REMOVE_BUTTON)

    # ---------- name ----------
    def name(self) -> str:
        return self.name_input.input_value()

    def rename(self, new_name: str) -> None:
        """Type a new name and leave the field; the app saves the name on blur."""
        with self.page.expect_response(api_call("PUT", TREND_API)) as saved:
            self.name_input.fill(new_name)
            self.name_input.press("Tab")
        response = saved.value
        assert response.ok, f"Saving the name failed: HTTP {response.status}"
        assert response.json()["data"]["sectionName"] == new_name

    # ---------- tags ----------
    def tag_count(self) -> int:
        count = self.tag_chips.count()
        if self.overflow_chip.count():
            count += int(re.search(r"\d+", self.overflow_chip.inner_text()).group())
        return count

    def expect_tag_count(self, expected: int) -> None:
        BasePage.wait_until(
            lambda: self.tag_count() == expected,
            message=lambda: f"Expected {expected} tags in the section, found {self.tag_count()}",
        )

    def tag_names(self) -> List[str]:
        """All tag names of the section, including those hidden behind "(+N)"."""
        names = [chip.get_attribute("title") for chip in self.tag_chips.all()]
        if self.overflow_chip.count():
            self.overflow_chip.click()
            expect(self.overflow_list).to_be_visible()
            labels = self.overflow_list.locator(SectionLocators.OVERFLOW_ITEM_LABEL)
            names += [label.get_attribute("title") for label in labels.all()]
            self.overflow_chip.click()  # the chip toggles the list
            expect(self.overflow_list).to_be_hidden()
        return names

    def open_tag_picker(self) -> TagPicker:
        self.add_tag_button.click()
        picker = TagPicker(self.page, self.root.locator(SectionLocators.TAG_PICKER))
        expect(picker.search_input).to_be_visible()
        return picker

    def add_tags(self, tags: Sequence[str]) -> List[str]:
        """Add tags through the picker; returns the tag names saved by the server."""
        picker = self.open_tag_picker()
        picker.select_tags(tags)
        saved_tags = picker.confirm()
        missing = [tag for tag in tags if tag not in saved_tags]
        assert not missing, f"{missing} were not part of the saved section: {saved_tags}"
        return saved_tags

    def remove_tag(self, tag: str) -> None:
        """Click X next to a tag (directly on the chip or inside the "(+N)" list)."""
        chip = self.root.locator(f'mat-chip[title="{tag}"]')
        with self.page.expect_response(api_call("PUT", TREND_API)) as saved:
            if chip.count():
                chip.locator(SectionLocators.CHIP_REMOVE_BUTTON).click()
            else:
                self.overflow_chip.click()
                item = self.overflow_list.locator(SectionLocators.OVERFLOW_ITEM).filter(
                    has=self.page.locator(f'{SectionLocators.OVERFLOW_ITEM_LABEL}[title="{tag}"]')
                )
                item.locator(SectionLocators.OVERFLOW_ITEM_REMOVE).click()
        assert saved.value.ok, f"Removing tag {tag} failed: HTTP {saved.value.status}"

    def hover_add_tag_button(self) -> None:
        self.add_tag_hint_trigger.hover()

    def check_saved_tags_are_limited(self, saved_tags: Sequence[str], rejected_tag: str) -> None:
        """Exactly MAX_TAGS tags were saved and the tag over the limit is not among them."""
        assert len(saved_tags) == MAX_TAGS, f"Expected {MAX_TAGS} saved tags, got {saved_tags}"
        assert rejected_tag not in saved_tags, f"{rejected_tag} must not be saved: {saved_tags}"

    def check_add_tag_is_blocked(self, hint: str) -> None:
        """At the tag limit "+" is disabled and its tooltip explains why."""
        self.expect_tag_count(MAX_TAGS)
        expect(self.add_tag_button).to_be_disabled()
        self.hover_add_tag_button()
        tooltip = self.page.locator(TrendPageLocators.TOOLTIP).filter(has_text=hint)
        expect(tooltip).to_be_visible()


class TrendPage(BasePage):
    def __init__(self, page: Page, url: str = TrendPageLocators.URL, timeout: int = 20):
        super().__init__(page, url, timeout)
        self.sections = page.locator(TrendPageLocators.SECTIONS)
        self.add_section_button = page.locator(TrendPageLocators.ADD_SECTION_BUTTON)
        self.remove_dialog = page.locator(TrendPageLocators.REMOVE_DIALOG)

    # ---------- navigation ----------
    def open(self) -> None:
        # Opened by URL: from the app menu the Dashboard opens in a new browser tab, and
        # navigation is not the subject of these tests.
        self._load(lambda: self.page.goto(self.url))

    def reload(self) -> None:
        self._load(self.page.reload)

    def _load(self, navigate: Callable[[], object]) -> None:
        with self.page.expect_response(api_call("GET", TRENDS_API)) as loaded:
            navigate()
        response = loaded.value
        assert response.ok, f"Loading the trend sections failed: HTTP {response.status}"
        saved_sections = response.json()["data"]
        expect(self.sections).to_have_count(len(saved_sections))
        expect(self.add_section_button).to_be_visible()
        # A cursor left over a hint trigger would show its tooltip again and cover other controls.
        self.page.mouse.move(0, 0)

    def check_sections_count(self, expected: int) -> None:
        expect(self.sections).to_have_count(expected)

    def check_section_is_saved(self, name: str, expected_tags: Sequence[str]) -> None:
        """A section with `name` exists and holds exactly `expected_tags`."""
        section = self.section_named(name)
        assert section is not None, f"Section '{name}' is missing"
        expect(section.name_input).to_have_value(name)
        assert sorted(section.tag_names()) == sorted(expected_tags)

    # ---------- sections ----------
    def section(self, index: int) -> Section:
        return Section(self.page, self.sections.nth(index))

    def all_sections(self) -> List[Section]:
        return [self.section(i) for i in range(self.sections.count())]

    def section_named(self, name: str) -> Optional[Section]:
        return next((s for s in self.all_sections() if s.name() == name), None)

    def first_section_with_free_tag_slot(self) -> Optional[Section]:
        return next((s for s in self.all_sections() if s.add_tag_button.is_enabled()), None)

    def add_section(self) -> Section:
        """Click Add. NOTE: today this creates an empty "Section N" at once (BUG-01).
        When the configuration popup is implemented, fill it here."""
        before = self.sections.count()
        with self.page.expect_response(api_call("POST", TREND_API)) as created:
            self.add_section_button.click()
        assert created.value.ok, f"Creating a section failed: HTTP {created.value.status}"
        expect(self.sections).to_have_count(before + 1)
        return self.section(before)

    def remove_section(self, section: Section) -> None:
        before = self.sections.count()
        section.remove_button.click()
        expect(self.remove_dialog).to_contain_text("Remove this section from your view?")
        with self.page.expect_response(api_call("DELETE", TRENDS_API)) as deleted:
            self.remove_dialog.locator(TrendPageLocators.REMOVE_DIALOG_CONFIRM).get_by_text(
                "Yes", exact=True
            ).click()
        assert deleted.value.ok, f"Removing the section failed: HTTP {deleted.value.status}"
        expect(self.sections).to_have_count(before - 1)
