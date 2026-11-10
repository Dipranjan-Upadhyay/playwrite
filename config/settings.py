"""Central configuration. Every value can be overridden by an environment variable,
so the same suite runs locally, in CI, or against another environment."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ui_base_url: str = os.getenv("UI_BASE_URL", "https://www.saucedemo.com")
    ui_password: str = os.getenv("UI_PASSWORD", "secret_sauce")  # public demo credential

    api_base_url: str = os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")
    api_username: str = os.getenv("API_USERNAME", "admin")  # public demo credential
    api_password: str = os.getenv("API_PASSWORD", "password123")
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))


settings = Settings()
