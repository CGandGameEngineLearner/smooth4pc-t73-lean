#!/usr/bin/env python3
"""Check that the paper does not outrun the candidate-level evidence."""

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
    require(paper_text, r"P0a & \Open", paper)
    require(paper_text, r"C1 & \Open", paper)
    require(paper_text, r"P2/E7 & \Open", paper)
    require(paper_text, r"P2/E10/S & \Open", paper)
    require(paper_text, r"P3/E11 & \Open", paper)
    require(paper_text, r"P3/E12 & \Discharged", paper)
    require(paper_text, r"P3/E13 & \Discharged", paper)
    require(paper_text, "a\nconditional theorem", paper)
    require(paper_text, "P0a--c, C1--C2 and S", paper)

    reject(paper_text, r"\begin{theorem}[Main theorem]\label{thm:joined}", paper)
    reject(paper_text, r"P2/E10/S & \Discharged", paper)
    reject(paper_text, "gives a counterexample to the smooth", paper)


def main() -> None:
    check()
    print("T73_CLAIM_BOUNDARY=PASS")


if __name__ == "__main__":
    main()
