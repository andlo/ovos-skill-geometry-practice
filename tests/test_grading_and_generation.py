"""Tests for grading and question-generation invariants."""
import math

from unittest.mock import patch


def test_within_tolerance_accepts_close_values():
    import geometrypractice_skill as m
    assert m.within_tolerance(50.3, 50.2654)
    assert not m.within_tolerance(52.0, 50.2654)


def test_within_tolerance_zero_edge_case():
    import geometrypractice_skill as m
    assert m.within_tolerance(0.005, 0)
    assert not m.within_tolerance(1, 0)


def test_grade_numeric_exact_uses_epsilon_not_tolerance():
    import geometrypractice_skill as m
    # 15.005 is within DECIMAL_GRADING_EPSILON of 15 but the SAME
    # relative distance would fail a 2% tolerance check for a small
    # number like this if it were treated as non-exact - confirms
    # exact=True uses the tight epsilon, not the loose percentage.
    assert m.grade_numeric_response("15.005", 15.0, True, "en-us")
    assert not m.grade_numeric_response("15.3", 15.0, True, "en-us")


def test_grade_numeric_tolerance_accepts_approximate_pi_based_answer():
    import geometrypractice_skill as m
    correct = math.pi * 16  # ~50.2655
    assert m.grade_numeric_response("50.3", correct, False, "en-us")
    assert not m.grade_numeric_response("40", correct, False, "en-us")


def test_grade_numeric_unparseable_response_is_wrong():
    import geometrypractice_skill as m
    assert not m.grade_numeric_response("banana", 15.0, True, "en-us")


def test_generate_definition_question_distractors_are_same_category():
    import geometrypractice_skill as m
    for _ in range(20):
        key, choices, correct_idx = m.generate_definition_question("circle")
        assert key == "circle"
        assert choices[correct_idx] == "circle"
        assert len(choices) == 3
        assert len(set(choices)) == 3
        for c in choices:
            assert m.GLOSSARY[c] == m.GLOSSARY["circle"]


def test_generate_area_perimeter_question_rectangle_always_exact():
    import geometrypractice_skill as m
    for _ in range(30):
        shape, prop, dims, value, exact = m.generate_area_perimeter_question()
        if shape == "circle":
            assert exact is False
        else:
            assert exact is True


def test_generate_pythagoras_question_triples_are_exact_integers():
    import geometrypractice_skill as m
    with patch("geometrypractice_skill.random.random", return_value=0.0):
        leg_a, leg_b, hyp, exact = m.generate_pythagoras_question()
    assert exact is True
    assert hyp == int(hyp)
    assert (leg_a, leg_b, hyp) in m.PYTHAGOREAN_TRIPLES or (leg_b, leg_a, hyp) in m.PYTHAGOREAN_TRIPLES
