#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
paper_dir="$repo_root/paper/spc4-t73-candidate"
output_dir="$repo_root/output/pdf"
mode="${1:---english}"

mkdir -p "$output_dir"

build_english() {
  cd "$paper_dir"
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  bibtex main
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  cp main.pdf "$output_dir/.spc4-t73-candidate.new.pdf"
  mv -f "$output_dir/.spc4-t73-candidate.new.pdf" "$output_dir/spc4-t73-candidate.pdf"
  echo "Wrote $output_dir/spc4-t73-candidate.pdf"
}

case "$mode" in
  --english)
    build_english
    ;;
  --zh)
    "$repo_root/scripts/build_zh_paper.sh"
    ;;
  --all)
    build_english
    "$repo_root/scripts/build_zh_paper.sh"
    ;;
  *)
    echo "usage: $0 [--english|--zh|--all]" >&2
    exit 2
    ;;
esac
