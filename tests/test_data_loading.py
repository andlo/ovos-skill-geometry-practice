"""Data-integrity tests - every locale has every required intent,
dialog, and vocab file. Given how much manual per-locale dialog
authoring this skill involved (19 dialogs x 5 languages), this is
the automated safety net against a missed file."""
from pathlib import Path

import pytest

LOCALES = ["en-us", "da-dk", "de-de", "fr-fr", "es-es"]
LOCALE_DIR = Path(__file__).resolve().parents[1] / "locale"

REQUIRED_INTENTS = [
    "quiz_terms", "quiz_area_perimeter", "quiz_pythagoras",
    "teach_me", "teach_pythagoras", "quiz_taught",
]
REQUIRED_DIALOGS = [
    "quiz_question_definition", "quiz_question_rectangle", "quiz_question_square",
    "quiz_question_triangle", "quiz_question_circle", "quiz_question_pythagoras",
    "quiz_correct", "quiz_incorrect_definition", "quiz_incorrect_numeric",
    "quiz_no_answer", "quiz_finished",
    "teach_definition", "teach_formula", "teach_pythagoras", "teach_example_pythagoras",
    "continue_teaching_prompt", "teaching_finished", "nothing_taught_yet",
    "category_not_understood",
    # worked-example dialogs duplicated from ovos-skill-geometry (see DEVELOPMENT.md)
    "area_of_rectangle", "perimeter_of_rectangle", "area_of_square", "perimeter_of_square",
    "area_of_triangle", "area_of_circle", "circumference_of_circle",
]
REQUIRED_VOC = ["choice_a", "choice_b", "choice_c", "repeat"]


@pytest.mark.parametrize("lang", LOCALES)
def test_every_intent_file_exists(lang):
    for name in REQUIRED_INTENTS:
        assert (LOCALE_DIR / lang / f"{name}.intent").exists(), f"{lang}/{name}.intent missing"


@pytest.mark.parametrize("lang", LOCALES)
def test_every_dialog_file_exists(lang):
    for name in REQUIRED_DIALOGS:
        assert (LOCALE_DIR / lang / f"{name}.dialog").exists(), f"{lang}/{name}.dialog missing"


@pytest.mark.parametrize("lang", LOCALES)
def test_every_voc_file_exists(lang):
    for name in REQUIRED_VOC:
        assert (LOCALE_DIR / lang / f"{name}.voc").exists(), f"{lang}/{name}.voc missing"


@pytest.mark.parametrize("lang", LOCALES)
def test_skill_json_exists(lang):
    assert (LOCALE_DIR / lang / "skill.json").exists(), f"{lang}/skill.json missing"
