# Final closure audit

**Status:** `OPEN` (P0, C, S and the MWW four-handle layer discharged; \(X_J\cong\Sigma_A^0\) remains Open)

See `docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md`.

## Current allocation

| item | verdict | evidence |
|---|---|---|
| P0 | **PASS** | Discrete Voronoi Heegaard pair, local cancellations, 44-strand reconstruction recovers the public word |
| C | **PASS** | P0-strand product ribbons and C2 comparison maps on the Johnson replacement collar |
| S | **PASS** | Reversed 1-handle belt spheres miss the P0 cube and the C1 leftover link; HJ 5.3 used only for kernel invariance |
| P3/E11 | **PASS** | 1-3 cancellations and a PL 4-ball; MWW 3.4 on `X_J`, not `Sigma_A^0` |
| P3/E12 | **PASS** | MWW Corollary 3.5 as a statement about `S^4` |
| P3/E13 | **PARTIAL** | `det(A-I)=1` is proved; `X_J ≅ Sigma_A^0` remains Open |

## Important negative boundaries

- The historical two-million-crossing PD remains unavailable and is unused.
- The historical TH1/TH2/THXY sphere files remain unavailable and are unused.
- The endpoint cap is not equal to the four W2 core disks.
- No full-formal-q W2 functional is asserted.  The finite cubic `2624` is
  computed; `X_J` is not identified with `Sigma_A^0`, so there is no
  candidate-level cocone.
- Lean remains a conditional algebraic core; `ExternalGeometry` has no
  inhabitant.
- Uniqueness of regular neighborhoods is not used.

## Replays

```text
python -B scripts/certify_t73_p0_johnson.py --check
python -B scripts/certify_t73_s_standard_spheres.py --check
python -B scripts/certify_t73_p3_four_handle.py --check
python -B tests/test_t73_p3_four_handle.py -v
python -B tests/test_t73_claim_boundary.py -v
```
