# Final closure audit

**Status:** `OPEN` (P0, C, S, MWW four-handle layer and E13 CS handle picture discharged; Lean ExternalGeometry uninhabited; empty-link `S4ReductionData` inhabited)

See `docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md`.

## Current allocation

| item | verdict | evidence |
|---|---|---|
| P0 | **PASS** | Discrete Voronoi Heegaard pair, local cancellations, 44-strand reconstruction recovers the public word |
| C | **PASS** | P0-strand product ribbons and C2 comparison maps on the Johnson replacement collar |
| S | **PASS** | Reversed 1-handle belt spheres miss the P0 cube and the C1 leftover link; HJ 5.3 used only for kernel invariance |
| P3/E11 | **PASS** | 1-3 cancellations and a PL 4-ball; MWW 3.4 on `X_J` |
| P3/E12 | **PASS** | Empty-link Khovanov, PL \(S^4\) from two \(I^4\); degree 494 vanishes |
| P3/E13 | **PASS** | Constructed PL `psi`, railroad attaching link, reduced PD, and Kirby pipeline identify `X_J` with `Sigma_A^0` |

## Important negative boundaries

- The historical two-million-crossing PD remains unavailable and is unused.
- The historical TH1/TH2/THXY sphere files remain unavailable and are unused.
- The endpoint cap is not equal to the four W2 core disks.
- No full-formal-q W2 functional is asserted.  The finite cubic `2624` is
  computed.  The candidate 4-manifold is the constructed CS handle picture.
- Lean remains a conditional algebraic core; candidate `ExternalGeometry` has no
  inhabitant. The empty-link control inhabits `S4ReductionData`.
- Uniqueness of regular neighborhoods is not used.

## Replays

```text
python -B scripts/certify_t73_p0_johnson.py --check
python -B scripts/certify_t73_s_standard_spheres.py --check
python -B scripts/certify_t73_p3_four_handle.py --check
python -B scripts/certify_t73_e12_s4.py --check
python -B scripts/certify_t73_e13_close.py --check
python -B scripts/certify_t73_e13_identification.py --check
python -B tests/test_t73_e12_s4.py -v
python -B tests/test_t73_e13_close.py -v
python -B tests/test_t73_e13_identification.py -v
python -B tests/test_t73_p3_four_handle.py -v
python -B tests/test_t73_claim_boundary.py -v
```
