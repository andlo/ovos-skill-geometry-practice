# Development

## Architecture at a glance

Two quiz types plus teach-then-practice. All glossary/formula/
computation data comes from
[ovos-skill-geometry](https://github.com/andlo/ovos-skill-geometry)
(a `requirements.txt` dependency) - `GLOSSARY`, `resolve_term()`,
`rectangle_area()`, `pythagorean_hypotenuse()`, `PYTHAGOREAN_TRIPLES`,
`format_number()`, `parse_number()`, etc, imported directly rather
than duplicated. See that package's own DEVELOPMENT.md for the data
itself.

## Grading: exact where possible, real tolerance where not

`grade_numeric_response(response, correct_value, exact, lang)`:
- `exact=True` uses `DECIMAL_GRADING_EPSILON` (0.01) - a
  float-representation guard only, not a real tolerance. Used for
  rectangle/square/triangle area/perimeter (always integer or a
  clean X.5 from integer dimensions) and triple-based Pythagoras
  (always a clean integer).
- `exact=False` uses `within_tolerance()` - a REAL 2% margin. Used
  ONLY for circle area/circumference (pi) and non-triple Pythagoras
  (an irrational square root the vast majority of the time). This is
  the first skill in the `*-practice` family that genuinely needs
  this - `ovos-skill-math-practice`'s DEVELOPMENT.md flagged that a
  "genuinely irrational quantity... can't be constructed exact and
  will need real tolerance-band grading" back when it was still
  hypothetical; this is that case actually arriving.
- Percentage-based, not a fixed absolute margin, since answers here
  range from single digits to hundreds - a fixed margin would be far
  too loose for small values and far too strict for large ones.

## Question generation

`generate_definition_question(term_key=None)` - distractors are
OTHER glossary entries' real definitions from the SAME category
(`GLOSSARY[key]` is `"term"`/`"shape2d"`/`"shape3d"`) - guaranteed
well-formed, true sentences, never invented wrong text, and at least
plausible since they're the same kind of thing.

`generate_area_perimeter_question()` - picks a random shape from
`rectangle`/`square`/`triangle`/`circle` and a random property valid
for it (`FORMULA_PROPERTIES`), with integer dimensions in [2, 20]
(circle radius in [2, 15], kept smaller since pi-multiplied values
grow fast). Returns `exact=False` only for circle.

`generate_pythagoras_question()` - 50/50 between a known
`PYTHAGOREAN_TRIPLES` entry (exact) and arbitrary integer legs in
[2, 20] (not exact, the hypotenuse is irrational the vast majority of
the time).

## Teach mode reuses ovos-skill-geometry's own answer-dialog wording

`_worked_example_text()` duplicates 7 dialog files
(`area_of_rectangle.dialog`, etc) from `ovos-skill-geometry`'s
locale/ into this repo's own locale/ - same reasoning as
`ovos-skill-geography-practice`'s `about_country.dialog` copy:
`self.resources.load_dialog_file()` only reads the CALLING skill's
own locale folder, so a shared sentence-builder still needs a local
copy of the wording. `EXAMPLE_DIMS` (fixed, not randomized - 5&3,
4, 6&4, 4) keeps worked examples easy to follow along with mentally,
unlike the randomized quiz questions.

**A real bug this surfaced, not just a design note:** building this
teach mode's `formula_words()` reuse caught a doubled-phrasing bug
that had already shipped in `ovos-skill-geometry` v0.0.1 ("the area
of a circle is the area of a circle is pi times the radius squared")
- fixed there in v0.0.2. `FORMULA_WORDS` must store only the
right-hand side of the formula, never a full sentence, since the
dialog templates that consume it (both there and here) already
supply the "the X of a Y is" prefix.

## `quiz_taught()` mixes topics per taught entry

For each taught key: the `"_pythagorean"` sentinel always gets a
Pythagoras question; a shape with `FORMULA_PROPERTIES` gets a 50/50
mix of a definition question or a numeric formula question (a random
one of its supported properties, freshly generated - not the fixed
teach-mode example numbers); anything else (a term with no formula)
always gets a definition question. Reuses the exact same
`_ask_and_grade_*()` methods the standalone quizzes use.

## Setup
```bash
git clone https://github.com/andlo/ovos-skill-geometry-practice.git
cd ovos-skill-geometry-practice
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```

## Running tests
```bash
pytest tests/ -v
```
`tests/test_data_loading.py` checks every locale has every required
intent/dialog/vocab file (19 dialogs x 5 languages was a lot of
manual authoring - this is the automated safety net).
`tests/test_grading_and_generation.py` covers `within_tolerance()`,
`grade_numeric_response()`'s exact-vs-tolerance branches, and the
three question generators. `tests/test_quiz.py` and
`tests/test_teach_then_practice.py` cover the intent handlers and
teach/quiz flow, en-us locale.

## Versioning and releasing

Same convention as the rest of this project family - see
`ovos-skill-geography-practice`'s DEVELOPMENT.md for the exact steps
(tag-triggered PyPI publish via trusted publishing OIDC, needs a
one-time per-package browser setup before the first release).

## Style / conventions

- License: GPL-3.0-or-later.
- `locale/<lang-code>/` layout, `skill.json` inside each locale
  folder.
- Present design changes for review before implementing.
