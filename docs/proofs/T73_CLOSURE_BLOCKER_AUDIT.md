# Final closure audit

**Status:** `CONDITIONAL_NOT_CLOSED`

## Current allocation

| item | verdict | evidence |
|---|---|---|
| P0 | **OPEN** | Johnson splitting lift and finite replacement braid pass, but P0a--c remain unproved |
| C | **OPEN** | The 44-rectangle Hattori and statewise cocone are conditional on C1/C2 |
| S | **OPEN** | HJ/MWW formal setup exists, but fixed-detector and essential-sphere endpoint maps remain unproved |
| P3/E11 | **PARTIAL** | MWW four-handle isomorphism is general, but candidate application depends on P0/C/S |
| P3/E12 | **DISCHARGED** | MWW standard-S4 module concentrated in bidegree zero |
| P3/E13 | **DISCHARGED** | P0 manifold identification plus Iwaki's determinant criterion |

## Important negative boundaries

- The historical two-million-crossing PD remains unavailable and is unused.
- The historical TH1/TH2/THXY sphere files remain unavailable and are unused.
- The endpoint cap is not equal to the four W2 core disks.
- No full-formal-q W2 functional is asserted.  The proved object is the
  leading divided cubic cocone, which is exactly the strength needed for the
  ordinary rational lasagna module.
- Lean remains a conditional algebraic core; the missing candidate topology
  and functoriality inputs are not supplied by the paper.

## Replays

```text
python -B scripts/generate_t73_ar_product_witness.py --check --source-pdf AR.pdf
python -B scripts/generate_t73_c_comparison_witness.py --check
python -I -B tests/test_t73_ar_product_witness.py -v
python -I -B tests/test_t73_c_comparison_witness.py -v
python -I -B tests/test_t73_claim_boundary.py -v
```

The detailed proofs are Sections 6--9 of the paper.
