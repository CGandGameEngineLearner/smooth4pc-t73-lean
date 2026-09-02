# Trace-73 Cappell--Shaneson paper

This directory contains the English `amsart` preprint for the compact trace-73
Cappell--Shaneson argument.  The compact presentation and comparison theorems
replace the historical large PD/TH artifacts.  Exact Artin--Magnus expansion
and the pure-braid Andreadakis equality verify cubic order for every physical
cabling.

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

The comparison with the MWW skein lasagna evaluation is proved through the
BPW/BHPW quantum horizontal trace and the compact Hattori construction.  The
paper keeps the Lean scope separate: Lean checks the finite and quotient
algebra but does not formalize smooth topology or link-homology functoriality.

The public availability check is:

```text
python -B scripts/check_geometric_evidence.py
```

It is expected to report the retired historical objects as missing.  The
compact proof does not consume them; their names and SHA-256 values remain in
`audit/geometric_evidence_manifest.json` and Appendix A for provenance.
