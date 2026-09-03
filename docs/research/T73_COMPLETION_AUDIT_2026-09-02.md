# Trace-73 paper-only completion audit

Date: 2026-09-03

## Result

P0, C, S and the MWW four-handle layer are discharged for the explicit
Johnson replacement.  The identification of the closed picture `X_J` with
`Sigma_A^0` remains Open.  No counterexample is claimed.

| item | verdict | remaining obligation |
|---|---|---|
| P0 | **PASS** | Computational reconstruction recovers the public 11340-letter word. |
| C | **PASS** | Collar-bound product rectangles and C2 comparison maps. |
| S | **PASS** | Reversed 1-handle belt spheres miss the P0 cube and the C1 leftover link; chart returns miss every belt cube. |
| P3/E11 | **PASS** | 1-3 cancellations and a PL 4-ball; MWW 3.4 on `X_J`, not `Sigma_A^0`. |
| P3/E12 | **PASS** | MWW Corollary 3.5 as a statement about `S^4`. |
| P3/E13 | **PARTIAL** | `det(A-I)=1` is proved; `X_J ≅ Sigma_A^0` remains Open. |

`det(A-I)=1` and `D_3=2624` are finite facts.

## Formal boundary

The controlling Lean theorem remains an implication with external structures:

    ExternalGeometry -> CSExternalGeometry ->
    IsHomotopySphere candidate /\ not Diffeomorphic candidate S4.

Lean does not construct either external structure.
