# Compact Burau--MWW comparison

**Status:** `DISCHARGED`

The P0 normal fields turn the word-level counts into actual product
rectangles.  The deterministic pairing witness verifies:

```text
m2 y/z pairs: 42
rxy y/z pairs: 2
total product rectangles: 44
remaining z circles: 227
```

These rectangles induce the action-compatible Hattori coefficient
equivalence used in Theorem C.  Endpoint labels are chosen after one common
pivotal transport of the operator, cup, and cap.  Mixed orientations differ
from the all-positive BPW model by zero-writhe grading shifts and simultaneous
pivotal conjugation, so the pairing is unchanged.

The local checked R-matrix becomes the public unreduced Burau block after
`t=q^-2`.  Exact order-three divisibility holds on all 7,744 endpoint matrix
entries.  The four possible constant cup/cap signs yield

```text
-53824, -53760, -59008, -59072,
```

so nonvanishing is convention independent.

The full proof, including q-completion and the divided beta/psi cocone, is in
Section 7 of the paper and
`docs/research/T73_C_DISCHARGE_2026-09-02.md`.
