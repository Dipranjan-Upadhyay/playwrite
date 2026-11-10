"""Service object for the Restful-Booker API (the API equivalent of a page object)."""
from api.client import ApiClient


class BookingApi:
    def __init__(self, client: ApiClient):
        self.client = client

    # --- auth ---
    def create_token(self, username: str, password: str):
        return self.client.post("/auth", json={"username": username, "password": password})

    # --- bookings ---
    def health_check(self):
        return self.client.get("/ping")

    def get_booking_ids(self, **filters):
        return self.client.get("/booking", params=filters or None)

    def get_booking(self, booking_id):
        return self.client.get(f"/booking/{booking_id}")

    def create_booking(self, payload):
        return self.client.post("/booking", json=payload)

    def create_booking_raw(self, raw_body: str):
        return self.client.post("/booking", data=raw_body)

    def update_booking(self, booking_id, payload, token=None, headers=None):
        return self.client.put(
            f"/booking/{booking_id}", json=payload, headers=self._auth(token, headers)
        )

    def partial_update_booking(self, booking_id, payload, token=None, headers=None):
        return self.client.patch(
            f"/booking/{booking_id}", json=payload, headers=self._auth(token, headers)
        )

    def delete_booking(self, booking_id, token=None, headers=None):
        return self.client.delete(f"/booking/{booking_id}", headers=self._auth(token, headers))

    @staticmethod
    def _auth(token, headers):
        merged = dict(headers or {})
        if token is not None:
            merged["Cookie"] = f"token={token}"
        return merged
