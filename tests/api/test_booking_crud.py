import allure
import pytest

from utils.data_loader import as_params
from utils.schema_validator import assert_matches_schema

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.feature("API - Bookings")
class TestBookingCrud:
    @pytest.mark.smoke
    def test_health_check(self, booking_api):
        assert booking_api.health_check().status_code == 201

    @pytest.mark.smoke
    @pytest.mark.schema
    def test_list_booking_ids_matches_schema(self, booking_api):
        response = booking_api.get_booking_ids()
        assert response.status_code == 200
        assert_matches_schema(response.json(), "booking_ids.json")

    @pytest.mark.schema
    @pytest.mark.parametrize("case", as_params("bookings.json", "valid_bookings"))
    def test_create_booking(self, booking_api, auth_token, case):
        response = booking_api.create_booking(case["payload"])
        assert response.status_code == 200
        body = response.json()
        try:
            assert_matches_schema(body, "create_booking_response.json")
            assert body["booking"] == case["payload"]
        finally:
            booking_api.delete_booking(body["bookingid"], token=auth_token)

    @pytest.mark.schema
    def test_get_booking_by_id(self, booking_api, created_booking):
        response = booking_api.get_booking(created_booking["id"])
        assert response.status_code == 200
        assert_matches_schema(response.json(), "booking.json")
        assert response.json() == created_booking["payload"]

    def test_filter_booking_ids_by_name(self, booking_api, created_booking):
        payload = created_booking["payload"]
        response = booking_api.get_booking_ids(
            firstname=payload["firstname"], lastname=payload["lastname"]
        )
        assert response.status_code == 200
        ids = [b["bookingid"] for b in response.json()]
        assert created_booking["id"] in ids

    def test_full_update_booking(self, booking_api, created_booking, auth_token):
        updated = {**created_booking["payload"], "firstname": "Updated", "totalprice": 777}
        response = booking_api.update_booking(created_booking["id"], updated, token=auth_token)
        assert response.status_code == 200
        assert_matches_schema(response.json(), "booking.json")
        assert response.json() == updated

    @pytest.mark.parametrize(
        "patch",
        [
            pytest.param({"firstname": "Patched"}, id="firstname"),
            pytest.param({"totalprice": 1}, id="totalprice"),
            pytest.param({"depositpaid": False}, id="depositpaid"),
            pytest.param({"additionalneeds": "Dinner"}, id="additionalneeds"),
        ],
    )
    def test_partial_update_booking(self, booking_api, created_booking, auth_token, patch):
        response = booking_api.partial_update_booking(created_booking["id"], patch, token=auth_token)
        assert response.status_code == 200
        assert response.json() == {**created_booking["payload"], **patch}

    def test_delete_booking(self, booking_api, booking_payload, auth_token):
        booking_id = booking_api.create_booking(booking_payload).json()["bookingid"]
        assert booking_api.delete_booking(booking_id, token=auth_token).status_code == 201
        assert booking_api.get_booking(booking_id).status_code == 404
