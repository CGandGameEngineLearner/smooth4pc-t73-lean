# Final closure audit

**Status:** `OPEN` (P0 and C discharged; S remains Open)

See `docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md`.

## Current allocation

| item | verdict | evidence |
|---|---|---|
| P0 | **PASS** | Discrete Voronoi Heegaard pair, local cancellations, 44-strand reconstruction recovers the public word |
| C | **PASS** | P0-strand product ribbons and C2 comparison maps on the Johnson replacement collar |
| S | **OPEN** | Kernel unknots and Nielsen generator movies miss the P0 cube, but there is no B-fixing move list from the actual attaching system |
| P3/E11 | **OPEN** | MWW Proposition 3.4 applies only after P0--S |
| P3/E12 | **CITED_EXTERNAL** | MWW Corollary 3.5 as a statement about S^4 |
| P3/E13 | **PARTIAL** | det(A-I)=1 is proved; the Johnson replacement is the discharged P0 presentation |

## Important negative boundaries

- The historical two-million-crossing PD remains unavailable and is unused.
- The historical TH1/TH2/THXY sphere files remain unavailable and are unused.
- The endpoint cap is not equal to the four W2 core disks.
- No full-formal-q W2 functional is asserted.  The finite cubic `2624` is
  computed; S remains Open, so there is no candidate-level cocone.
- Lean remains a conditional algebraic core; `ExternalGeometry` has no
  inhabitant.
- Uniqueness of regular neighborhoods is not used.

## Replays

```text
python -B scripts/certify_t73_p0_johnson.py --check
python -B scripts/generate_t73_ar_product_witness.py --check --source-pdf AR.pdf
python -B scripts/generate_t73_c_comparison_witness.py --check
python -I -B tests/test_t73_ar_product_witness.py -v
python -I -B tests/test_t73_c_comparison_witness.py -v
python -I -B tests/test_t73_claim_boundary.py -v
```

C remains discharged only for the Johnson replacement collar; S remains Open; see
`docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md`.
