# Geometric and functorial instantiation audit

**Status:** `DISCHARGED BY PUBLIC REPLACEMENT ROUTES`

This file is the current audit from the conditional Lean implication to the
mathematical instances supplied in the paper.  Historical PD/TH artifacts are
not premises.

## Ordered verdicts

Only `DISCHARGED`, `PARTIAL`, and `OPEN` are used.

| priority / item | verdict | public evidence |
|---|---|---|
| P0 replacement AR presentation | **DISCHARGED** | public AR scan; `audit/t73_ar_product_witness.json`; complete Section 6 proof |
| P1/C coefficient comparison | **DISCHARGED** | `audit/t73_c_comparison_witness.json`; representable Lean theorem; complete Section 7 proof |
| P2/E7 attaching spheres | **DISCHARGED** | P0 handle pattern and detector ball; HJ Theorem 5.3 and relative uniqueness |
| P2/E10/S three-handle quotient | **DISCHARGED** | MWW local module action; monoidal divided detector; complete Section 8 proof |
| P3/E11 four-handle | **DISCHARGED** | MWW Proposition 3.4 |
| P3/E12 standard sphere | **DISCHARGED** | MWW Corollary 3.5 |
| P3/E13 homotopy sphere | **DISCHARGED** | P0 plus Iwaki Proposition 2.1 |

No load-bearing `OPEN` or `PARTIAL` item remains.

## Lean field allocation

| Lean obligation | mathematical instance |
|---|---|
| `x0, ell0, ell0_x0` | actual Hattori class and divided endpoint row from Theorem C |
| `q01, ell1_comp_q01` | complete divided beta/psi cocone |
| `q12, ell2_comp_q12` | relative standard spheres and MWW local sphere action |
| `transport, fourIso` | MWW three-/four-handle formulas |
| `s4DegreeZero` | rational degree-494 consequence of the standard S4 computation |
| `diffeomorphismEquiv` | intrinsic graded diffeomorphism invariance |
| `matrixConditionsToHomotopySphere` | P0 identification and the CS determinant criterion |

The Lean files do not define smooth topology or lasagna functoriality.  Their
structures remain parameters in the kernel statement; Sections 6--9 provide
the corresponding mathematical constructions.

## Retired routes

The availability audit for `audit/geometric_evidence_manifest.json` still
reports historical objects as missing.  This is expected and does not
contradict the verdicts above:

- the public AR product witness replaces the PD/builder/framing route;
- the relative sphere theorem replaces TH1/TH2/THXY;
- the public C witness replaces the historical cable/Hattori artifact.

Hashes of retired files remain provenance only.
