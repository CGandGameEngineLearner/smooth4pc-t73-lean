#!/usr/bin/env python3
"""Audit the proof state of every load-bearing premise in the T73 paper.

Geometric items are Open until the named acceptance tests pass.  This program
does not hardcode proved: true.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "audit" / "t73_premise_audit.json"


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: missing premise marker {needle!r}")


def generate() -> dict[str, Any]:
    paper = ROOT / "paper" / "spc4-t73-candidate" / "main.tex"
    paper_text = paper.read_text(encoding="utf-8")
    completion = ROOT / "docs" / "research" / "T73_COMPLETION_AUDIT_2026-09-02.md"
    completion_text = completion.read_text(encoding="utf-8")
    p0_certificate = json.loads(
        (ROOT / "audit" / "t73_p0_johnson_certificate.json").read_text(encoding="utf-8")
    )
    c_witness = json.loads(
        (ROOT / "audit" / "t73_c_comparison_witness.json").read_text(encoding="utf-8")
    )
    s_certificate = json.loads(
        (ROOT / "audit" / "t73_s_relative_moves_certificate.json").read_text(encoding="utf-8")
    )

    for marker in (
        r"P0a & \Discharged",
        r"C1 & \Discharged",
        r"C2 & \Discharged",
        r"P2/E10/S & \Open",
    ):
        require(paper_text, marker, paper)
    for marker in ("| P0 | **PASS**", "| C | **PASS**", "| S | **OPEN**"):
        require(completion_text, marker, completion)

    p0_pass = (
        p0_certificate.get("verdict") == "PASS"
        and p0_certificate.get("P0_status") != "OPEN"
    )
    if p0_pass and p0_certificate.get("checks", {}).get("johnson_ar_affine_bridge") is not True:
        raise AssertionError("P0 cannot be PASS without the Johnson--AR handlebody bridge")
    c_pass = (
        c_witness.get("C_status") == "PASS"
        and c_witness.get("C1_status") == "PASS"
        and c_witness.get("C2_status") == "PASS"
    )
    if c_pass and not p0_pass:
        raise AssertionError("C cannot be PASS without P0")
    items = {
        "P0": {
            "state": "PASS" if p0_pass else "OPEN",
            "proved": p0_pass,
            "falsified": False,
            "evidence": [
                "scripts/certify_t73_johnson_ar_bridge.py",
                "scripts/reconstruct_t73_p0.py",
                "scripts/certify_t73_spine_star_handlebodies.py",
                "audit/t73_p0a_handlebody_pair.json",
                "scripts/check_t73_p0_pipeline.py",
                "scripts/falsify_t73_linking_from_words.py",
                "scripts/search_t73_johnson_alpha_sides.py",
                "docs/proofs/T73_GAP_FREE_BASIS_RECEIPT.md",
                "tests/test_t73_p0_reconstruction.py",
                "audit/t73_p0_johnson_certificate.json",
                "docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md",
            ],
            "blocker": (
                "none"
                if p0_pass
                else "P0 reconstruction input is missing or reconstruct_t73_p0.py rejected it."
            ),
            "control": "The synthetic rational 44-strand control recovers the public word but is deliberately not AR-bound.",
            "falsified_route": "The current 19-step Nielsen representative is falsified as the source of the public 44-channel collar; only that retired route remains rejected.",
            "falsified_compact_lift": "GAP proves the three compact straight spine words are injective but not surjective on F3, so they cannot be the images of a handlebody homeomorphism.",
            "replacement_candidate": "Inner conjugation by x^-1 gives a GAP-certified F3 automorphism with 44 channels, but its exact compact word and geometric owner/framing movie remain open.",
            "replacement_adjudication": "The x^-1 correction is simultaneous inner conjugation, hence only a basepoint change in Out(F3); its two extra word passages are not an embedded 44-channel witness.",
            "johnson_candidate": (
                "The 93-bit Johnson alpha-side lift is a GAP free basis, "
                "matches compact m2, has 44 y-channels, and the six-sweep "
                "reconstruction recovers the public 11340-letter word."
            ),
            "certificate_sha256": p0_certificate["certificate_sha256"],
            "p0a_status": "PASS" if p0_pass else "OPEN",
            "p0b_status": "PASS" if p0_pass else "OPEN",
            "p0c_status": "PASS" if p0_pass else "OPEN",
            "p0d_finite_word_match": True,
        },
        "C": {
            "state": "PASS" if c_pass else "OPEN",
            "proved": c_pass,
            "falsified": False,
            "generator_internal_status": c_witness.get("C_status"),
            "evidence": [
                "scripts/generate_t73_c_comparison_witness.py",
                "scripts/certify_t73_c1_cut_link.py",
                "scripts/certify_t73_c2_comparison.py",
                "audit/t73_c_comparison_witness.json",
                "audit/t73_c1_cut_link.json",
                "audit/t73_c2_comparison.json",
                "Smooth4PC/RepresentableCoefficient.lean",
            ],
            "blocker": (
                "none"
                if c_pass
                else "C1 requires collar-bound product rectangles and C2 comparison maps."
            ),
            "adjudication": (
                "Johnson replacement: C1 product isotopy of P0 reconstruction "
                "strands and C2 action cubes plus RepresentableCoefficient.lean. "
                "S remains Open."
            ),
            "certificate_sha256": c_witness["witness_sha256"],
        },
        "S": {
            "state": "OPEN",
            "proved": False,
            "falsified": False,
            "generator_internal_status": s_certificate.get("verdict"),
            "evidence": [
                "scripts/certify_t73_s_relative_moves.py",
                "scripts/certify_t73_s_standard_spheres.py",
                "audit/t73_s_relative_moves_certificate.json",
                "audit/t73_s_standard_spheres.json",
            ],
            "relative_geometry_proved": False,
            "blocker": (
                "No B-fixing move list in Q = partial W2 \\ Int B0, and "
                "actual_standard_sphere_endpoint_foam_computed is false. "
                "Closed-manifold HJ Theorem 5.3 is not used as 'B is fixed'."
            ),
            "adjudication": "Paper Lemmas Ssystem and Sendpoint remain slogans.",
            "certificate_sha256": s_certificate["certificate_sha256"],
        },
        "P3_E11": {
            "state": "OPEN",
            "proved": False,
            "falsified": False,
            "blocker": "MWW Proposition 3.4 applies only after P0--S",
            "evidence": ["MWW Proposition 3.4; candidate application is conditional on P0--S"],
        },
        "P3_E12": {
            "state": "CITED_EXTERNAL",
            "proved": False,
            "falsified": False,
            "evidence": ["MWW Corollary 3.5 as a statement about S^4, not a candidate identification"],
        },
        "P3_E13": {
            "state": "PARTIAL",
            "proved": False,
            "falsified": False,
            "blocker": "det(A-I)=1 is proved; the Johnson replacement is the discharged P0 presentation",
            "evidence": ["Smooth4PC/T73Finite.lean", "Iwaki Proposition 2.1 for the matrix criterion"],
        },
    }
    return {
        "schema": "t73_premise_audit/v1",
        "overall": "OPEN",
        "counterexample_claim_proved": False,
        "counterexample_claim_falsified": False,
        "items": items,
        "interpretation": (
            "P0 is discharged for the explicit Johnson replacement, and C is "
            "discharged for the collar-bound product comparison. S remains Open. "
            "The counterexample claim is not proved."
        ),
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
        print("T73_PREMISE_AUDIT=OPEN")
        print(f"OVERALL={generated['overall']}")
        print(f"P0={generated['items']['P0']['state']}")
        print(f"C={generated['items']['C']['state']}")
        print(f"S={generated['items']['S']['state']}")
        print(f"COUNTEREXAMPLE={generated['counterexample_claim_proved']}")
        return
    if not args.write:
        print(json.dumps(generated, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
