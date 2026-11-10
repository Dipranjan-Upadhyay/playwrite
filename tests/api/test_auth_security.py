"""Authentication, invalid-token and unauthorized-access tests."""
import base64

import allure
import pytest

from utils.data_loader import as_params
from utils.schema_validator import assert_matches_schema

pytestmark = [pytest.mark.api, pytest.mark.security, pytest.mark.regression]


def basic_auth(user: str, password: str) -> dict:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@allure.feature("API - Authentication")
class TestAuthentication:
    @pytest.mark.smoke
    @pytest.mark.schema
    def test_valid_credentials_return_token(self, booking_api, settings):
        response = booking_api.create_token(settings.api_username, settings.api_password)
        assert response.status_code == 200
        assert_matches_schema(response.json(), "auth_token.json")

    def test_each_login_issues_a_new_token(self, booking_api, settings):
        first = booking_api.create_token(settings.api_username, settings.api_password).json()
        second = booking_api.create_token(settings.api_username, settings.api_password).json()
        assert first["token"] != second["token"]

    @pytest.mark.parametrize("case", as_params("bookings.json", "invalid_credentials"))
    def test_invalid_credentials_do_not_return_token(self, booking_api, case):
        response = booking_api.create_token(case["username"], case["password"])
        body = response.json()
        assert "token" not in body
        assert body.get("reason") == "Bad credentials"

    def test_password_not_echoed_in_response(self, booking_api, settings):
        response = booking_api.create_token(settings.api_username, "wrong-secret-xyz")
        assert "wrong-secret-xyz" not in response.text


@allure.feature("API - Authorization")
class TestUnauthorizedAccess:
    @pytest.mark.smoke
    def test_update_without_token_is_forbidden(self, booking_api, created_booking):
        response = booking_api.update_booking(created_booking["id"], created_booking["payload"])
        assert response.status_code == 403

    def test_partial_update_without_token_is_forbidden(self, booking_api, created_booking):
        response = booking_api.partial_update_booking(created_booking["id"], {"firstname": "Hacker"})
        assert response.status_code == 403
        # the record must be unchanged
        assert booking_api.get_booking(created_booking["id"]).json() == created_booking["payload"]

    def test_delete_without_token_is_forbidden(self, booking_api, created_booking):
        assert booking_api.delete_booking(created_booking["id"]).status_code == 403
        assert booking_api.get_booking(created_booking["id"]).status_code == 200

    @pytest.mark.parametrize("case", as_params("bookings.json", "invalid_tokens"))
    def test_update_with_invalid_token_is_forbidden(self, booking_api, created_booking, case):
        response = booking_api.update_booking(
            created_booking["id"], created_booking["payload"], token=case["token"]
        )
        assert response.status_code == 403

    @pytest.mark.parametrize("case", as_params("bookings.json", "invalid_tokens"))
    def test_delete_with_invalid_token_is_forbidden(self, booking_api, created_booking, case):
        assert booking_api.delete_booking(created_booking["id"], token=case["token"]).status_code == 403
        assert booking_api.get_booking(created_booking["id"]).status_code == 200

    def test_valid_basic_auth_is_accepted(self, booking_api, created_booking, settings):
        headers = basic_auth(settings.api_username, settings.api_password)
        response = booking_api.partial_update_booking(
            created_booking["id"], {"firstname": "BasicAuth"}, headers=headers
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "user, password",
        [
            pytest.param("admin", "wrong", id="wrong_password"),
            pytest.param("guest", "password123", id="wrong_user"),
            pytest.param("", "", id="empty"),
        ],
    )
    def test_invalid_basic_auth_is_forbidden(self, booking_api, created_booking, user, password):
        response = booking_api.partial_update_booking(
            created_booking["id"], {"firstname": "Hacker"}, headers=basic_auth(user, password)
        )
        assert response.status_code == 403
