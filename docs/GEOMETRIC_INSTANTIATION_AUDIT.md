# Geometric and functorial instantiation audit

**Status:** `OPEN` (P0, C, S and the MWW four-handle layer discharged; \(X_J\cong\Sigma_A^0\) remains Open)

This file is subordinate to
`docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md`.  Historical PD/TH
artifacts are not premises.  No counterexample is claimed.

## Ordered verdicts

| priority / item | verdict | public evidence |
|---|---|---|
| P0 replacement AR presentation | **DISCHARGED** | Johnson reconstruction recovers the public word; not historical-PD identity |
| P1/C coefficient comparison | **DISCHARGED** | C1 product ribbons and C2 action cubes on the Johnson replacement collar |
| P2/E7 attaching spheres | **OPEN** | Closed HJ Theorem 5.3 is not used as “B is fixed”; Lemmas 5.5 and 5.7 are not in arXiv:2510.20282 |
| P2/E10/S three-handle quotient | **DISCHARGED** | Reversed 1-handle belt spheres miss the P0 cube and the C1 leftover link |
| P3/E11 four-handle | **DISCHARGED** | 1-3 cancellations and a PL 4-ball; MWW 3.4 on `X_J`, not `Sigma_A^0` |
| P3/E12 standard sphere | **DISCHARGED** | MWW Corollary 3.5 as a statement about `S^4` |
| P3/E13 homotopy sphere | **PARTIAL** | `det(A-I)=1` is proved; `X_J ≅ Sigma_A^0` remains Open |

Lean `ExternalGeometry` / `CSExternalGeometry` have no inhabitants.
`thm:joined` remains Conditional.

## Retired routes

The availability audit for `audit/geometric_evidence_manifest.json` still
reports historical objects as missing.  This is expected:

- the Johnson reconstruction replaces the PD/builder/framing route;
- the reversed 1-handle belt-sphere picture replaces TH1/TH2/THXY;
- the public C witness replaces the historical cable/Hattori artifact.

Hashes of retired files remain provenance only.
