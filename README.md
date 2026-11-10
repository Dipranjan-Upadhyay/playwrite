# Hybrid Test Automation Framework (Python · Playwright · Pytest)

A single Pytest framework that covers **UI tests** (Playwright, Page Object Model) and
**REST API tests** (Requests, service objects). It also includes data-driven tests,
cross-browser and parallel runs, security tests, JSON schema validation, GitHub Actions CI
and Allure reporting.

| Layer | System under test |
|---|---|
| UI | [SauceDemo](https://www.saucedemo.com), a public e-commerce practice site |
| API | [Restful-Booker](https://restful-booker.herokuapp.com), a public REST API with token auth |

Both targets can be overridden with environment variables (see `config/settings.py`).

## Project layout

```
config/settings.py          env-driven configuration
pages/                      Page Object Model (BasePage, LoginPage, InventoryPage, Cart/Checkout)
api/client.py               requests.Session wrapper that logs each call to Allure
api/booking_api.py          API service object (endpoints + auth handling)
schemas/*.json              JSON Schemas (draft-07, cross-file $ref)
utils/schema_validator.py   schema assertion with readable errors
utils/data_loader.py        JSON test data turned into pytest.param objects
test_data/*.json            data for data-driven tests
conftest.py                 shared fixtures (api client, auth token, booking setup and teardown)
tests/ui/conftest.py        page-object fixtures and a screenshot on failure
tests/ui/                   login, security, inventory and checkout tests
tests/api/                  CRUD, auth/authorization and input-validation tests
scripts/report_summary.py   pass-rate and failure metrics (Markdown) from Allure results
allure/categories.json      failure classification shown in the Allure report
.github/workflows/          CI pipeline
```

## Features and where they live

| Feature | Implementation |
|---|---|
| Page Object Model | `pages/`. Tests never touch raw selectors. |
| Reusable fixtures | `conftest.py`: session-scoped `api_client` and `auth_token`; `created_booking` cleans up after itself; page fixtures |
| Data-driven tests | `@pytest.mark.parametrize` fed from `test_data/*.json` via `as_params()` |
| Cross-browser | pytest-playwright `--browser chromium/firefox/webkit`; CI runs a 3-browser matrix |
| Parallel runs | pytest-xdist `-n auto` |
| Security tests | invalid and expired-style tokens, missing auth, bad Basic auth, bad credentials, protected pages without login, session ending on logout, SQLi/XSS input, masked password field |
| Input validation | missing required fields, malformed JSON, invalid IDs, injection strings stored only as literal text |
| JSON schema validation | `assert_matches_schema(body, "booking.json")` with date-format checks and `additionalProperties: false` |
| CI | runs on every push and PR, plus a weekday nightly run |
| Reporting | Allure report with trend history, environment info, failure categories, screenshots, request/response logs. Published to GitHub Pages. Pass rate and failures written to the job summary. |

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium firefox webkit

pytest                                   # everything (UI on chromium)
pytest -m api -n 4                       # API suite in parallel
pytest -m "ui and smoke" --headed        # watch the UI smoke tests
pytest -m security                       # security tests only
pytest tests/ui --browser chromium --browser firefox --browser webkit -n auto   # cross-browser

# Reports
allure serve allure-results              # needs the Allure CLI (scoop install allure / npm i -g allure-commandline)
python scripts/report_summary.py allure-results
```

Markers: `ui`, `api`, `security`, `smoke`, `regression`, `schema`.

## CI/CD (GitHub Actions)

`.github/workflows/regression.yml` runs these jobs:
1. **api-tests**: the API suite, run in parallel with one retry for flaky tests.
2. **ui-tests**: a matrix over Chromium, Firefox and WebKit. Each runs in parallel and keeps a Playwright trace and video for failed tests.
3. **report**: merges all results, restores Allure history for trend charts, and generates the report. It writes pass rate, per-feature breakdown, failures and flaky tests to the job summary, and fails the run if the pass rate drops below 90%. It publishes the report to GitHub Pages (`main` branch only).

To enable publishing: push to GitHub, then go to **Settings → Pages → Deploy from branch → `gh-pages`**.
The report then appears at `https://<user>.github.io/<repo>/`.

## Known issue tracked in the suite

Restful-Booker answers `500` instead of `400` for invalid payloads. `test_missing_field_returns_client_error`
is marked `xfail`, so the defect is visible in reports without failing the build. It shows up
under *Known issues* in the Allure categories.
