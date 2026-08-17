"""Tests for the 3 quiz intent handlers and quiz_taught, en-us locale.
Mocks get_response/voc_match/speak_dialog for deterministic flow."""
from unittest.mock import MagicMock, patch


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_quiz_terms_asks_five_questions(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="a")
    skill.voc_match = MagicMock(side_effect=lambda u, v: v == "choice_a")
    skill.handle_quiz_terms(_msg())
    assert skill.get_response.call_count == 5
    final = skill.speak_dialog.call_args_list[-1]
    assert final[0][0] == "quiz_finished"
    assert final[0][1]["total"] == 5


def test_quiz_area_perimeter_asks_five_questions(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="100")
    skill.handle_quiz_area_perimeter(_msg())
    assert skill.get_response.call_count == 5
    final = skill.speak_dialog.call_args_list[-1]
    assert final[0][0] == "quiz_finished"


def test_quiz_pythagoras_asks_five_questions(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="100")
    skill.handle_quiz_pythagoras(_msg())
    assert skill.get_response.call_count == 5
    final = skill.speak_dialog.call_args_list[-1]
    assert final[0][0] == "quiz_finished"


def test_quiz_taught_with_nothing_taught(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_quiz_taught(_msg())
    skill.speak_dialog.assert_called_once_with("nothing_taught_yet")


def test_quiz_taught_pythagoras_sentinel(skill):
    skill._taught_keys = ["_pythagorean"]
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="5")
    skill.handle_quiz_taught(_msg())
    assert skill.get_response.call_count == 1
    final = skill.speak_dialog.call_args_list[-1]
    assert final[0][0] == "quiz_finished"
    assert final[0][1]["total"] == 1
