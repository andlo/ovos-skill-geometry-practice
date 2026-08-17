# Development

**This skill doesn't exist as code yet - this document describes how
to get started once the open design questions in README.md are
resolved, not how to work on something already built.**

## Before writing any code

The README's "Real, open design questions" section has three items
that affect the skill's core architecture (grading tolerance,
problem-generation strategy, teach-mode content). At least the
tolerance-band question should be resolved - here or in whichever of
`ovos-skill-unit-practice` / `ovos-skill-math-practice` issue #5
lands first - before scaffolding starts, since it changes how
`generate_problem()`-equivalent logic needs to be built from day one.

## Setup (once implementation starts)
```bash
git clone https://github.com/andlo/ovos-skill-geometry-practice.git
cd ovos-skill-geometry-practice
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```
(`setup.py`, `requirements.txt`, `requirements-test.txt`, `__init__.py`,
`locale/`, `tests/`, `version.py`, `.github/workflows/` don't exist
yet - `ovos-skill-math-practice` is the reference layout to copy from
when scaffolding begins.)

## Expected structure, mirroring `ovos-skill-math-practice`

- `__init__.py` - skill logic. Likely: a Pythagorean-triple-based
  generator for the "clean by construction" easy tier, a formula
  registry (name -> callable + required inputs), teach/quiz intent
  handlers following the same `get_response()` pattern (no background
  thread needed here either).
- `locale/<lang>/` - intents, dialogs, and (if the tolerance/alias
  pattern from `unit-practice` or `convert` ends up reused) any alias
  JSON files, same convention as the rest of this project family.
- `tests/` - invariant tests for problem generation (mirroring
  `math-practice`'s `test_problem_generation.py` - e.g. "every
  Pythagorean-triple-derived problem's hypotenuse actually satisfies
  a²+b²=c²"), plus flow tests for teach/quiz mirroring
  `test_quiz.py` / `test_teach_then_practice.py`.

## Versioning and releasing

Not applicable yet - no `version.py`, no tags, nothing published.
When implementation starts, follow `ovos-skill-math-practice`'s
`DEVELOPMENT.md` exactly (semantic-ish `MAJOR.MINOR.BUILD[aALPHA]`
versioning, tag-triggered PyPI release via trusted publishing OIDC,
GitHub Release notes accompanying every publish).

## Style / conventions

- License: GPL-3.0-or-later (matches the other `andlo` skill repos).
- `locale/<lang-code>/` layout, `skill.json` inside each locale
  folder, once locale exists.
- Present design changes for review before implementing - same rule
  as every other skill in this family.
