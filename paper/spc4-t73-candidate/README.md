# Trace-73 Cappell--Shaneson paper

This directory contains an English `amsart` conditional preprint about the
trace-73 Cappell--Shaneson candidate.  Exact Artin--Magnus expansion and the
pure-braid Andreadakis equality verify a cubic-order statement for the public
braid, but the candidate-level Kirby, MWW comparison, and three-handle joins
remain explicit hypotheses.

## Build

From this directory in WSL:

```text
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
mkdir -p ../../output/pdf
cp main.pdf ../../output/pdf/spc4-t73-candidate.pdf
```

The repository build places the reviewed PDF at
`output/pdf/spc4-t73-candidate.pdf`.  Replace the provisional author block and
add submission metadata before an arXiv upload.  The draft must not be
advertised as a disproof of smooth four-dimensional Poincare.

## Evidence boundary

The comparison with the MWW skein lasagna evaluation is a named hypothesis.
The available BPW/BHPW results and compact Hattori counts do not yet construct
the required candidate-specific natural map or simultaneous transport.  Lean
checks finite and quotient algebra but neither constructs the external
geometry structures nor formalizes smooth topology/link-homology
functoriality.

The public availability check is:

```text
python -B scripts/check_geometric_evidence.py
```

The paper/evidence consistency gate is:

```text
python -B scripts/check_t73_claim_boundary.py
```

It is expected to report the historical objects as missing.  Their absence is
still relevant to P0/P2; the compact ledgers do not presently replace the
missing embedded geometric certificates.  Names and SHA-256 values remain in
`audit/geometric_evidence_manifest.json` and Appendix A for provenance.
