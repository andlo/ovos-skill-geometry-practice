"""
skill OVOS Geometry Practice
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

Interactive geometry quizzes and teach-then-practice: glossary term
recognition (multiple choice), area/perimeter/circumference
calculation, and Pythagoras' theorem.

Depends on ovos-skill-geometry directly for its glossary, formulas,
and computation functions (GLOSSARY, resolve_term(), rectangle_area(),
pythagorean_hypotenuse(), PYTHAGOREAN_TRIPLES, etc) rather than
duplicating them - the same relationship
ovos-skill-geography-practice has with ovos-skill-geography.

THE REAL DIFFERENCE FROM THE REST OF THIS PROJECT FAMILY: most
*-practice skills construct every quiz problem so the answer is
exact (no tolerance needed at all). Geometry can't always do that -
circle area/circumference (uses pi) and a Pythagorean hypotenuse from
non-triple legs are GENUINELY irrational. This is the first skill in
the family to use a real tolerance-band grade (see
within_tolerance() and DEVELOPMENT.md) rather than construct-exact.
Where exact construction IS possible (rectangle/square/triangle
area/perimeter, and triple-based Pythagoras), it's still used -
tolerance is the exception, not the default, even here.
"""

import random

import functools
import threading

from ovos_bus_client.message import Message
from ovos_bus_client.session import SessionManager
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

from ovos_skill_geometry import (
    GLOSSARY,
    GLOSSARY_NAMES,
    resolve_term,
    term_name,
    term_definition,
    FORMULA_PROPERTIES,
    formula_words,
    rectangle_area,
    rectangle_perimeter,
    square_area,
    square_perimeter,
    triangle_area,
    circle_area,
    circle_circumference,
    pythagorean_hypotenuse,
    PYTHAGOREAN_TRIPLES,
    format_number,
    parse_number,
)

NUM_QUIZ_QUESTIONS = 5
TOLERANCE_PERCENT = 0.02  # 2% - see DEVELOPMENT.md for why this exists at all
DECIMAL_GRADING_EPSILON = 0.01  # float-representation guard ONLY, not a real tolerance - see ovos-skill-math-practice's DEVELOPMENT.md precedent


# ---------------------------------------------------------------
# Grading - the ONE place in this project family that uses a real
# tolerance-band, alongside exact grading (still used wherever
# construction makes it possible). See DEVELOPMENT.md.
# ---------------------------------------------------------------

def within_tolerance(value, correct, tolerance_percent=TOLERANCE_PERCENT):
    """A REAL tolerance-band, not a float-representation guard - used
    only for genuinely irrational correct values (circle area/
    circumference, non-triple Pythagoras). Percentage-based rather
    than a fixed absolute margin, since geometry answers here range
    from single digits to hundreds - a fixed margin would be far too
    loose for small values and far too strict for large ones."""
    if correct == 0:
        return abs(value) < 0.01
    return abs(value - correct) / abs(correct) <= tolerance_percent


def grade_numeric_response(response_raw, correct_value, exact, lang):
    """exact=True: DECIMAL_GRADING_EPSILON (float-representation
    guard only, matching ovos-skill-math-practice's decimal
    precedent). exact=False: within_tolerance() (a real % margin,
    the genuinely-irrational case)."""
    value = parse_number(response_raw, lang)
    if value is None:
        return False
    if exact:
        return abs(value - correct_value) < DECIMAL_GRADING_EPSILON
    return within_tolerance(value, correct_value)


# ---------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------

def generate_definition_question(term_key=None):
    """Returns (key, choices, correct_index) for a 3-way multiple-
    choice 'which of these is the definition of a {term}' question.
    Distractors are OTHER glossary entries' REAL definitions from the
    SAME category (term/shape2d/shape3d) - guaranteed well-formed,
    true sentences, never invented wrong text, and at least plausible
    since they're the same kind of thing (a shape's wrong options are
    other shapes, not random terms)."""
    keys = list(GLOSSARY.keys())
    key = term_key or random.choice(keys)
    category = GLOSSARY[key]
    same_category = [k for k in keys if GLOSSARY[k] == category and k != key]
    distractor_count = min(2, len(same_category))
    distractors = random.sample(same_category, distractor_count)
    choices = [key] + distractors
    random.shuffle(choices)
    return key, choices, choices.index(key)


