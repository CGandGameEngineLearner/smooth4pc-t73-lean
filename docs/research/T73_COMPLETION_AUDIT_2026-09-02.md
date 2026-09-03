# Trace-73 paper-only completion audit

Date: 2026-09-02

## Corrected result

The earlier same-day claim that every load-bearing item was discharged is
retracted.  The Johnson reconstruction, statewise coefficient construction,
and genus-zero hemisphere calculation now close P0, C and S:

| item | verdict | remaining obligation |
|---|---|---|
| P0 | **DISCHARGED** | The Johnson alpha-side lift gives a free-basis AR representative, exact compact m2, two framed cancellations, 44 rational lanes and an independently generated/re-extracted 11340-letter braid. |
| C | **DISCHARGED** | Equations (17) and (24)--(27) construct the product-ribbon coefficient maps and all-state beta/psi cocone; the witness is bound to the Johnson certificate. |
| S | **DISCHARGED** | The fixed-detector HJ move table supplies the spheres; diagram (30) and the all-$b$ genus-zero core-counit calculation (32) prove the six essential-sphere equations (31). |

P3 follows from the cited MWW four-handle theorem, standard $S^4$ support,
and Iwaki's Cappell--Shaneson criterion after the now-constructed joins.

## Why the compact witnesses do not close the theorem

The older AR JSON witness records parametrizations, framings, words, and
hashes and remains insufficient.  It is superseded for P0 by
`audit/t73_p0_johnson_certificate.json`, which uses Johnson splitting
generators and does not claim historical-PD identity.  The product Hattori
witness is now bound to that presentation, and the paper defines its maps at
every cable level.  Horvat--Jablonowski v3 supplies the relative move list;
the spotted-ball argument removes boundary slides outside the inner detector
ball.  Removing the actual two-handle core disks from each sphere leaves a
connected genus-zero cobordism; the Frobenius calculation (32), together with
cubic-order transport invariance, computes the essential $A_0,A_1$ actions.

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
