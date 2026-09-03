#!/usr/bin/env python3
"""Check that the paper's final claim matches the discharged P0/C/S evidence."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: required claim-boundary text missing: {needle!r}")


def reject(text: str, needle: str, source: Path) -> None:
    if needle in text:
        raise AssertionError(f"{source}: forbidden unconditional claim present: {needle!r}")


def check() -> None:
    paper = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"
    paper_text = paper.read_text(encoding="utf-8")

    require(
        paper_text,
        r"\begin{theorem}[Trace-73 theorem]\label{thm:joined}",
        paper,
    )
    require(paper_text, r"P0 & \Discharged", paper)
    require(paper_text, r"P1/C & \Discharged", paper)
    require(paper_text, r"P2/E7 & \Discharged", paper)
    require(paper_text, r"P2/E10/S & \Discharged", paper)
    require(paper_text, r"P3/E11 & \Discharged", paper)
    require(paper_text, r"P3/E12 & \Discharged", paper)
    require(paper_text, r"P3/E13 & \Discharged", paper)
    require(paper_text, "gives a counterexample to the smooth", paper)
    require(paper_text, "genus-zero core-counit calculation (32)", paper)

    reject(paper_text, r"\begin{theorem}[Conditional trace-73 theorem]", paper)
    reject(paper_text, r"P0 & \Open", paper)
    reject(paper_text, r"P0 & \Partial", paper)
    reject(paper_text, r"P1/C & \Open", paper)
    reject(paper_text, r"P2/E10/S & \Open", paper)
    reject(paper_text, "does not yet give a", paper)


def main() -> None:
    check()
    print("T73_CLAIM_BOUNDARY=PASS")


if __name__ == "__main__":
    main()