def generate_area_perimeter_question():
    """Returns (shape, prop, dims, correct_value, exact). rectangle/
    square/triangle are always constructed from integer dimensions,
    so their area/perimeter is always exact (an integer, or - for
    triangle - a clean X.5, still exactly representable, not
    irrational). circle is the one genuinely irrational case here
    (pi) - exact=False, needs within_tolerance()."""
    shape = random.choice(["rectangle", "square", "triangle", "circle"])
    prop = random.choice(FORMULA_PROPERTIES[shape])
    if shape == "rectangle":
        length, width = random.randint(2, 20), random.randint(2, 20)
        dims = {"length": length, "width": width}
        value = rectangle_area(length, width) if prop == "area" else rectangle_perimeter(length, width)
        exact = True
    elif shape == "square":
        side = random.randint(2, 20)
        dims = {"side": side}
        value = square_area(side) if prop == "area" else square_perimeter(side)
        exact = True
    elif shape == "triangle":
        base, height = random.randint(2, 20), random.randint(2, 20)
        dims = {"base": base, "height": height}
        value = triangle_area(base, height)
        exact = True
    else:  # circle
        radius = random.randint(2, 15)
        dims = {"radius": radius}
        value = circle_area(radius) if prop == "area" else circle_circumference(radius)
        exact = False
    return shape, prop, dims, value, exact


def generate_pythagoras_question():
    """Returns (leg_a, leg_b, hypotenuse, exact). Half the time, a
    known Pythagorean triple (exact integer hypotenuse, no tolerance
    needed) - the other half, arbitrary integer legs (a genuinely
    irrational hypotenuse the vast majority of the time, needs
    within_tolerance())."""
    if random.random() < 0.5:
        a, b, c = random.choice(PYTHAGOREAN_TRIPLES)
        if random.random() < 0.5:
            a, b = b, a
        return a, b, c, True
    leg_a, leg_b = random.randint(2, 20), random.randint(2, 20)
    return leg_a, leg_b, pythagorean_hypotenuse(leg_a, leg_b), False


# ---------------------------------------------------------------
# Category resolution for teach mode - hand-authored (only 3
# categories), not sourced anywhere - see ovos-skill-geometry's
# GLOSSARY category field ("term"/"shape2d"/"shape3d").
# ---------------------------------------------------------------
CATEGORY_NAMES = {
    "en-us": {"term": "terms", "shape2d": "2d shapes", "shape3d": "3d shapes"},
    "da-dk": {"term": "termer", "shape2d": "2d former", "shape3d": "3d former"},
    "de-de": {"term": "begriffe", "shape2d": "2d formen", "shape3d": "3d formen"},
    "fr-fr": {"term": "termes", "shape2d": "formes en 2d", "shape3d": "formes en 3d"},
    "es-es": {"term": "términos", "shape2d": "formas en 2d", "shape3d": "formas en 3d"},
}
CATEGORY_NAME_TO_KEY = {
    lang: {name.strip().lower(): key for key, name in names.items()}
    for lang, names in CATEGORY_NAMES.items()
}


def resolve_category(raw, lang):
    if not raw:
        return None
    lang = lang.lower()
    lookup = CATEGORY_NAME_TO_KEY.get(lang) or CATEGORY_NAME_TO_KEY.get("en-us", {})
    return lookup.get(raw.strip().lower())


SHAPE_PHRASE_DIALOG = {
    "rectangle": "quiz_question_rectangle",
    "square": "quiz_question_square",
    "triangle": "quiz_question_triangle",
    "circle": "quiz_question_circle",
}

