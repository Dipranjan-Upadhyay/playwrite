"""Root fixtures shared by UI and API suites."""
import copy
import platform

import pytest

from api.booking_api import BookingApi
from api.client import ApiClient
from config.settings import settings as _settings
from utils.data_loader import load_json


@pytest.fixture(scope="session")
def settings():
    return _settings


# ---------------- API fixtures ----------------
@pytest.fixture(scope="session")
def api_client(settings):
    client = ApiClient(settings.api_base_url, settings.request_timeout)
    yield client
    client.session.close()


@pytest.fixture(scope="session")
def booking_api(api_client):
    return BookingApi(api_client)


@pytest.fixture(scope="session")
def auth_token(booking_api, settings):
    response = booking_api.create_token(settings.api_username, settings.api_password)
    assert response.status_code == 200, f"Could not authenticate: {response.text}"
    return response.json()["token"]


@pytest.fixture
def booking_payload():
    """A fresh, mutable copy of a valid booking for each test."""
    return copy.deepcopy(load_json("bookings.json")["valid_bookings"][0]["payload"])


@pytest.fixture
def created_booking(booking_api, booking_payload, auth_token):
    """Creates a booking for the test and always deletes it afterwards."""
    response = booking_api.create_booking(booking_payload)
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    yield {"id": booking_id, "payload": booking_payload}
    booking_api.delete_booking(booking_id, token=auth_token)


# ---------------- Allure environment widget ----------------
def pytest_sessionfinish(session):
    # Only the controller process writes it when running under pytest-xdist.
    if hasattr(session.config, "workerinput"):
        return
    alluredir = session.config.getoption("--alluredir", default=None)
    if not alluredir:
        return
    from pathlib import Path

    out = Path(alluredir)
    out.mkdir(parents=True, exist_ok=True)
    browsers = session.config.getoption("--browser", default=None) or ["chromium"]
    (out / "environment.properties").write_text(
        "\n".join(
            [
                f"UI.Base.URL={_settings.ui_base_url}",
                f"API.Base.URL={_settings.api_base_url}",
                f"Browsers={','.join(browsers)}",
                f"Python={platform.python_version()}",
                f"OS={platform.system()} {platform.release()}",
            ]
        ),
        encoding="utf-8",
    )
