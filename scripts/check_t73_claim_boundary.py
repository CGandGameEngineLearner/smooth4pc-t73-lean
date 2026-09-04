#!/usr/bin/env python3
"""Check the unconditional paper theorem and its partial Lean boundary.

The mathematical theorem is unconditional after P0/C/S/E13, while the Lean
formalization must still state that ExternalGeometry remains uninhabited.
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

    # Unconditional paper theorem, separated from the partial Lean status.
    require(
        paper_text,
        r"\begin{theorem}[Trace-73 theorem]\label{thm:joined}",
        PAPER,
    )
    require(
        paper_text,
        "Consequently it is a counterexample to the smooth four-dimensional",
        PAPER,
    )
    require(
        paper_text,
        "paper-level mathematical claim subject to expert review",
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
        r"Hypothesis~\ref{hyp:P0} holds for the explicit Johnson presentation",
        PAPER,
    )
    require(
        paper_text,
        r"Hypothesis~\ref{hyp:P1} holds for the explicit Johnson presentation",
        PAPER,
    )
    require(
        paper_text,
        r"Hypothesis~\ref{hyp:P2} holds for the explicit Johnson presentation",
        PAPER,
    )
    require(
        paper_text,
        "not yet a fully",
        PAPER,
    )
    require(
        paper_text,
        "geometry-bound Burau",
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

    # Forbidden: stale OPEN rows, absent-ledger slogans, or a claim that Lean
    # already contains the analytic geometry inhabitant.
    reject(paper_text, r"\begin{theorem}[Conditional trace-73 theorem]\label{thm:joined}", PAPER)
    reject(paper_text, "fully Lean-verified counterexample is proved", PAPER)
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
    print("T73_CLAIM_BOUNDARY=UNCONDITIONAL_PAPER_LEAN_PARTIAL")
    print(f"PAPER={PAPER}")


if __name__ == "__main__":
    main()
