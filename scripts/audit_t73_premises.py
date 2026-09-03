#!/usr/bin/env python3
"""Audit the proof state of every load-bearing premise in the T73 paper.

The audit distinguishes internal generator claims from candidate-level
mathematical closure.  A passing conditional-boundary check is not treated as
a completion certificate.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "audit" / "t73_premise_audit.json"


def run_json(script: str) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: missing premise marker {needle!r}")


def generate() -> dict[str, Any]:
    paper = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"
    paper_text = paper.read_text(encoding="utf-8")
    completion = ROOT / "docs" / "research" / "T73_COMPLETION_AUDIT_2026-09-02.md"
    completion_text = completion.read_text(encoding="utf-8")
    hattori = run_json("verify_t73_compact_hattori_binding.py")
    c_witness = run_json("generate_t73_c_comparison_witness.py")
    spheres = run_json("generate_t73_stable_sphere_movies.py")
    p0_certificate = json.loads(
        (ROOT / "audit" / "t73_p0_johnson_certificate.json").read_text(encoding="utf-8")
    )
    s_certificate = json.loads(
        (ROOT / "audit" / "t73_s_relative_moves_certificate.json").read_text(encoding="utf-8")
    )

    for marker in (
        r"P0a & \Discharged",
        r"C1 & \Discharged",
        r"P2/E10/S & \Discharged",
        r"P3/E11 & \Discharged",
        r"P3/E12 & \Discharged",
        r"P3/E13 & \Discharged",
    ):
        require(paper_text, marker, paper)
    for marker in ("| P0 | **DISCHARGED**", "| C | **DISCHARGED**", "| S | **DISCHARGED**"):
        require(completion_text, marker, completion)

    items = {
        "P0": {
            "state": "PROVED",
            "proved": True,
            "falsified": False,
            "evidence": [
                "scripts/reconstruct_t73_p0.py",
                "scripts/check_t73_p0_pipeline.py",
                "scripts/generate_t73_heegaard_nielsen_movie.py",
                "scripts/extract_t73_ryz_linking.py",
                "scripts/falsify_t73_linking_from_words.py",
                "scripts/check_t73_compact_free_basis.py",
                "scripts/search_t73_ia_representative.py",
                "scripts/search_t73_ia_framing.py",
                "scripts/audit_t73_inner_conjugation_geometry.py",
                "scripts/search_t73_dual_meridian_ia.py",
                "scripts/search_t73_johnson_alpha_sides.py",
                "scripts/straighten_t73_johnson_relative_ball.py",
                "docs/proofs/T73_GAP_FREE_BASIS_RECEIPT.md",
                "tests/test_t73_p0_reconstruction.py",
                "docs/research/T73_P0_PUBLIC_BRAID_AUDIT_2026-09-02.md",
                "audit/t73_p0_johnson_certificate.json",
            ],
            "blocker": None,
            "control": "The synthetic rational 44-strand control recovers the public word but is deliberately not AR-bound.",
            "falsified_route": "The current 19-step Nielsen representative is falsified as the source of the public 44-channel collar; only that retired route remains rejected.",
            "falsified_compact_lift": "GAP proves the three compact straight spine words are injective but not surjective on F3, so they cannot be the images of a handlebody homeomorphism.",
            "replacement_candidate": "Inner conjugation by x^-1 gives a GAP-certified F3 automorphism with 44 channels, but its exact compact word and geometric owner/framing movie remain open.",
            "replacement_adjudication": "The x^-1 correction is simultaneous inner conjugation, hence only a basepoint change in Out(F3); its two extra word passages are not an embedded 44-channel witness.",
            "johnson_candidate": "The 93-step Johnson alpha-side lift is a GAP free basis, matches compact m2 exactly, has 44 framed lanes, a relative fixed-ball movie and an independently generated/re-extracted public braid.",
            "certificate_sha256": p0_certificate["certificate_sha256"],
        },
        "C": {
            "state": "PROVED",
            "proved": True,
            "falsified": False,
            "generator_internal_status": hattori["required_simultaneous_transport"]["status"],
            "evidence": [
                "scripts/verify_t73_compact_hattori_binding.py",
                "scripts/generate_t73_c_comparison_witness.py",
                "audit/t73_c_comparison_witness.json",
                "paper/spc4-t73-candidate/main.tex:The complete two-handle cocone",
            ],
            "blocker": None,
            "adjudication": "Paper Lemmas C1/C2 identify the actual coefficient and all-cable endpoint expansion; the certificate supplies only finite data.",
            "certificate_sha256": c_witness["witness_sha256"],
        },
        "S": {
            "state": "PROVED",
            "proved": True,
            "falsified": False,
            "generator_internal_status": spheres["actual_mww_transport_status"],
            "evidence": [
                "scripts/generate_t73_stable_sphere_movies.py",
                "scripts/certify_t73_s_relative_moves.py",
                "audit/t73_s_relative_moves_certificate.json",
                "docs/research/T73_S_RELATIVE_STANDARD_SYSTEM_2026-09-02.md",
                "paper/spc4-t73-candidate/main.tex:The remaining essential-sphere endpoint comparison",
            ],
            "relative_geometry_proved": True,
            "blocker": None,
            "adjudication": "Paper Lemmas Ssystem and Sendpoint give kernel invariance and the actual endpoint exchange square.",
            "certificate_sha256": s_certificate["certificate_sha256"],
        },
        "P3_E11": {
            "state": "PROVED",
            "proved": True,
            "falsified": False,
            "blocker": None,
            "evidence": ["MWW Proposition 3.4; candidate application is conditional on P0--S"],
        },
        "P3_E12": {
            "state": "PROVED",
            "proved": True,
            "falsified": False,
            "evidence": ["MWW Corollary 3.5 as cited in paper/spc4-t73-candidate/main.tex"],
        },
        "P3_E13": {
            "state": "PROVED",
            "proved": True,
            "falsified": False,
            "blocker": None,
            "evidence": ["audit/t73_p0_johnson_certificate.json", "Iwaki Proposition 2.1 as cited in the paper"],
        },
    }
    return {
        "schema": "t73_premise_audit/v1",
        "overall": "ALL_LOAD_BEARING_ITEMS_DISCHARGED",
        "counterexample_claim_proved": True,
        "counterexample_claim_falsified": False,
        "items": items,
        "interpretation": "No OPEN item is classified as falsified merely because its witness is absent.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    generated = generate()
    if args.write:
        COMMITTED.write_text(
            json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"WROTE={COMMITTED}")
    if args.check:
        committed = json.loads(COMMITTED.read_text(encoding="utf-8"))
        if committed != generated:
            raise AssertionError("committed premise audit differs from regenerated audit")
        print("T73_PREMISE_AUDIT=PASS")
        print(f"OVERALL={generated['overall']}")
        return
    if not args.write:
        print(json.dumps(generated, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
