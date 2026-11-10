"""Loads external test data so tests stay data-driven (edit JSON, not code)."""
import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"


def load_json(file_name: str):
    return json.loads((DATA_DIR / file_name).read_text(encoding="utf-8"))


def as_params(file_name: str, key: str, id_field: str = "id"):
    """Turn a list of dicts in a JSON file into pytest.param objects with readable ids."""
    return [pytest.param(case, id=case[id_field]) for case in load_json(file_name)[key]]
