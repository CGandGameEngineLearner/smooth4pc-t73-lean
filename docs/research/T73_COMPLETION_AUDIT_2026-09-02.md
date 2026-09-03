# Trace-73 paper-only completion audit

Date: 2026-09-02

## Corrected result

The earlier same-day claim that every load-bearing item was discharged is
retracted.  The Johnson reconstruction, statewise coefficient construction,
and genus-zero hemisphere calculation still leave candidate-specific
identifications to be checked:

| item | verdict | remaining obligation |
|---|---|---|
| P0 | **OPEN** | The Johnson certificate gives a replacement mapping-class word and finite braid data, but P0a--c remain unproved. |
| C | **OPEN** | Equations (17) and (24)--(27) are a conditional construction; actual MWW coefficient identification C1 and all-cable C2 remain unproved. |
| S | **OPEN** | HJ/MWW give the formal setup, but the fixed-detector realization and actual essential-sphere endpoint square remain unproved. |

P3 remains conditional on P0--S; E12 and the matrix-only E13 statement are
independent.

## Why the compact witnesses do not close the theorem

The older AR JSON witness records parametrizations, framings, words, and
hashes and remains insufficient.  It is superseded for P0 by
`audit/t73_p0_johnson_certificate.json`, which uses Johnson splitting
generators and does not claim historical-PD identity.  The product Hattori
witness is bound to that presentation only at certificate level; the paper
defines conditional maps at every cable level.  Horvat--Jablonowski v3
supplies the relative move list but not the candidate fixed-detector
realization.  Removing core disks and applying Frobenius would compute the
sphere actions only after the missing actual endpoint exchange square exists.

The committed m2 word has length 311 and remains length 311 after linear and
cyclic free reduction. A reported length 309 therefore reflects a different
convention or input; this discrepancy is not the load-bearing obstruction.

## Formal boundary

The controlling Lean theorem remains an implication with external structures:

    ExternalGeometry -> CSExternalGeometry ->
    IsHomotopySphere candidate /\ not Diffeomorphic candidate S4.

The Lean algebra does not construct either external structure; Sections 6--9
prove their mathematical instances outside Lean.  The claim-boundary gate
checks this allocation but is not a substitute for reviewing those proofs.
