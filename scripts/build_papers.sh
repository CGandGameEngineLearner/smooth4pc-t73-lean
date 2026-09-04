#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
paper_dir="$repo_root/paper/spc4-t73-candidate"
output_dir="$repo_root/output/pdf"
mode="${1:---english}"

# Make the reviewed PDFs byte-reproducible instead of embedding wall-clock
# timestamps on every local rebuild.
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -C "$repo_root" log -1 --format=%ct -- paper/spc4-t73-candidate/main.tex)}"
export FORCE_SOURCE_DATE=1
export TZ=UTC

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
