"""Input validation: missing fields, wrong types, malformed bodies, injection strings."""
import allure
import pytest

from utils.data_loader import as_params
from utils.schema_validator import assert_matches_schema

pytestmark = [pytest.mark.api, pytest.mark.security, pytest.mark.regression]


@allure.feature("API - Input validation")
class TestInputValidation:
    @pytest.mark.parametrize("case", as_params("bookings.json", "missing_required_fields"))
    def test_missing_required_field_is_rejected(self, booking_api, booking_payload, case):
        booking_payload.pop(case["remove"])
        response = booking_api.create_booking(booking_payload)
        assert response.status_code >= 400, "Booking with a missing field must not be created"
        assert "bookingid" not in response.text

    @pytest.mark.xfail(
        reason="Known defect: API answers 500 instead of 400 for invalid payloads", strict=False
    )
    def test_missing_field_returns_client_error(self, booking_api, booking_payload):
        booking_payload.pop("firstname")
        assert booking_api.create_booking(booking_payload).status_code == 400

    def test_malformed_json_is_rejected(self, booking_api):
        response = booking_api.create_booking_raw('{"firstname": "Jane", "lastname": ')
        assert response.status_code >= 400

    @pytest.mark.parametrize(
        "booking_id",
        [
            pytest.param(999999999, id="non_existent"),
            pytest.param("abc", id="non_numeric"),
            pytest.param(-1, id="negative"),
            pytest.param("' OR '1'='1", id="sql_injection"),
        ],
    )
    def test_invalid_booking_id_returns_404(self, booking_api, booking_id):
        assert booking_api.get_booking(booking_id).status_code == 404

    @pytest.mark.xfail(
        reason="Known defect: IDs are parsed leniently ('1abc', '1 OR 1=1' resolve to booking 1)",
        strict=False,
    )
    @pytest.mark.parametrize("booking_id", ["1abc", "1 OR 1=1"], ids=["trailing_chars", "sql_tail"])
    def test_id_with_trailing_garbage_is_rejected(self, booking_api, booking_id):
        assert booking_api.get_booking(booking_id).status_code == 404

    @pytest.mark.schema
    @pytest.mark.parametrize("case", as_params("bookings.json", "injection_strings"))
    def test_injection_strings_are_stored_as_literal_text(
        self, booking_api, booking_payload, auth_token, case
    ):
        """Malicious strings must be treated as data: stored verbatim, never interpreted."""
        booking_payload["firstname"] = case["value"]
        response = booking_api.create_booking(booking_payload)
        assert response.status_code == 200
        booking_id = response.json()["bookingid"]
        try:
            fetched = booking_api.get_booking(booking_id)
            assert fetched.status_code == 200
            assert fetched.headers["Content-Type"].startswith("application/json")
            assert_matches_schema(fetched.json(), "booking.json")
            assert fetched.json()["firstname"] == case["value"]
            # the service keeps working after the injection attempt
            assert booking_api.health_check().status_code == 201
        finally:
            booking_api.delete_booking(booking_id, token=auth_token)
