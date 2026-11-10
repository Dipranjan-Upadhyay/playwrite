"""JSON-schema validation with cross-file $ref support and Allure-friendly errors."""
import json
from functools import lru_cache
from pathlib import Path

import allure
from jsonschema import Draft7Validator, FormatChecker
from referencing import Registry, Resource

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


@lru_cache(maxsize=1)
def _registry() -> Registry:
    resources = []
    for path in SCHEMA_DIR.glob("*.json"):
        contents = json.loads(path.read_text(encoding="utf-8"))
        resources.append((path.name, Resource.from_contents(contents)))
    return Registry().with_resources(resources)


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def assert_matches_schema(instance, schema_name: str) -> None:
    validator = Draft7Validator(
        load_schema(schema_name), registry=_registry(), format_checker=FormatChecker()
    )
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    with allure.step(f"Validate response against schema '{schema_name}'"):
        if errors:
            details = "\n".join(
                f"- at '{'/'.join(map(str, e.path)) or '<root>'}': {e.message}" for e in errors
            )
            allure.attach(details, "schema errors", allure.attachment_type.TEXT)
            raise AssertionError(f"Response does not match {schema_name}:\n{details}")
