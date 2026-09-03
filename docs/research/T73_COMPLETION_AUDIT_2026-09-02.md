# Trace-73 paper-only completion audit

Date: 2026-09-03

## Result

P0, C, S, the MWW four-handle layer and the E13 CS handle picture are
discharged for the explicit Johnson replacement.  Lean ExternalGeometry
remains uninhabited.  The empty-link control `S4ReductionData` is inhabited
in `Smooth4PC/T73S4Inhabitant.lean`.  No counterexample is claimed.

| item | verdict | remaining obligation |
|---|---|---|
| P0 | **PASS** | Computational reconstruction recovers the public 11340-letter word. |
| C | **PASS** | Collar-bound product rectangles and C2 comparison maps. |
| S | **PASS** | Reversed 1-handle belt spheres miss the P0 cube and the C1 leftover link; chart returns miss every belt cube. |
| P3/E11 | **PASS** | 1-3 cancellations and a PL 4-ball; MWW 3.4 on `X_J`. |
| P3/E12 | **PASS** | Empty-link Khovanov, PL \(S^4\) from two \(I^4\), degree 494 vanishes. Lean empty-link `S4ReductionData` inhabited; candidate `ExternalGeometry` uninhabited. |
| P3/E13 | **PASS** | Constructed PL `psi`, railroad attaching link, reduced PD, and Kirby pipeline identify `X_J` with `Sigma_A^0`. Lean `CSTopologyData` uninhabited. |

`det(A-I)=1` and `D_3=2624` are finite facts.

## Formal boundary

The controlling Lean theorem remains an implication with external structures:

    ExternalGeometry -> CSExternalGeometry ->
    IsHomotopySphere candidate /\ not Diffeomorphic candidate S4.

Lean does not construct either external structure for the Johnson candidate.
The empty-link control universe inhabits `S4ReductionData` only.
