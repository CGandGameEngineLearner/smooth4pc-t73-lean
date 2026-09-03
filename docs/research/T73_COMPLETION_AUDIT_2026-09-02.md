# Trace-73 paper-only completion audit

Date: 2026-09-02

## Corrected result

The earlier same-day claim that every load-bearing item was discharged is
retracted.  The Johnson reconstruction, statewise coefficient construction,
and the new paper lemmas now close the candidate-specific identifications:

| item | verdict | remaining obligation |
|---|---|---|
| P0 | **DISCHARGED** | Paper Lemmas P0a--c supply the handlebody diffeomorphism, framed cancellations and MWW framing; the certificate supplies the replacement word. |
| C | **DISCHARGED** | Paper Lemmas C1/C2 identify the actual coefficient shadow and all-cable constant term; equations (24)--(27) give the cocone. |
| S | **DISCHARGED** | Paper Lemmas Ssystem/Sendpoint give total-kernel invariance and the actual essential-sphere endpoint square. |

P3 follows from the cited MWW four-handle theorem, standard S4 support and
Iwaki's criterion after P0--S.

## Why the compact witnesses do not close the theorem

The older AR JSON witness records parametrizations, framings, words, and
hashes and remains insufficient.  It is superseded for P0 by
`audit/t73_p0_johnson_certificate.json`, which uses Johnson splitting
generators and does not claim historical-PD identity.  The finite witnesses
remain insufficient by themselves.  Paper Lemma C1 supplies the actual
coefficient identification, Lemma C2 supplies the uniform cable expansion,
HJ Theorem 5.3 plus Lemma Ssystem avoids the relative boundary-slide issue,
and Lemma Sendpoint constructs the endpoint square from the actual cut
sphere movie.

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
