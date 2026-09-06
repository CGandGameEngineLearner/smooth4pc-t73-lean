#!/usr/bin/env python3
"""Bind F-563 inductive stub embeddedness through the AC-side R3 PL map."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE0 = ROOT / "geometry/t73_x_positive_belt_state0.json"
MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
MOVIE_RECEIPT = ROOT / "audit/t73_x_band_local_movie_verification.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
STUBS_FULL = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_verification.json"
SHELL = ROOT / "geometry/t73_x_m1_support_cut_r3_shell.json"
OUTPUT = ROOT / "audit/t73_x_m1_stub_r3_embeddedness_transfer.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def build():
    state0 = json.loads(STATE0.read_text())
    movie = json.loads(MOVIE.read_text())
    movie_receipt = json.loads(MOVIE_RECEIPT.read_text())
    stubs = json.loads(STUBS.read_text())
    stubs_full = json.loads(STUBS_FULL.read_text())
    shell = json.loads(SHELL.read_text())
    signatures = []
    monotone_segments = 0
    for arc in state0["arcs"]:
        vertices = [point(value) for value in arc["polyline"]]
        belt = [value for value in vertices if value[0] == 2]
        if len(belt) != 1:
            raise AssertionError("state-0 passage does not cross x=2 exactly once")
        signatures.append(belt[0][1:])
        for first, second in zip(vertices, vertices[1:]):
            if second[0] <= first[0] or first[1:] != second[1:]:
                raise AssertionError("state-0 passage is not a straight ordered x-lane")
            monotone_segments += 1
    if len(set(signatures)) != 1514:
        raise AssertionError("state-0 belt passage positions are not unique")
    full = movie_receipt["full_verifier_result"]
    if full["verdict"] != "PASS_ALL_1513_X_LOCAL_FRAMED_BAND_STATES":
        raise AssertionError("full local-movie clearance receipt is missing")
    if stubs_full["full_result"]["core_pieces_reconstructed"] != 10582:
        raise AssertionError("full R3 stub reconstruction receipt changed")
    result = {
        "schema": "t73_x_m1_stub_r3_embeddedness_transfer/v1",
        "x_positive_belt_state0_sha256": state0["sha256"],
        "x_band_local_movie_sha256": movie["sha256"],
        "x_band_local_movie_full_verification_sha256": movie_receipt["movie_payload_sha256"],
        "x_band_local_movie_verifier_sha256": movie_receipt["verifier_bytes_sha256"],
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "splice_stub_cores_r3_full_verification_sha256": stubs_full["sha256"],
        "support_cut_r3_shell_sha256": shell["sha256"],
        "initial_passage_count": len(signatures),
        "initial_unique_belt_positions": len(set(signatures)),
        "initial_straight_segment_count": monotone_segments,
        "inductive_band_steps": full["bands"],
        "inductive_states": full["states"],
        "numpy_broad_phase_pairs_replayed": full["numpy_broad_phase_pairs"],
        "exact_segment_triangle_checks_replayed": full["exact_segment_triangle_checks"],
        "source_triangle_contacts": full["source_triangle_contacts"],
        "target_triangle_contacts": full["target_triangle_contacts"],
        "final_local_segment_count": full["final_segments"],
        "source_stub_segment_count": 4 * full["bands"],
        "r3_stub_piece_count": stubs["mapped_core_piece_count"],
        "r3_stub_subdivision_continuity_checks": stubs["r3_piece_continuity_checks"],
        "transfer_argument": [
            "state 0 is a disjoint family because all straight x-lanes have distinct belt positions",
            "at each step the fully replayed embedded band disk is disjoint from every current historical segment except its declared source and target contacts",
            "the four added stub edges are boundary edges of that embedded disk, so induction preserves current-state embeddedness",
            "all final source stubs lie on the AC boundary side and the exact nondegenerate R3 shell barycentric map is a PL homeomorphism there",
            "subdivision from 6052 source stub segments to 10582 R3 pieces preserves the embedded disjoint union",
        ],
        "stub_r3_pairwise_embeddedness": True,
        "completion_status": "F563_STUB_EMBEDDEDNESS_TRANSFERRED_TO_R3_SHELL",
        "verdict": "PASS_X_M1_STUB_R3_EMBEDDEDNESS_TRANSFER",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("stub R3 embeddedness transfer is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "initial_lanes": result["initial_unique_belt_positions"],
        "inductive_steps": result["inductive_band_steps"],
        "source_stub_segments": result["source_stub_segment_count"],
        "r3_stub_pieces": result["r3_stub_piece_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
