# Trace-73 Cappell--Shaneson paper

This directory contains an English `amsart` preprint stating a conditional
obstruction for a trace-73 Cappell--Shaneson candidate.  Exact
Artin--Magnus expansion and the pure-braid Andreadakis equality verify a
cubic-order statement for the public braid.  The paper does not claim an
unconditional counterexample: P0, C, and S retain candidate-specific
geometric and functorial gaps.

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

The proposed comparison with the MWW skein lasagna evaluation uses the 44
public product rectangles, BPW/BHPW functoriality, and the divided beta/psi
cocone.  The committed data check the abstract algebraic shape, but do not
construct the actual candidate MWW chain/foam maps or all naturality squares.
Lean checks finite and quotient algebra; it neither supplies the missing
smooth topology nor formalizes four-dimensional differential topology.

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

The compact word ledger alone is deliberately insufficient.  The AR witness
adds symbolic simultaneous component parametrizations, normal fields and
cancellation data, but no independently checkable ambient embedding theorem
for the framed detector collar in the actual reduced Kirby link.  Moreover,
the public 11340-letter word is regenerated from crossing rows whose
provenance is the unavailable historical planar diagram; it is not derived
as the relative-endpoint braid of the selected AR passages.

The ordinary representable-coefficient reduction used inside the proposed C
comparison is proved in `Smooth4PC/RepresentableCoefficient.lean`; its
standalone axiom report is `T73RepresentableAudit.lean`.  The finite product
pairing ledger is regenerated with:

```text
python -B scripts/generate_t73_c_comparison_witness.py --check
python -I -B tests/test_t73_c_comparison_witness.py -v
```

The availability script still reports the historical objects as missing.
The public replacement ledgers do not discharge the missing candidate-level
embedding, MWW comparison, or fixed-detector sphere argument.  Names and
SHA-256 values remain in `audit/geometric_evidence_manifest.json` and
Appendix A for provenance.
