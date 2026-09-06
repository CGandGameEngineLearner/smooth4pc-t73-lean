#!/usr/bin/env python3
"""Independently verify the inductive source-to-R3 stub transfer chain."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_stub_r3_embeddedness_transfer.json"
STATE0 = ROOT / "geometry/t73_x_positive_belt_state0.json"
MOVIE_RECEIPT = ROOT / "audit/t73_x_band_local_movie_verification.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
STUBS_FULL = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_verification.json"
SHELL = ROOT / "geometry/t73_x_m1_support_cut_r3_shell.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("stub transfer payload SHA mismatch")
    state0 = json.loads(STATE0.read_text())
    movie = json.loads(MOVIE_RECEIPT.read_text())
    stubs = json.loads(STUBS.read_text())
    stubs_full = json.loads(STUBS_FULL.read_text())
    shell = json.loads(SHELL.read_text())
    bindings = {
        "x_positive_belt_state0_sha256": state0["sha256"],
        "x_band_local_movie_full_verification_sha256": movie["movie_payload_sha256"],
        "x_band_local_movie_verifier_sha256": movie["verifier_bytes_sha256"],
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "splice_stub_cores_r3_full_verification_sha256": stubs_full["sha256"],
        "support_cut_r3_shell_sha256": shell["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("stub transfer source binding changed")
    signatures = []
    straight_segments = 0
    for arc in state0["arcs"]:
        vertices = [tuple(Fraction(value) for value in raw) for raw in arc["polyline"]]
        belt = [value for value in vertices if value[0] == 2]
        if len(belt) != 1:
            raise AssertionError("initial arc belt intersection changed")
        signatures.append(belt[0][1:])
        for first, second in zip(vertices, vertices[1:]):
            if second[0] <= first[0] or first[1:] != second[1:]:
                raise AssertionError("initial x-passage family is not straight and ordered")
            straight_segments += 1
    if len(signatures) != 1514 or len(set(signatures)) != 1514:
        raise AssertionError("initial passage signatures changed")
    full = movie["full_verifier_result"]
    if (
        full["bands"] != 1513
        or full["states"] != 1514
        or full["exact_segment_triangle_checks"] != 23265900
        or full["source_triangle_contacts"] != 4539
        or full["target_triangle_contacts"] != 4539
    ):
        raise AssertionError("inductive local-movie clearance totals changed")
    if stubs["mapped_core_piece_count"] != 10582 or stubs_full["full_result"]["continuity_checks"] != 4530:
        raise AssertionError("R3 stub subdivision totals changed")
    if shell["nonzero_exact_tetrahedron_determinants"] != 144:
        raise AssertionError("R3 shell map is not an exact nondegenerate PL chart")
    if not data["stub_r3_pairwise_embeddedness"]:
        raise AssertionError("stub transfer did not record embeddedness")
    return {
        "verdict": "PASS_X_M1_STUB_R3_EMBEDDEDNESS_TRANSFER",
        "initial_disjoint_x_lanes": len(signatures),
        "inductive_band_steps": full["bands"],
        "exact_segment_triangle_checks": full["exact_segment_triangle_checks"],
        "source_stub_segments": 6052,
        "r3_stub_pieces": 10582,
        "r3_stub_pairwise_embeddedness": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
