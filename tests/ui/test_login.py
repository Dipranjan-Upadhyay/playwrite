import allure
import pytest
from playwright.sync_api import expect

from pages.inventory_page import InventoryPage
from utils.data_loader import as_params

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.feature("UI - Authentication")
class TestLogin:
    @pytest.mark.smoke
    @pytest.mark.parametrize("user", as_params("ui_users.json", "valid_users"))
    def test_valid_user_can_log_in(self, login_page, page, settings, user):
        login_page.login(user["username"], settings.ui_password)
        inventory = InventoryPage(page, settings.ui_base_url)
        expect(page).to_have_url(inventory.url)
        expect(inventory.page_title).to_have_text("Products")
        expect(inventory.items).to_have_count(6)

    @pytest.mark.parametrize("case", as_params("ui_users.json", "invalid_logins"))
    def test_invalid_login_shows_error(self, login_page, page, case):
        login_page.login(case["username"], case["password"])
        expect(login_page.error_message).to_contain_text(case["error"])
        expect(page).to_have_url(login_page.url)


@allure.feature("UI - Security")
@pytest.mark.security
class TestLoginSecurity:
    @pytest.mark.parametrize("payload", as_params("ui_users.json", "malicious_inputs"))
    @pytest.mark.parametrize("field", ["username", "password"])
    def test_malicious_input_is_rejected_and_not_executed(
        self, login_page, page, settings, field, payload
    ):
        username = payload["value"] if field == "username" else "standard_user"
        password = payload["value"] if field == "password" else "wrong_password"
        login_page.login(username, password)

        expect(login_page.error_message).to_be_visible()
        expect(page).to_have_url(login_page.url)  # no auth bypass
        assert page.evaluate("window.__xss") is None, "Injected script was executed"

    @pytest.mark.smoke
    @pytest.mark.parametrize("path", ["/inventory.html", "/cart.html", "/checkout-step-one.html"])
    def test_protected_pages_require_login(self, page, settings, path):
        page.goto(f"{settings.ui_base_url}{path}")
        error = page.locator('[data-test="error"]')
        expect(error).to_contain_text("You can only access")
        expect(error).to_contain_text("when you are logged in")

    def test_session_is_invalidated_after_logout(self, inventory_page, page, settings):
        inventory_page.logout()
        page.goto(inventory_page.url)
        expect(page.locator('[data-test="error"]')).to_contain_text("when you are logged in")

    def test_password_field_is_masked(self, login_page):
        expect(login_page.password_input).to_have_attribute("type", "password")
