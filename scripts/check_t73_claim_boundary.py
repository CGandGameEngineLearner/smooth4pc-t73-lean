#!/usr/bin/env python3
"""Check that the paper does not claim a discharged counterexample."""

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
        r"\begin{theorem}[Conditional trace-73 theorem]\label{thm:joined}",
        paper,
    )
    require(paper_text, r"P0a & \Discharged", paper)
    require(paper_text, r"C1 & \Discharged", paper)
    require(paper_text, r"C2 & \Discharged", paper)
    require(paper_text, r"P2/E10/S & \Discharged", paper)
    require(paper_text, r"P3/E11 & \Discharged", paper)
    require(paper_text, r"P3/E12 & \Discharged", paper)
    require(paper_text, r"P3/E13 & \Partial", paper)
    require(paper_text, r"computedCubic_eq_2624", paper)
    require(paper_text, "2624", paper)

    reject(paper_text, r"P2/E10/S & \Open", paper)
    reject(paper_text, r"P3/E11 & \Open", paper)
    reject(paper_text, "gives a counterexample", paper)
    reject(paper_text, r"\begin{theorem}[Trace-73 theorem]\label{thm:joined}", paper)


def main() -> None:
    check()
    print("T73_CLAIM_BOUNDARY=OPEN_GEOMETRY")


if __name__ == "__main__":
    main()
