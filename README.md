# Smooth4PC T73 — conditional skein-lasagna obstruction

[中文说明](README.zh-CN.md)

This repository supports a **conditional** skein-lasagna obstruction for the
trace-73 Cappell--Shaneson homotopy 4-sphere associated with
\[
A=\begin{pmatrix}0&269&1240\\0&41&189\\1&0&32\end{pmatrix}
\]
(Iwaki standard form \(X_{41,189,73}\)).

**No counterexample to the smooth four-dimensional Poincaré conjecture is
claimed.** The controlling manuscript is
[`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
(*A conditional skein-lasagna obstruction for a trace-73 Cappell--Shaneson
sphere*).

## What is proved, and what is open

For an explicit **Johnson-generator** handle presentation the paper proves the
geometric inputs **P0, C, S, and P3** needed for a skein-lasagna comparison at
quantum degree \(494\), including the identification \(X_J\cong\Sigma_A^0\).

An exact finite calculation gives a nonzero divided cubic \(D_3=2624\). An
Artin--Magnus certificate and the pure-braid Andreadakis theorem establish a
third-order property of the public braid word.

A Lean development formalizes the **abstract quotient argument**: given
interface data assembling the MWW quotients and four-handle transport
(`ExternalGeometry`), a nonzero degree-\(494\) class would obstruct
diffeomorphism with \(S^4\). Those geometric interfaces are **not** constructed
in Lean.

| Layer | Status |
| --- | --- |
| Finite algebra (\(2624\), degree \(494\), \(\det A=\det(A-I)=1\)) | Checked in Lean |
| Abstract conditional implication | Checked in Lean |
| Johnson P0 / C / S / P3 (paper geometry + certificates) | Discharged in the paper |
| Lean inhabitant of `ExternalGeometry` | **Open** |

The exact Lean boundary is
[`Smooth4PC/T73External.lean`](Smooth4PC/T73External.lean). Premises audit:

```text
python3 scripts/audit_t73_premises.py --check
```

Expected summary: `P0/C/S/P3=PASS`, `OVERALL=OPEN`, `COUNTEREXAMPLE=False`.

**Erratum (2 September 2026).** An earlier draft mixed two endpoint index
tables and reported \(-59072\). With both objects in the collar table used by
the braid word, the exact value is \(+2624\) (still nonzero).

## PDFs for review

- English: [`output/pdf/spc4-t73-candidate.pdf`](output/pdf/spc4-t73-candidate.pdf)
- Chinese: [`output/pdf/spc4-t73-candidate-zh.pdf`](output/pdf/spc4-t73-candidate-zh.pdf)

Paper sources and build notes:
[`paper/spc4-t73-candidate/README.md`](paper/spc4-t73-candidate/README.md).

## Start here

1. Read the paper abstract and §3 (precise statements) in
   [`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
   or the English PDF above.
2. Follow [`REPRODUCING.md`](REPRODUCING.md) to build from a fresh clone, audit
   reported axioms, and recompute the detector.
3. For the independent-review boundary map, see
   [`docs/INDEPENDENT_REVIEW.md`](docs/INDEPENDENT_REVIEW.md).

## Reproducibility contract

- Lean toolchain: `leanprover/lean4:v4.32.1`
- mathlib revision: `520045ab14e26149ee970e2e617ca04b09bde5d6`
- Python: 3.10 or later
- expected axiom reports: `38`
- allowed reported axioms: `propext`, `Classical.choice`, `Quot.sound`
- `sorryAx`: absent
- expected detector value: `2624`

The committed `lake-manifest.json` pins Lean dependencies. Build products and
local dependency copies are not part of the source contract.

## Scope

This is a public verification package for a **conditional** obstruction, not a
claim of peer acceptance and not a claimed counterexample. The most useful
adverse review attacks the Johnson geometric bindings and the remaining Lean
`ExternalGeometry` assembly, not the already checked integer arithmetic.

## Why this is being released on GitHub first

GitHub is the first public release channel for access, speed and
reproducibility—not a substitute for scholarly review. Existing arXiv history
is in computer science; mathematics-category endorsement may be unavailable.
The full argument, Lean sources, certificates and replay instructions are
inspectable here. After substantive scrutiny, a conventional preprint
submission is intended.

## License

The repository is released under the [MIT License](LICENSE).
