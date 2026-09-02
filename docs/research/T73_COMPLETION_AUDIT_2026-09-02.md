# Trace-73 completion audit

Date: 2026-09-02

## Result

All load-bearing mathematical items P0, C, S and P3 are discharged in the
paper.  The smooth four-dimensional Poincare conclusion is therefore stated
unconditionally in the paper.

Lean remains deliberately narrower: its exported theorem still takes
`ExternalGeometry` and `CSExternalGeometry` arguments.  The paper supplies
those inputs mathematically; it does not claim that Lean formalizes smooth
four-manifold topology or skein-lasagna functoriality.

## Requirement-by-requirement evidence

| requirement | evidence | verdict |
|---|---|---|
| P0 actual manifold and collar | public AR scan; parameterized P0 witness; Section 6 | **DISCHARGED** |
| C actual MWW comparison | 44 product rectangles, representable trace theorem, completed BPW/BHPW shadow, divided beta/psi cocone; Section 7 | **DISCHARGED** |
| S three-handle closure | relative HJ system and intrinsic MWW local module action; Section 8 | **DISCHARGED** |
| P3 final joins | MWW three/four-handle formulas, standard-S4 support, Iwaki criterion; Section 9 | **DISCHARGED** |
| paper proof completeness | explicit proofs in Sections 3 and 6--9; status table has no OPEN/PARTIAL row | **DISCHARGED** |
| Lean scope honesty | `T73Conditional.lean` retains both external structures; new algebra has foundational axioms only | **DISCHARGED** |

## Negative statements retained

1. The historical full PD and TH files remain unavailable and unused.
2. The endpoint cap is not identified with the four W2 core disks.
3. The proof descends the divided cubic through W2; it does not claim a full-q
   W2 endpoint functional.
4. The Lean kernel does not check the cited smooth topology or link-homology
   functoriality.

These are scope boundaries, not remaining assumptions in the mathematical
theorem.

## Final gates

```text
python -B scripts/generate_t73_ar_product_witness.py --check --source-pdf AR.pdf
python -B scripts/generate_t73_c_comparison_witness.py --check
python -I -B tests/test_t73_ar_product_witness.py -v
python -I -B tests/test_t73_c_comparison_witness.py -v
python -I -B tests/test_t73_claim_boundary.py -v
python -I -B tests/test_t73_completion.py -v
```
