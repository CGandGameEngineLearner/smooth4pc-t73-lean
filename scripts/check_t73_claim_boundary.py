#!/usr/bin/env python3
"""Check that the paper's final claim matches the replacement witnesses.

This is a consistency gate, not a mathematical proof.  Historical scripts may
retain OPEN fields for retired routes; the current paper must instead bind all
load-bearing rows to the public replacement witnesses.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: required claim-boundary text missing: {needle!r}")


def reject(text: str, needle: str, source: Path) -> None:
    if needle in text:
        raise AssertionError(f"{source}: forbidden stale claim text present: {needle!r}")


def check() -> None:
    paper = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"
    p0_witness = ROOT / "audit" / "t73_ar_product_witness.json"
    c_witness = ROOT / "audit" / "t73_c_comparison_witness.json"
    paper_text = paper.read_text(encoding="utf-8")
    require(p0_witness.read_text(encoding="utf-8"), '"schema": "t73_p0_embedded_framed_link_witness/v1"', p0_witness)
    require(c_witness.read_text(encoding="utf-8"), '"schema": "t73_candidate_c_comparison_witness/v1"', c_witness)

    require(paper_text, r"\begin{theorem}[Main theorem]\label{thm:joined}", paper)
    require(paper_text, r"P0 & \Discharged", paper)
    require(paper_text, r"P1/C & \Discharged", paper)
    require(paper_text, r"P2/E7 & \Discharged", paper)
    require(paper_text, r"P2/E10/S & \Discharged", paper)
    require(paper_text, r"P3/E11 & \Discharged", paper)
    require(paper_text, r"P3/E12 & \Discharged", paper)
    require(paper_text, r"P3/E13 & \Discharged", paper)
    require(paper_text, "gives a counterexample to the smooth", paper)

    reject(paper_text, "C remains open", paper)
    reject(paper_text, "pending coefficient-trace comparison", paper)
    reject(paper_text, "conditional theorem", paper)
    reject(paper_text, r"P1/C & \Open", paper)
    reject(paper_text, r"P2/E10/S & \Partial", paper)


def main() -> None:
    check()
    print("T73_CLAIM_BOUNDARY=PASS")


if __name__ == "__main__":
    main()
