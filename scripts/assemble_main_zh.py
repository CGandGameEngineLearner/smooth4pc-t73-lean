#!/usr/bin/env python3
"""Assemble main-zh.tex from Chinese preamble and translated zh-chunks."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_main_zh import (  # noqa: E402
    HYPersetup_NEW,
    HYPersetup_OLD,
    MAIN,
    PREAMBLE_NEW,
    PREAMBLE_OLD,
    STATUS_NEW,
    STATUS_OLD,
    THEOREM_NEW,
    THEOREM_OLD,
    TITLE_NEW,
    TITLE_OLD,
)

PAPER = ROOT / "paper" / "spc4-t73-candidate"
CHUNKS = PAPER / "zh-chunks"
OUT = PAPER / "main-zh.tex"


def chinese_preamble() -> str:
    text = MAIN.read_text(encoding="utf-8")
    for old, new in (
        (PREAMBLE_OLD, PREAMBLE_NEW),
        (TITLE_OLD, TITLE_NEW),
        (THEOREM_OLD, THEOREM_NEW),
        (STATUS_OLD, STATUS_NEW),
        (HYPersetup_OLD, HYPersetup_NEW),
    ):
        text = text.replace(old, new)
    lines = text.splitlines()
    end = next(i for i, line in enumerate(lines) if line.strip() == r"\begin{document}")
    return "\n".join(lines[: end + 1])


def assemble() -> None:
    parts = [chinese_preamble()]
    for i in range(17):
        chunk = CHUNKS / f"chunk-{i:02d}-zh.tex"
        if not chunk.is_file():
            raise FileNotFoundError(chunk)
        parts.append(chunk.read_text(encoding="utf-8").rstrip())
    parts.append(r"\end{document}")
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"ASSEMBLED {OUT} ({len(parts)} parts, {len(OUT.read_text(encoding='utf-8').splitlines())} lines)")


if __name__ == "__main__":
    assemble()
