# Локаторы — CSS-селекторы (строки). Приложение не имеет data-testid, поэтому используются
# CSS-классы Angular-компонентов, взятые из живого DOM demo-3.


class LoginPageLocators:
    URL = "/admin-ui/#/login"
    USERNAME_INPUT = "#email"  # "Business e-mail / User name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON_NAME = "LOGIN"  # accessible name of the button (get_by_role)


class TrendPageLocators:
    URL = "/investigation/#/dashboard/trend"
    SECTIONS = ".dashboard-trend"
    ADD_SECTION_BUTTON = "button.dashboard-trends__add-btn"
    REMOVE_DIALOG = "mat-dialog-container"
    REMOVE_DIALOG_CONFIRM = ".confirm-container"
    TOOLTIP = ".mat-mdc-tooltip-surface"


class SectionLocators:
    NAME_INPUT = "input.dashboard-trend__title-input"
    # The first tag is shown as a chip, the others are collapsed into a "(+N)" chip.
    TAG_CHIPS = "mat-chip:not(.dashboard-trend__overflow-chip)"
    OVERFLOW_CHIP = "mat-chip.dashboard-trend__overflow-chip"
    OVERFLOW_LIST = ".dashboard-trend__overflow-dropdown"
    OVERFLOW_ITEM = ".overflow-dropdown__item"
    OVERFLOW_ITEM_LABEL = ".overflow-dropdown__item-label"
    OVERFLOW_ITEM_REMOVE = "button.overflow-dropdown__item-remove"
    ADD_TAG_BUTTON = "button.dashboard-trend__add-tag-btn"
    # The tooltip of "+" lives on a wrapper <span>, so it also works while "+" is disabled.
    ADD_TAG_HINT_TRIGGER = "span.mat-mdc-tooltip-trigger:has(button.dashboard-trend__add-tag-btn)"
    REMOVE_BUTTON = "button:has(mat-icon.delete-btn)"
    TAG_PICKER = ".dashboard-trend__tag-dropdown"
    CHIP_REMOVE_BUTTON = "button.mat-mdc-chip-remove"


class TagPickerLocators:
    SEARCH_INPUT = 'input[placeholder="Add tag"]'
    OPTIONS = ".answer-container"
    OPTION_NAME = ".tag-name"
    OPTION_CHECKBOX = "input[type=checkbox]"
    CONFIRM_BUTTON = "button.search-tag-actions__button--confirm"
    CANCEL_BUTTON = "button.search-tag-actions__button--cancel"
    LIMIT_ALERT = "mat-icon.search-tag-actions__alert"
