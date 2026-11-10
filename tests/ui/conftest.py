"""UI fixtures. `page`, `browser` and `--browser` come from pytest-playwright."""
import allure
import pytest

from pages.checkout_page import CartPage, CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1366, "height": 768}}


@pytest.fixture
def login_page(page, settings):
    return LoginPage(page, settings.ui_base_url).open()


@pytest.fixture
def inventory_page(login_page, page, settings):
    """Logged-in starting point for tests that are not about login itself."""
    login_page.login("standard_user", settings.ui_password)
    inventory = InventoryPage(page, settings.ui_base_url)
    inventory.page_title.wait_for()
    return inventory


@pytest.fixture
def cart_page(page, settings):
    return CartPage(page, settings.ui_base_url)


@pytest.fixture
def checkout_page(page, settings):
    return CheckoutPage(page, settings.ui_base_url)


# ---------------- screenshot on failure ----------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Runs right after the test body, before fixtures (and the page) are torn down."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page = item.funcargs.get("page")
    if page is None:
        return
    try:
        allure.attach(
            page.screenshot(full_page=True),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(page.url, name="failure-url", attachment_type=allure.attachment_type.TEXT)
    except Exception:  # page may already be closed
        pass
