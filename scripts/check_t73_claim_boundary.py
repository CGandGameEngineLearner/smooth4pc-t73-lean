#!/usr/bin/env python3
"""Reject a paper that outruns the repository's candidate-level evidence.

This is a consistency gate, not a mathematical proof.  It prevents the known
OPEN transport fields from coexisting with an unconditional paper claim.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: required claim-boundary text missing: {needle!r}")


def reject(text: str, needle: str, source: Path) -> None:
    if needle in text:
        raise AssertionError(f"{source}: forbidden unconditional text present: {needle!r}")


def check() -> None:
    paper = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"
    hattori = ROOT / "scripts" / "verify_t73_compact_hattori_binding.py"
    spheres = ROOT / "scripts" / "generate_t73_stable_sphere_movies.py"
    paper_text = paper.read_text(encoding="utf-8")
    hattori_text = hattori.read_text(encoding="utf-8")
    sphere_text = spheres.read_text(encoding="utf-8")

    require(hattori_text, '"status": "OPEN"', hattori)
    require(sphere_text, '"actual_mww_transport_status"', spheres)
    require(sphere_text, '"OPEN:', spheres)

    require(paper_text, "Conditional trace-73 theorem", paper)
    require(paper_text, r"P0 & \Open", paper)
    require(paper_text, r"P1/C & \Open", paper)
    require(paper_text, r"P2/E7 & \Open", paper)
    require(paper_text, r"P2/E10/S & \Open", paper)
    require(paper_text, "They have not been discharged", paper)

    reject(paper_text, "the smooth four-dimensional Poincare conjecture is false", paper)
    reject(paper_text, r"P0 & \Discharged", paper)
    reject(paper_text, r"P1/C & \Discharged", paper)
    reject(paper_text, r"P2/E7 & \Discharged", paper)
    reject(paper_text, r"P2/E10/S & \Discharged", paper)


def main() -> None:
    check()
    print("T73_CLAIM_BOUNDARY=PASS")


if __name__ == "__main__":
    main()
