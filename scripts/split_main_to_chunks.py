#!/usr/bin/env python3
"""Split main.tex body into zh-chunks/chunk-XX.tex at section boundaries."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"
CHUNKS = ROOT / "paper" / "spc4-t73-candidate" / "zh-chunks"

# Start markers inside \begin{document} ... \end{document} (exclusive of preamble).
MARKERS = [
    r"\begin{abstract}",
    r"\section{Introduction}",
    r"\section{The trace-73 Cappell--Shaneson candidate}",
    r"\section{Precise statements}",
    r"\section{The finite computational layer}",
    r"\section{Lasagna modules and the comparison framework}",
    r"\section{Johnson product-ribbon presentation and P0}",
    r"\section{The coefficient-trace comparison}",
    r"\section{Three-handle sphere closure}",
    r"\section{Final identifications}",
    r"\input{sec-retired-assumptions}",
    r"\section{Related work}",
    r"\section{Conclusion}",
    r"\appendix",
    r"\section{P0 reconstruction protocol}",
    r"\input{sec-appendices-extra}",
    r"\section{Correspondence with the Lean fields}",
]


def extract_body(text: str) -> str:
    start = text.index(r"\begin{document}") + len(r"\begin{document}")
    end = text.index(r"\end{document}")
    return text[start:end]


def split_body(body: str) -> list[str]:
    positions: list[tuple[int, str]] = []
    for marker in MARKERS:
        idx = body.index(marker)
        positions.append((idx, marker))
    positions.sort(key=lambda x: x[0])
    chunks: list[str] = []
    for i, (pos, _marker) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(body)
        chunk = body[pos:end].strip()
        chunks.append(chunk + "\n")
    return chunks


def main() -> None:
    body = extract_body(MAIN.read_text(encoding="utf-8"))
    chunks = split_body(body)
    CHUNKS.mkdir(parents=True, exist_ok=True)
    for i, chunk in enumerate(chunks):
        path = CHUNKS / f"chunk-{i:02d}.tex"
        path.write_text(chunk, encoding="utf-8")
        print(f"WROTE {path.name} ({len(chunk.splitlines())} lines)")
    print(f"SPLIT {len(chunks)} chunks from {MAIN.name}")


if __name__ == "__main__":
    main()
