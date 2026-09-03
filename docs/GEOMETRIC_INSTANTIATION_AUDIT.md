# Geometric and functorial instantiation audit

**Status:** `OPEN` (P0, C, S, MWW four-handle layer and E13 CS handle picture discharged; Lean ExternalGeometry uninhabited; empty-link `S4ReductionData` inhabited)

This file is subordinate to
`docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md`.  Historical PD/TH
artifacts are not premises.  No counterexample is claimed.

## Ordered verdicts

| priority / item | verdict | public evidence |
|---|---|---|
| P0 replacement AR presentation | **DISCHARGED** | Johnson reconstruction recovers the public word; not historical-PD identity |
| P1/C coefficient comparison | **DISCHARGED** | C1 product ribbons and C2 action cubes on the Johnson replacement collar |
| P2/E7 attaching spheres | **UNUSED** | Closed HJ Theorem 5.3 is not used as “B is fixed”; S uses the reversed belt-sphere picture. Lemmas 5.5 and 5.7 are not in arXiv:2510.20282 |
| P2/E10/S three-handle quotient | **DISCHARGED** | Reversed 1-handle belt spheres miss the P0 cube and the C1 leftover link |
| P3/E11 four-handle | **DISCHARGED** | 1-3 cancellations and a PL 4-ball; MWW 3.4 on `X_J` |
| P3/E12 standard sphere | **DISCHARGED** | Empty-link Khovanov and PL \(S^4=I^4\cup_{S^3}I^4\); Lean empty-link `S4ReductionData` inhabited |
| P3/E13 homotopy sphere | **DISCHARGED** | Constructed PL `psi`, railroad attaching link, reduced PD, Kirby pipeline; Lean `CSTopologyData` uninhabited |

Lean `ExternalGeometry` / `CSExternalGeometry` have no candidate inhabitants.
The empty-link control inhabits `S4ReductionData` in `T73S4Inhabitant.lean`.
`thm:joined` remains Conditional on a candidate `ExternalGeometry`.

## Retired routes

The availability audit for `audit/geometric_evidence_manifest.json` still
reports historical objects as missing.  This is expected:

- the Johnson reconstruction replaces the PD/builder/framing route;
- the reversed 1-handle belt-sphere picture replaces TH1/TH2/THXY.
