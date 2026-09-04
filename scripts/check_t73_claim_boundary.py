#!/usr/bin/env python3
"""Check that the controlling paper keeps a conditional claim boundary.

The English manuscript marks Johnson P0/C/S as Open until actual geometry
is supplied, and must not claim an unconditional smooth counterexample:
Lean ExternalGeometry remains uninhabited, and MWW 3.4/3.5 are cited rather
than proved here.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: required claim-boundary text missing: {needle!r}")


def reject(text: str, needle: str, source: Path) -> None:
    if needle in text:
        raise AssertionError(f"{source}: forbidden unconditional claim present: {needle!r}")


def check() -> None:
    paper_text = PAPER.read_text(encoding="utf-8")

    # Conditional top-level theorem (not an unconditional Trace-73 theorem).
    require(
        paper_text,
        r"\begin{theorem}[Conditional trace-73 theorem]\label{thm:joined}",
        PAPER,
    )
    require(
        paper_text,
        "That interface is not constructed in Lean, so no counterexample is claimed.",
        PAPER,
    )
    require(
        paper_text,
        r"that assembly is \Open\ for the Johnson candidate",
        PAPER,
    )

    # Discharged geometric theorems / lemmas used by the claim map.
    for marker in (
        r"\label{thm:P0discharge}",
        r"\label{lem:P0d-link}",
        r"\label{lem:C1}",
        r"\label{thm:Cdischarge}",
        r"\label{thm:Sdischarge}",
        r"\label{hyp:P3}",
        r"\label{sec:final-identifications}",
        r"Not the E7",
    ):
        require(paper_text, marker, PAPER)

    require(
        paper_text,
        r"Hypothesis~\ref{hyp:P0} remains \Open",
        PAPER,
    )
    require(
        paper_text,
        r"Hypothesis~\ref{hyp:P1} remains \Open",
        PAPER,
    )
    require(
        paper_text,
        r"Hypothesis~\ref{hyp:P2} remains \Open",
        PAPER,
    )
    require(
        paper_text,
        "geometry-bound truncated Burau",
        PAPER,
    )
    require(
        paper_text,
        "dated 24 August 2026, contains Lemma~5.5",
        PAPER,
    )

    # Finite / cited layers that must remain visible in the manuscript.
    require(paper_text, "2624", PAPER)
    require(paper_text, "494", PAPER)
    require(
        paper_text,
        r"\cite[Proposition~3.4 and Corollary~3.5]{ManolescuWalkerWedrich2023}",
        PAPER,
    )
    require(paper_text, "cited not formalized", PAPER)
    require(paper_text, r"scripts/recompute\_t73\_delta3.py --check", PAPER)
    require(paper_text, r"certify\_t73\_e12\_s4.py", PAPER)

    # Forbidden: restored status-table OPEN rows, absent-ledger slogans,
    # or an unconditional joined theorem / counterexample claim.
    reject(paper_text, r"\begin{theorem}[Trace-73 theorem]\label{thm:joined}", PAPER)
    reject(paper_text, "gives a counterexample", PAPER)
    reject(paper_text, "The actual reduced PD ledger is absent", PAPER)
    reject(paper_text, "that object is absent", PAPER)
    reject(paper_text, r"P0a & \Open", PAPER)
    reject(paper_text, r"P3/E11 & \Open", PAPER)
    reject(paper_text, r"P2/E10/S & \Open", PAPER)
    reject(paper_text, r"C3 & \Open", PAPER)
    reject(paper_text, r"P2/E7 & \Open", PAPER)
    reject(paper_text, "Lemmas~5.5 and~5.7 do not appear", PAPER)
    reject(paper_text, r"u_0=e_0\pm e_5", PAPER)
    reject(paper_text, "1--3 cancellations restore", PAPER)
    reject(paper_text, "we have proved Hypotheses", PAPER)


def main() -> None:
    check()
    print("T73_CLAIM_BOUNDARY=OPEN_GEOMETRY")
    print(f"PAPER={PAPER}")


if __name__ == "__main__":
    main()
