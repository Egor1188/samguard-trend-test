# SAM GUARD Trend View – automated tests (Python + Playwright)

Two automated tests for **Dashboard → Trend (Section & Tag Management)**:

| Test | Manual case | What it proves |
|---|---|---|
| `test_tc33_section_name_and_tags_persist_after_refresh` | TC-33 (spec 2.4) | A renamed section and an added tag are saved. After a page refresh the section count, the new name and the exact tag list are unchanged. |
| `test_tc25_more_than_five_tags_is_blocked_with_error` | TC-25 + TC-26 (spec 2.3) | Selecting tags up to the limit is allowed. A 6th tag disables Confirm and shows "Maximum of 5 can be added". Exactly 5 tags are saved. "+" (Add Sensor) is then disabled with the tooltip "No additional tags can be added to this section". |

Both tests leave the shared demo data as they found it (see *Test data* below).

## Prerequisites
- Python **3.14**
- [Poetry](https://python-poetry.org/docs/#installation) 2.x
- Internet access to `https://demo-3.client.samguard.co`
- The demo credentials from the assignment document

## Install
Windows (PowerShell):
```powershell
poetry config virtualenvs.in-project true --local   # optional: keep the venv in .venv
poetry install
poetry run playwright install chromium
copy .env.example .env      # then open .env and set SAMGUARD_PASSWORD
```
macOS / Linux:
```bash
poetry install
poetry run playwright install chromium
cp .env.example .env        # then set SAMGUARD_PASSWORD in .env
```

## Run
```bash
poetry run pytest                  # headed (visible browser) by default, both tests (~1 min)
poetry run pytest --slowmo 300     # slowed down - use this for the screen recording
poetry run pytest -k tc25          # a single test
poetry run pytest -m smoke        # by marker
```

## Video and debugging output
- A **video of every test** is recorded automatically (`--video on` in `pyproject.toml`) to
  `test-results/<test-name>/video.webm`.
- For one continuous recording, run `poetry run pytest --slowmo 300` and record the screen (Windows: Win+Alt+R / Xbox Game Bar, or OBS).
- Failed tests also keep a screenshot and a Playwright trace: `poetry run playwright show-trace test-results/<test-name>/trace.zip`.

## Test data and assumptions
- **Shared account.** `demo@samguard.co` is shared and keeps one Trend configuration per user.
  - The tests pick the **first section that can take another tag**.
  - The fixture `editable_section` records its name and tags and **restores them in teardown**, also when a test fails.
  - If every section already has 5 tags, the fixture creates a section and removes it afterwards. If that is also impossible (4 full sections), the tests are skipped with a clear message.
- **Tags** from `data.py` (`FI8903`, `PI527`, `LI3606`, `TI4972`, `PI3901A`, `TI8325`, `LC81013`) must exist in the demo plant (they did on 09 Oct 2026).
- **Do not run in parallel** (e.g. `pytest -n`) and avoid editing Trend View manually while the tests run: both use the same account.
- **Navigation.** The Trend View is opened by URL (`/investigation/#/dashboard/trend`) after a UI login. From the app menu, the Dashboard opens in a new browser tab, and navigation is not what these tests check.
- **Synchronisation.** The tests wait for the app's own REST calls (`GET/PUT/POST/DELETE …/investigation/trend(s)`) and use Playwright's auto-waiting assertions. There are no fixed sleeps.

## Project structure
```
pages/base_page.py       BasePage: url, default timeout, open/reload, wait_until helper
pages/locators.py        CSS locators grouped per page / component
pages/login_page.py      LoginPage
pages/trend_page.py      TrendPage, Section and TagPicker page objects + API wait helpers
data.py                  tag pool, unique valid section names
conftest.py              browser/context settings, credentials, login, editable_section (snapshot + restore)
test_trend_view.py       TestTrendView: the two tests
pyproject.toml           Poetry dependencies + pytest options (browser, video, trace, markers)
```
## Known application issues (not covered by these tests)
BUG-01 ("Add" creates an empty section without a popup), BUG-02 (last tag removable) and BUG-03 (name rules not enforced) are described in `../3_Bug_Reports.md`. `TrendPage.add_section()` currently relies on the BUG-01 behaviour. When the configuration popup is implemented, that helper has to fill in the popup.

## If a locator breaks
The app has no `data-testid` attributes, so all locators are CSS classes of the Angular components, grouped at the top of each page-object class. Use `poetry run playwright codegen https://demo-3.client.samguard.co/admin-ui/#/login` to inspect the current DOM.
