"""Thin wrapper over requests.Session that logs every call to the Allure report."""
import json

import allure
import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        with allure.step(f"{method.upper()} {endpoint}"):
            response = self.session.request(method, url, **kwargs)
            self._attach(method, url, kwargs, response)
        return response

    def get(self, endpoint, **kw):
        return self.request("GET", endpoint, **kw)

    def post(self, endpoint, **kw):
        return self.request("POST", endpoint, **kw)

    def put(self, endpoint, **kw):
        return self.request("PUT", endpoint, **kw)

    def patch(self, endpoint, **kw):
        return self.request("PATCH", endpoint, **kw)

    def delete(self, endpoint, **kw):
        return self.request("DELETE", endpoint, **kw)

    @staticmethod
    def _attach(method, url, kwargs, response):
        body = kwargs.get("json", kwargs.get("data"))
        req = f"{method.upper()} {url}\nparams: {kwargs.get('params')}\nbody: {body}"
        allure.attach(req, "request", allure.attachment_type.TEXT)
        try:
            resp_body = json.dumps(response.json(), indent=2)
        except ValueError:
            resp_body = response.text
        allure.attach(
            f"status: {response.status_code}\nelapsed: {response.elapsed.total_seconds():.3f}s\n\n{resp_body}",
            "response",
            allure.attachment_type.TEXT,
        )
