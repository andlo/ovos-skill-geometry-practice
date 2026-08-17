"""Tests for teach-then-practice (handle_teach_me, handle_teach_pythagoras)."""
from unittest.mock import MagicMock


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_teach_me_terms_teaches_all_ten_terms(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="ok")
    skill.voc_match = MagicMock(return_value=False)
    skill.handle_teach_me(_msg(category="terms"))
    assert len(skill._taught_keys) == 10
    assert all(k for k in skill._taught_keys)
    final = skill.speak_dialog.call_args_list[-1]
    assert final == (("teaching_finished", {"count": 10}), {})


def test_teach_me_2d_shapes_includes_formula_for_rectangle(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="ok")
    skill.voc_match = MagicMock(return_value=False)
    skill.handle_teach_me(_msg(category="2d shapes"))
    assert "rectangle" in skill._taught_keys
    # a rectangle has 2 formula properties (area, perimeter) - each
    # should have contributed a "the ... is ..." + worked-example
    # utterance concatenated into ONE speak() call for that entry
    spoken = " ".join(str(c) for c in skill.speak.call_args_list)
    assert "length times width" in spoken


def test_teach_me_unrecognized_category(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.handle_teach_me(_msg(category="Narnia"))
    skill.speak_dialog.assert_called_once_with("category_not_understood", {"category": "Narnia"})
    skill.speak.assert_not_called()


def test_teach_me_repeat_flow(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(side_effect=["repeat"] + ["ok"] * 20)
    skill.voc_match = MagicMock(side_effect=lambda u, v: v == "repeat" and u == "repeat")
    skill.handle_teach_me(_msg(category="terms"))
    # 10 terms taught, first one repeated once = 11 speak() calls
    assert skill.speak.call_count == 11


def test_teach_pythagoras_records_sentinel(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.handle_teach_pythagoras(_msg())
    assert skill._taught_keys == ["_pythagorean"]
    skill.speak_dialog.assert_called_once_with("teaching_finished", {"count": 1})
    spoken = skill.speak.call_args[0][0]
    assert "hypotenuse" in spoken.lower()
