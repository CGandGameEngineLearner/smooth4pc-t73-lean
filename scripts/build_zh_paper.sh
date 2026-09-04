#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER="$ROOT/paper/spc4-t73-candidate"
OUT="$ROOT/output/pdf"

cd "$PAPER"
# Do not use -halt-on-error: luatexja+Fandol emits recoverable \textfont7
# math-font noise that still yields a usable PDF under nonstopmode.
lualatex -interaction=nonstopmode main-zh.tex
bibtex main-zh
lualatex -interaction=nonstopmode main-zh.tex
lualatex -interaction=nonstopmode main-zh.tex

mkdir -p "$OUT"
cp main-zh.pdf "$OUT/.spc4-t73-candidate-zh.new.pdf"
mv -f "$OUT/.spc4-t73-candidate-zh.new.pdf" "$OUT/spc4-t73-candidate-zh.pdf"
echo "Wrote $OUT/spc4-t73-candidate-zh.pdf"
