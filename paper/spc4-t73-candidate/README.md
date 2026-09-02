# Trace-73 Cappell--Shaneson paper

This directory contains an English `amsart` conditional preprint about the
trace-73 Cappell--Shaneson candidate.  Exact Artin--Magnus expansion and the
pure-braid Andreadakis equality verify a cubic-order statement for the public
braid.  The public AR product witness closes the candidate-level Kirby
identification, and the relative standard-sphere theorem derives the
three-handle join from the symmetric-monoidal form of C.  The remaining open
core is the candidate-level MWW coefficient comparison C.

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

A public P0 replacement can be regenerated and checked with:

```text
python -B scripts/generate_t73_ar_product_witness.py --check \
  --source-pdf PATH_TO_PUBLIC_AR_SCAN
python -B scripts/check_t73_p0_embedded_witness.py \
  audit/t73_ar_product_witness.json
python -I -B tests/test_t73_ar_product_witness.py -v
```

The compact word ledger alone is deliberately rejected; the AR witness adds
the simultaneous component parametrizations, normal fields, cancellation
movies and ambient detector-collar embedding.

The ordinary representable-coefficient reduction used inside the proposed C
comparison is proved in `Smooth4PC/RepresentableCoefficient.lean`; its
standalone axiom report is `T73RepresentableAudit.lean`.  This theorem does
not instantiate the actual product Hattori bimodule equivalence or its
quantum/completed lift.

The availability script still reports the historical objects as missing.
They are retired: the public AR replacement discharges P0, and the relative
standard-sphere proof does not consume TH1/TH2/THXY.  Names and SHA-256 values
remain in `audit/geometric_evidence_manifest.json` and Appendix A for
provenance.
