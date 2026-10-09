"""Trend View - Section & Tag Management.

TC-33  Name and tag changes persist after a page refresh            (spec 2.4)
TC-25  More than 5 tags is blocked with an error message (+ TC-26)  (spec 2.3)
"""
import pytest

from data import pick_tags, unique_section_name
from pages.trend_page import MAX_TAGS, Section, TrendPage


@pytest.mark.trend_test
class TestTrendView:

    @pytest.mark.smoke
    def test_tc33_section_name_and_tags_persist_after_refresh(
        self, trend_page: TrendPage, editable_section: Section
    ):
        section = editable_section
        sections_before = trend_page.sections.count()
        original_tags = section.tag_names()
        new_name = unique_section_name()
        [new_tag] = pick_tags(exclude=original_tags, count=1)

        section.rename(new_name)
        section.add_tags([new_tag])
        trend_page.reload()

        trend_page.check_sections_count(sections_before)
        trend_page.check_section_is_saved(new_name, original_tags + [new_tag])

    @pytest.mark.smoke
    def test_tc25_more_than_five_tags_is_blocked_with_error(
        self, trend_page: TrendPage, editable_section: Section
    ):
        section = editable_section
        existing_tags = section.tag_names()
        free_slots = MAX_TAGS - len(existing_tags)
        *tags_up_to_limit, extra_tag = pick_tags(exclude=existing_tags, count=free_slots + 1)

        picker = section.open_tag_picker()
        picker.select_tags(tags_up_to_limit)
        picker.check_confirm_is_enabled(selected_count=free_slots)

        picker.select(extra_tag)
        picker.check_limit_error_is_shown("Maximum of 5 can be added")

        picker.unselect(extra_tag)
        picker.check_confirm_is_enabled()
        saved_tags = picker.confirm()
        section.check_saved_tags_are_limited(saved_tags, extra_tag)

        # TC-26: with 5 tags, "+" (Add Sensor) is disabled and explains why
        section.check_add_tag_is_blocked("No additional tags can be added to this section")