# Fixed, small, clean-number dimensions for teach mode's worked
# examples - not randomized, since a worked example should be easy
# to follow along with mentally, not a fresh random quiz question.
EXAMPLE_DIMS = {
    "rectangle": {"length": 5, "width": 3},
    "square": {"side": 4},
    "triangle": {"base": 6, "height": 4},
    "circle": {"radius": 4},
}
WORKED_EXAMPLE_DIALOG = {
    ("rectangle", "area"): "area_of_rectangle", ("rectangle", "perimeter"): "perimeter_of_rectangle",
    ("square", "area"): "area_of_square", ("square", "perimeter"): "perimeter_of_square",
    ("triangle", "area"): "area_of_triangle",
    ("circle", "area"): "area_of_circle", ("circle", "circumference"): "circumference_of_circle",
}


class QuizStopped(Exception):
    """Raised inside a quiz or lesson once "stop" was requested for its
    session, so the question loop ends instead of asking the next one."""


def _session_id(message):
    try:
        return SessionManager.get(message).session_id
    except Exception:  # no usable session in the message
        return "default"


def stoppable(handler):
    """Marks an intent handler as stoppable: while it runs, can_stop()
    answers True for its session, and a stop for that session makes the
    next (or current) question end the handler quietly."""
    @functools.wraps(handler)
    def wrapper(self, message):
        sid = _session_id(message)
        state = self._stop_state()
        state["active"].add(sid)
        state["requested"].discard(sid)
        state["local"].sid = sid
        try:
            return handler(self, message)
        except QuizStopped:
            self.log.info(f"stopped in session {sid}")
        finally:
            state["active"].discard(sid)
            state["requested"].discard(sid)
            state["local"].sid = None
    return wrapper


