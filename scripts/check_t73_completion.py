#!/usr/bin/env python3
"""Final cross-layer completion gate for the trace-73 paper."""

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
        raise AssertionError(f"{source}: missing completion evidence {needle!r}")


def reject(text: str, needle: str, source: Path) -> None:
    if needle in text:
        raise AssertionError(f"{source}: stale incomplete claim {needle!r}")


def check() -> None:
    paper = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"
    pdf = ROOT / "output" / "pdf" / "spc4-t73-candidate.pdf"
    conditional = ROOT / "Smooth4PC" / "T73Conditional.lean"
    external = ROOT / "Smooth4PC" / "T73External.lean"
    representable = ROOT / "Smooth4PC" / "RepresentableCoefficient.lean"
    p0_witness = ROOT / "audit" / "t73_ar_product_witness.json"
    c_witness = ROOT / "audit" / "t73_c_comparison_witness.json"

    load_script("generate_t73_ar_product_witness").verify_committed(p0_witness)
    load_script("generate_t73_c_comparison_witness").verify_committed(c_witness)
    load_script("check_t73_claim_boundary").check()
    hattori = load_script("verify_t73_compact_hattori_binding").verify()
    if hattori["required_simultaneous_transport"]["status"] != (
        "DISCHARGED_BY_PUBLIC_REPLACEMENT_COORDINATES"
    ):
        raise AssertionError("live Hattori verifier still reports an open transport")
    sphere_movies = load_script("generate_t73_stable_sphere_movies").generate_ledger()
    if "RETIRED_NOT_LOAD_BEARING" not in sphere_movies["actual_mww_transport_status"]:
        raise AssertionError("historical sphere movie route is not marked retired")

    paper_text = paper.read_text(encoding="utf-8")
    require(paper_text, "A trace-73 Cappell--Shaneson homotopy 4-sphere", paper)
    require(paper_text, r"\begin{theorem}[Main theorem]\label{thm:joined}", paper)
    for item in ("P0", "P1/C", "P2/E7", "P2/E10/S", "P3/E11", "P3/E12", "P3/E13"):
        require(paper_text, f"{item} & \\Discharged", paper)
    require(paper_text, "gives a counterexample to the smooth", paper)
    for stale in (
        "C remains open",
        "pending coefficient-trace comparison",
        "conditional theorem",
        r"& \Open",
        r"& \Partial",
    ):
        reject(paper_text, stale, paper)

    conditional_text = conditional.read_text(encoding="utf-8")
    external_text = external.read_text(encoding="utf-8")
    require(conditional_text, "ExternalGeometry", conditional)
    require(conditional_text, "CSExternalGeometry", conditional)
    require(external_text, "structure ExternalGeometry", external)
    require(external_text, "structure CSExternalGeometry", external)

    lean_source = representable.read_text(encoding="utf-8")
    for token in ("sorry", "admit", "axiom", "opaque", "unsafe", "extern"):
        reject(lean_source, token, representable)

    if not pdf.is_file() or pdf.stat().st_size < 100_000:
        raise AssertionError("reviewed paper PDF is missing or implausibly small")


def main() -> None:
    check()
    print("T73_COMPLETION_GATE=PASS")


if __name__ == "__main__":
    main()
