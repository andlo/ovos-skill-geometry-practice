# Geometry Practice — a design document, not a working skill yet

**Status: idea and architecture stage.** Part of the `*-practice`
family. Split out as its own skill rather than folded into
`ovos-skill-math-practice` or `ovos-skill-science-practice` - see
[ovos-skill-math-practice issue #6](https://github.com/andlo/ovos-skill-math-practice/issues/6)
for the scope discussion that led here.

## The idea

Named theorems (Pythagoras' theorem), area/perimeter/volume formulas,
and similar geometric results - genuinely different from
`math-practice`'s arithmetic-fluency drilling (+/-/x/÷) and from
`science-practice`'s "well-defined, stable trivia" (physical
constants, the periodic table): geometry blends FACTUAL recall (the
formula itself) with actually APPLYING it numerically. "A triangle
has legs 3 and 4, what's the hypotenuse" needs both "know the
formula" and "do the arithmetic" - neither half alone is the
exercise.

## Likely scope (not yet decided in detail)

- **Named theorems**: Pythagoras' theorem to start (`a² + b² = c²`)
  - the clearest "formula + apply it" example. Others (e.g. the law
  of cosines) are plausible later additions, not v1.
- **Area/perimeter formulas**: rectangle, triangle, circle - both
  "recite the formula" (teach mode) and "apply it to these numbers"
  (quiz mode), mirroring `math-practice`'s teach-then-practice split.
- **Volume formulas**: cube, cylinder, sphere - probably a second
  pass after 2D shapes are solid, not launched simultaneously.
- Likely NOT in scope for v1: trigonometry beyond Pythagoras,
  coordinate geometry, proofs. Keep the exercise "know the formula,
  apply it to concrete numbers" - anything requiring multi-step
  derivation is a different, harder exercise than this skill's
  starting scope.

## Real, open design questions

- **Grading tolerance for non-integer results.** `√(3²+4²) = 5` is a
  clean example, but most triangles won't have integer hypotenuses -
  "what's the hypotenuse of a triangle with legs 5 and 7" has an
  irrational answer. This is the SAME open tolerance-band question
  raised in
  [ovos-skill-unit-practice](https://github.com/andlo/ovos-skill-unit-practice)'s
  design doc and
  [ovos-skill-math-practice issue #5](https://github.com/andlo/ovos-skill-math-practice/issues/5)
  (fractions/decimals) - worth designing the tolerance approach once,
  in whichever of the three lands first, and having the other two
  reuse it rather than solving it three times independently.
- **Problem generation with clean-by-construction numbers.**
  `math-practice`'s pattern is to construct problems so the answer is
  guaranteed exact (e.g. division built as divisor × quotient) rather
  than relying on tolerance. For Pythagoras specifically, Pythagorean
  triples (3-4-5, 5-12-13, 8-15-17, ...) give exact integer answers
  for free - worth generating FROM a known triple (possibly scaled)
  rather than picking two random legs and rounding the hypotenuse,
  at least for an "easy" difficulty tier. Non-triple legs (needing
  real tolerance-band grading) would be a separate, harder tier.
- **Teach mode content.** Does teach mode recite the formula itself
  ("the area of a rectangle is length times width"), or a set of
  worked examples the same way `math-practice` teaches facts rows?
  Probably needs both - formula first, then example rows - but not
  designed here yet.
- **Spoken problem phrasing.** "A triangle has legs 3 and 4, what's
  the hypotenuse" is fine written down; whether it's parsed
  unambiguously as spoken input (which number is which leg, is "legs"
  even in a listener's spoken response) isn't tested yet - same class
  of concern as
  [ovos-skill-math-practice issue #4](https://github.com/andlo/ovos-skill-math-practice/issues/4)'s
  spoken-ambiguity flag for order-of-operations questions.

## Example exercises (illustrative, not final wording)

```
"teach me pythagoras' theorem"
"quiz me on pythagoras"
"what is the area of a triangle with base 6 and height 4"
"quiz mig i pythagoras' sætning"
```

## Shared pattern: teach-then-practice

Once implementation starts, this skill should adopt the "teach, then
quiz on what was taught" pattern designed on `ovos-skill-math-practice`
(see [issue #1](https://github.com/andlo/ovos-skill-math-practice/issues/1))
rather than re-deriving the same architecture slightly differently
here. Not re-designed in this README to avoid the same pattern
existing in a slightly different shape in every `*-practice` sibling
- the shared design lives in one place and every sibling points back
to it.

## Category
**Education**

## Tags
#geometry #math #education #quiz #idea #design-doc
