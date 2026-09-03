#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER="$ROOT/paper/spc4-t73-candidate"
OUT="$ROOT/output/pdf"

python3 -B "$ROOT/scripts/assemble_main_zh.py"

cd "$PAPER"
lualatex -interaction=nonstopmode main-zh.tex
bibtex main-zh
lualatex -interaction=nonstopmode main-zh.tex
lualatex -interaction=nonstopmode main-zh.tex

mkdir -p "$OUT"
cp main-zh.pdf "$OUT/spc4-t73-candidate-zh.pdf"
echo "Wrote $OUT/spc4-t73-candidate-zh.pdf"
