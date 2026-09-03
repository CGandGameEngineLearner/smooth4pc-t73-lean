#!/usr/bin/env python3
"""Completion gate for the P0/C/S mathematical paper.

The historical filename is retained for callers.  It checks the paper,
external-interface boundary and final PDF presence.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: missing conditional-boundary evidence {needle!r}")


def check() -> None:
    paper = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"
    pdf = ROOT / "output" / "pdf" / "spc4-t73-candidate.pdf"
    conditional = ROOT / "Smooth4PC" / "T73Conditional.lean"
    external = ROOT / "Smooth4PC" / "T73External.lean"

    load_script("check_t73_claim_boundary").check()

    paper_text = paper.read_text(encoding="utf-8")
    require(paper_text, "gives a counterexample to the smooth", paper)
    require(paper_text, r"P2/E10/S & \Discharged", paper)

    conditional_text = conditional.read_text(encoding="utf-8")
    external_text = external.read_text(encoding="utf-8")
    require(conditional_text, "ExternalGeometry", conditional)
    require(conditional_text, "CSExternalGeometry", conditional)
    require(external_text, "structure ExternalGeometry", external)
    require(external_text, "structure CSExternalGeometry", external)

    if not pdf.is_file() or pdf.stat().st_size < 100_000:
        raise AssertionError("reviewed paper PDF is missing or implausibly small")


def main() -> None:
    check()
    print("T73_COMPLETION=PASS")


if __name__ == "__main__":
    main()