class GeometryPractice(OVOSSkill):


    # ------------------------------------------------------------------
    # Stop support (session-scoped)
    # ------------------------------------------------------------------

    def _stop_state(self):
        state = self.__dict__.get("_stop_state_data")
        if state is None:
            state = {"active": set(), "requested": set(), "local": threading.local()}
            self.__dict__["_stop_state_data"] = state
        return state

    def _raise_if_stopped(self):
        state = self._stop_state()
        sid = getattr(state["local"], "sid", None)
        if sid is not None and sid in state["requested"]:
            raise QuizStopped()

    def _ask(self, *args, **kwargs):
        """get_response() that ends the quiz/lesson once stop was
        requested - before asking, and after the (then aborted) wait."""
        self._raise_if_stopped()
        response = self.get_response(*args, **kwargs)
        self._raise_if_stopped()
        return response

    def can_stop(self, message) -> bool:
        return _session_id(message) in self._stop_state()["active"]

    def stop_session(self, session) -> bool:
        state = self._stop_state()
        if session.session_id in state["active"]:
            state["requested"].add(session.session_id)
            # End a get_response() that is waiting right now. Setting the
            # response to None (what workshop does after a successful stop)
            # is not enough on ovos-workshop 7.x: the wait loop keeps going.
            # abort_question is the supported way on 7.x and 9.x alike.
            self.bus.emit(Message("mycroft.skills.abort_question",
                                  {"skill_id": self.skill_id},
                                  {"session": session.serialize(),
                                   "skill_id": self.skill_id}))
            return True
        return False

    def initialize(self):
        self._taught_keys = []  # glossary keys taught this session, plus the sentinel "pythagorean"

    def _ask_and_grade_definition(self, key):
        term, choices, correct_idx = generate_definition_question(key)
        letters = ["A", "B", "C"][:len(choices)]
        options = "; ".join(
            f"{letter}: {term_definition(k, self.lang)}" for letter, k in zip(letters, choices))
        response = self._ask(dialog="quiz_question_definition", data={
            "term": term_name(term, self.lang), "options": options})
        if response is None:
            self.speak_dialog("quiz_no_answer")
            return False
        picked = None
        for letter in letters:
            if self.voc_match(response, f"choice_{letter.lower()}"):
                picked = letter
                break
        correct_letter = letters[correct_idx]
        if picked == correct_letter:
            self.speak_dialog("quiz_correct")
            return True
        self.speak_dialog("quiz_incorrect_definition", {
            "letter": correct_letter, "term": term_name(term, self.lang),
            "definition": term_definition(term, self.lang)})
        return False

    def _ask_and_grade_area_perimeter(self, shape, prop, dims, correct_value, exact):
        dims_formatted = {k: format_number(v) for k, v in dims.items()}
        response = self._ask(dialog=SHAPE_PHRASE_DIALOG[shape], data={
            **dims_formatted, "property": term_name(prop, self.lang)})
        if response is None:
            self.speak_dialog("quiz_no_answer")
            return False
        if grade_numeric_response(response, correct_value, exact, self.lang):
            self.speak_dialog("quiz_correct")
            return True
        self.speak_dialog("quiz_incorrect_numeric", {"answer": format_number(correct_value)})
        return False

    def _ask_and_grade_pythagoras(self, leg_a, leg_b, hyp, exact):
        response = self._ask(dialog="quiz_question_pythagoras", data={
            "leg_a": format_number(leg_a), "leg_b": format_number(leg_b)})
        if response is None:
            self.speak_dialog("quiz_no_answer")
            return False
        if grade_numeric_response(response, hyp, exact, self.lang):
            self.speak_dialog("quiz_correct")
            return True
        self.speak_dialog("quiz_incorrect_numeric", {"answer": format_number(hyp)})
        return False


    @intent_handler("quiz_terms.intent")
    @stoppable
    def handle_quiz_terms(self, message):
        correct_count = 0
        for _ in range(NUM_QUIZ_QUESTIONS):
            if self._ask_and_grade_definition(None):
                correct_count += 1
        self.speak_dialog("quiz_finished", {"correct": correct_count, "total": NUM_QUIZ_QUESTIONS})

    @intent_handler("quiz_area_perimeter.intent")
    @stoppable
    def handle_quiz_area_perimeter(self, message):
        correct_count = 0
        for _ in range(NUM_QUIZ_QUESTIONS):
            shape, prop, dims, value, exact = generate_area_perimeter_question()
            if self._ask_and_grade_area_perimeter(shape, prop, dims, value, exact):
                correct_count += 1
        self.speak_dialog("quiz_finished", {"correct": correct_count, "total": NUM_QUIZ_QUESTIONS})

    @intent_handler("quiz_pythagoras.intent")
    @stoppable
    def handle_quiz_pythagoras(self, message):
        correct_count = 0
        for _ in range(NUM_QUIZ_QUESTIONS):
            leg_a, leg_b, hyp, exact = generate_pythagoras_question()
            if self._ask_and_grade_pythagoras(leg_a, leg_b, hyp, exact):
                correct_count += 1
        self.speak_dialog("quiz_finished", {"correct": correct_count, "total": NUM_QUIZ_QUESTIONS})


    # ------------------------------------------------------------------
    # Teach-then-practice (see README "Teach-then-practice" and
    # ovos-skill-math-practice issue #1 for the shared pattern)
    # ------------------------------------------------------------------

    def _worked_example_text(self, shape, prop):
        """Reuses ovos-skill-geometry's own answer-dialog WORDING
        (duplicated into this repo's locale/, same as
        ovos-skill-geography-practice's about_country.dialog copy) as
        the worked example - it already says exactly what a worked
        example should ('the area of a rectangle with length 5 and
        width 3 is 15'), no separate example-phrasing needed."""
        dims = EXAMPLE_DIMS[shape]
        if shape == "rectangle":
            value = rectangle_area(**dims) if prop == "area" else rectangle_perimeter(**dims)
        elif shape == "square":
            value = square_area(**dims) if prop == "area" else square_perimeter(**dims)
        elif shape == "triangle":
            value = triangle_area(**dims)
        else:
            value = circle_area(**dims) if prop == "area" else circle_circumference(**dims)
        data = {k: format_number(v) for k, v in dims.items()}
        data[prop] = format_number(value)
        dialog_name = WORKED_EXAMPLE_DIALOG[(shape, prop)]
        return self.resources.load_dialog_file(dialog_name, data)[0]

    def _teach_terms(self, keys):
        self._taught_keys = []
        for idx, key in enumerate(keys):
            parts = [self.resources.load_dialog_file("teach_definition", {
                "term": term_name(key, self.lang), "definition": term_definition(key, self.lang)})[0]]
            for prop in FORMULA_PROPERTIES.get(key, []):
                formula = formula_words(f"{key}_{prop}", self.lang)
                parts.append(self.resources.load_dialog_file("teach_formula", {
                    "shape": term_name(key, self.lang), "property": term_name(prop, self.lang),
                    "formula": formula})[0])
                parts.append(self._worked_example_text(key, prop))
            rendered = " ".join(parts)
            self.speak(rendered, wait=True)
            self._taught_keys.append(key)

            if idx == len(keys) - 1:
                break
            response = self._ask(dialog="continue_teaching_prompt")
            if response and self.voc_match(response, "repeat"):
                self.speak(rendered, wait=True)

        self.speak_dialog("teaching_finished", {"count": len(self._taught_keys)})

    @intent_handler("teach_me.intent")
    @stoppable
    def handle_teach_me(self, message):
        category_raw = message.data.get("category")
        category = resolve_category(category_raw, self.lang)
        if category is None:
            self.speak_dialog("category_not_understood", {"category": category_raw or ""})
            return
        keys = [k for k, cat in GLOSSARY.items() if cat == category]
        self._teach_terms(keys)

    @intent_handler("teach_pythagoras.intent")
    @stoppable
    def handle_teach_pythagoras(self, message):
        formula = formula_words("pythagorean", self.lang)
        a, b, c = 3, 4, 5
        example = self.resources.load_dialog_file("teach_example_pythagoras", {
            "leg_a": a, "leg_b": b, "hypotenuse": c})[0]
        rendered = self.resources.load_dialog_file("teach_pythagoras", {"formula": formula})[0] + " " + example
        self.speak(rendered, wait=True)
        self._taught_keys = ["_pythagorean"]
        self.speak_dialog("teaching_finished", {"count": 1})

    @intent_handler("quiz_taught.intent")
    @stoppable
    def handle_quiz_taught(self, message):
        """For each taught key: the Pythagoras sentinel always gets a
        Pythagoras question; a shape with formulas gets a 50/50 mix
        of a definition question or a numeric formula question (a
        random one of its supported properties); anything else
        (a term with no formula) always gets a definition question."""
        if not self._taught_keys:
            self.speak_dialog("nothing_taught_yet")
            return
        correct_count = 0
        total = len(self._taught_keys)
        for key in self._taught_keys:
            if key == "_pythagorean":
                leg_a, leg_b, hyp, exact = generate_pythagoras_question()
                ok = self._ask_and_grade_pythagoras(leg_a, leg_b, hyp, exact)
            elif key in FORMULA_PROPERTIES and random.random() < 0.5:
                prop = random.choice(FORMULA_PROPERTIES[key])
                # generate dims/value for this SPECIFIC taught shape+prop
                # (not generate_area_perimeter_question(), which picks a
                # random shape - we already know which shape was taught)
                if key == "rectangle":
                    dims = {"length": random.randint(2, 20), "width": random.randint(2, 20)}
                    value = rectangle_area(**dims) if prop == "area" else rectangle_perimeter(**dims)
                    exact = True
                elif key == "square":
                    dims = {"side": random.randint(2, 20)}
                    value = square_area(**dims) if prop == "area" else square_perimeter(**dims)
                    exact = True
                elif key == "triangle":
                    dims = {"base": random.randint(2, 20), "height": random.randint(2, 20)}
                    value = triangle_area(**dims)
                    exact = True
                else:  # circle
                    dims = {"radius": random.randint(2, 15)}
                    value = circle_area(**dims) if prop == "area" else circle_circumference(**dims)
                    exact = False
                ok = self._ask_and_grade_area_perimeter(key, prop, dims, value, exact)
            else:
                ok = self._ask_and_grade_definition(key)
            if ok:
                correct_count += 1
        self.speak_dialog("quiz_finished", {"correct": correct_count, "total": total})
