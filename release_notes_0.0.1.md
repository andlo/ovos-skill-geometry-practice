## Geometry Practice - first release

Interactive geometry quizzes and teach-then-practice - glossary term recognition, area/perimeter/circumference calculation, and Pythagoras' theorem. Fully offline, available in English, Danish, German, French, and Spanish.

### Quiz

- `"quiz me on geometry terms"` - 5 multiple-choice questions, distractors are OTHER glossary entries' real definitions, never invented text.
- `"quiz me on area and perimeter"` - 5 numeric questions across rectangle/square/triangle/circle.
- `"quiz me on pythagoras"` - 5 hypotenuse questions mixing known triples (exact) and arbitrary legs (tolerance-band).

### Teach-then-practice

`"teach me about terms"` / `"teach me about 2d shapes"` / `"teach me about 3d shapes"` / `"teach me pythagoras' theorem"`, then `"quiz me on what you taught me"` - the shared pattern from [ovos-skill-math-practice](https://github.com/andlo/ovos-skill-math-practice).

### The first real tolerance-band grade in this project family

Every other `*-practice` skill constructs quiz answers to be exact. Circle area/circumference (pi) and non-triple Pythagorean hypotenuses are genuinely irrational - this skill uses a real 2% tolerance-band for exactly those two cases, and still constructs everything else exact. See [DEVELOPMENT.md](https://github.com/andlo/ovos-skill-geometry-practice/blob/main/DEVELOPMENT.md).

### Depends on ovos-skill-geometry

For its glossary, formulas, and computation functions - the same relationship [ovos-skill-geography-practice](https://github.com/andlo/ovos-skill-geography-practice) has with [ovos-skill-geography](https://github.com/andlo/ovos-skill-geography).

38 tests, all passing (including automated coverage of every locale file across all 5 languages).
