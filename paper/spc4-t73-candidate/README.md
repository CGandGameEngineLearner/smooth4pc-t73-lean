# Trace-73 Cappell--Shaneson paper

This directory contains an English `amsart` conditional preprint about the
trace-73 Cappell--Shaneson candidate.  Exact Artin--Magnus expansion and the
pure-braid Andreadakis equality verify a cubic-order statement for the public
braid, but the candidate-level Kirby, MWW comparison, and three-handle joins
are not all closed.  The relative standard-sphere theorem now derives the
three-handle join from P0 and the symmetric-monoidal form of C, so it is not an
independent hypothesis.

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

A proposed P0 replacement can be checked for the required embedded-witness
structure with:

```text
python -B scripts/check_t73_p0_embedded_witness.py PATH_TO_WITNESS.json
```

The compact word ledger is deliberately rejected by this checker because it
does not contain component parametrizations, normal fields, cancellation
movies, or an ambient detector-collar embedding.

The ordinary representable-coefficient reduction used inside the proposed C
comparison is proved in `Smooth4PC/RepresentableCoefficient.lean`; its
standalone axiom report is `T73RepresentableAudit.lean`.  This theorem does
not instantiate the actual product Hattori bimodule equivalence or its
quantum/completed lift.

It is expected to report the historical objects as missing.  Their absence is
still relevant to P0 and the old explicit-sphere route.  The relative
standard-sphere proof no longer consumes the TH1/TH2/THXY files.  Names and
SHA-256 values remain in `audit/geometric_evidence_manifest.json` and Appendix
A for provenance.
