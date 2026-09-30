"""Shared pytest fixtures for the geometry-practice skill test suite."""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("geometrypractice_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
sys.modules["geometrypractice_skill"] = _module
_spec.loader.exec_module(_module)

GeometryPractice = _module.GeometryPractice


@pytest.fixture
def skill(monkeypatch):
    s = GeometryPractice.__new__(GeometryPractice)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-geometry-practice.test"
    s.status = MagicMock()
    s._bus = MagicMock()
    monkeypatch.setattr(GeometryPractice, "lang", "en-us", raising=False)
    s.res_dir = str(Path(__file__).resolve().parents[1])
    s._lang_resources = {}
    s._voc_cache = {}
    # ovos-workshop >= 9.8 auto-registers entity files on load_lang(); needs
    # attributes that __new__() bypasses, and there are no entity files here
    monkeypatch.setattr(GeometryPractice, "_auto_register_entity_files", lambda *a, **k: None, raising=False)
    s._taught_keys = []
    return s
