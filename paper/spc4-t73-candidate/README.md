# Trace-73 Cappell--Shaneson paper

This directory contains an English `amsart` preprint proving that the
trace-73 Cappell--Shaneson sphere is nonstandard.  Exact Artin--Magnus expansion and the
pure-braid Andreadakis equality verify a cubic-order statement for the public
braid.  The public AR product witness closes the candidate-level Kirby
identification, the product-pairing witness gives the MWW coefficient
comparison C, and the relative standard-sphere theorem supplies the
three-handle join.

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
add submission metadata before an arXiv upload.

## Evidence boundary

The comparison with the MWW skein lasagna evaluation is constructed from the
44 public product rectangles, BPW/BHPW functoriality, and the divided
beta/psi cocone.  Lean checks finite and quotient algebra; the smooth topology
and link-homology functoriality are supplied by the paper rather than
formalized in Lean.

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
standalone axiom report is `T73RepresentableAudit.lean`.  The actual product
pairing and completed comparison are regenerated with:

```text
python -B scripts/generate_t73_c_comparison_witness.py --check
python -I -B tests/test_t73_c_comparison_witness.py -v
```

The availability script still reports the historical objects as missing.
They are retired: the public AR, coefficient-comparison, and relative-sphere
replacements discharge their old roles.  Names and SHA-256 values remain in
`audit/geometric_evidence_manifest.json` and Appendix A for provenance.
