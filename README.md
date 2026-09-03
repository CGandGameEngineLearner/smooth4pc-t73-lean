# Smooth4PC T73 counterexample / falsification package

[中文说明](README.zh-CN.md)

This repository presents a **candidate disproof of the smooth four-dimensional
Poincare conjecture, pending independent external review**.  The proposed
counterexample is the Cappell--Shaneson manifold `X(41,189,73)`, claimed to be
a homotopy four-sphere not diffeomorphic to the standard `S^4`.

The proposed distinguishing class has quantum degree `494`. Its divided cubic
detector evaluates to `2624`, whereas the corresponding degree of the
standard four-sphere module is zero. The finite calculation and the abstract
quotient implication are checked in Lean; the candidate-specific geometric
identifications and the cited topology theorems remain explicit inputs rather
than hidden axioms.

**Erratum (2 September 2026).** The former value `-59072` was wrong because
the endpoint vector and covector were read from two different index tables.
After both are expressed in the collar table used by the braid word, the exact
value is `+2624`, which is still nonzero. Both the numerical detector and the
proposed disproof remain conditional on the uncertified assumptions stated in
the paper; I am continuing to work on those premises.

That distinction matters: a successful Lean build verifies the implication
encoded by the repository. It does not, by itself, certify that every
geometric input has been formalized. The exact boundary is visible in
[`Smooth4PC/T73External.lean`](Smooth4PC/T73External.lean).

## PDF for public review

[PDF prepared for public review](paper/T73_SPC4_CANDIDATE_FALSIFICATION_20260902.pdf)

## Start here

1. Read [`docs/INDEPENDENT_REVIEW.md`](docs/INDEPENDENT_REVIEW.md) for the
   three-step proof chain, the published-source map and the review boundary.
2. Follow [`REPRODUCING.md`](REPRODUCING.md) to build from a fresh clone, audit
   all reported axioms and independently recompute the detector.
3. Use
   [`docs/proofs/T73_COUNTEREXAMPLE_MATERIALS_INDEX.md`](docs/proofs/T73_COUNTEREXAMPLE_MATERIALS_INDEX.md)
   to enter the full proof and evidence tree.

The proof manuscript itself is
[`docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md`](docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md).

## Reproducibility contract

- Lean toolchain: `leanprover/lean4:v4.32.1`
- mathlib revision: `520045ab14e26149ee970e2e617ca04b09bde5d6`
- Python: 3.10 or later
- expected axiom reports: `38`
- allowed reported axioms: `propext`, `Classical.choice`, `Quot.sound`
- `sorryAx`: absent
- expected detector value: `2624`

The committed `lake-manifest.json` pins all Lean dependencies. Build products,
local dependency copies and old probe files are not part of the source tree.

## Scope

This is a public verification package, not a claim of peer acceptance. The
most useful adverse review is one that attacks the candidate-specific
geometric bindings in the independent-review note, not one that merely reruns
the already checked integer arithmetic.

## Why this is being released on GitHub first

GitHub is being used as the first public release channel for reasons of access,
speed and reproducibility—not as a substitute for scholarly review. My
existing arXiv submission history is in computer science, and I may not
currently have the endorsement required for the relevant mathematics category.
This repository therefore makes the full argument, Lean sources, exact inputs
and replay instructions publicly inspectable now. If the work receives
substantive mathematical scrutiny and assistance, I intend to prepare a
conventional preprint and submit it through the appropriate scholarly channel.

## License

The repository is released under the [MIT License](LICENSE).
