#!/usr/bin/env python3
"""Write a full-verification receipt or perform its fast daily checks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
VERIFIER = ROOT / "scripts/verify_t73_x_band_local_movie.py"
OUTPUT = ROOT / "audit/t73_x_band_local_movie_verification.json"

EXPECTED_RESULT = {
    "verdict": "PASS_ALL_1513_X_LOCAL_FRAMED_BAND_STATES",
    "bands": 1513,
    "states": 1514,
    "initial_segments": 3028,
    "final_segments": 12106,
    "source_triangle_contacts": 4539,
    "target_triangle_contacts": 4539,
    "numpy_broad_phase_pairs": 91554656,
    "exact_segment_triangle_checks": 23265900,
    "remaining_x_passage_sources": ["m_1:C_i"],
    "global_hybrid_splices_verified": 1,
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def build_full() -> dict:
    from verify_t73_x_band_local_movie import verify

    result = verify()
    if result != EXPECTED_RESULT:
        raise AssertionError("full x-local verifier result differs from the receipt contract")
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    return {
        "schema": "t73_x_band_local_movie_verification_receipt/v1",
        "movie_path": "geometry/t73_x_band_local_movie.json",
        "movie_bytes_sha256": file_sha(MOVIE),
        "movie_payload_sha256": movie["sha256"],
        "verifier_path": "scripts/verify_t73_x_band_local_movie.py",
        "verifier_bytes_sha256": file_sha(VERIFIER),
        "positive_belt_state0_sha256": movie["positive_belt_state0_sha256"],
        "x_cancellation_sha256": movie["x_cancellation_sha256"],
        "actual_ar_link_sha256": movie["actual_ar_link_sha256"],
        "full_verifier_result": result,
        "verification_mode": "FULL_INDEPENDENT_CURRENT_SEGMENT_STATE_REPLAY",
        "verdict": result["verdict"],
    }


def check_receipt() -> dict:
    receipt = json.loads(OUTPUT.read_text(encoding="utf-8"))
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    payload = dict(movie)
    stored_payload_sha = payload.pop("sha256")
    checks = {
        "movie_bytes": receipt["movie_bytes_sha256"] == file_sha(MOVIE),
        "movie_payload": stored_payload_sha == canonical_sha(payload),
        "receipt_payload": receipt["movie_payload_sha256"] == stored_payload_sha,
        "verifier_bytes": receipt["verifier_bytes_sha256"] == file_sha(VERIFIER),
        "source_hashes": all(
            receipt[field] == movie[field]
            for field in (
                "positive_belt_state0_sha256",
                "x_cancellation_sha256",
                "actual_ar_link_sha256",
            )
        ),
        "fixed_result": receipt["full_verifier_result"] == EXPECTED_RESULT,
        "verdict": receipt["verdict"] == EXPECTED_RESULT["verdict"],
    }
    if not all(checks.values()):
        raise AssertionError(f"x-local verification receipt failed: {checks}")
    return {
        "verdict": "PASS_X_LOCAL_MOVIE_RECEIPT",
        "checks": checks,
        "full_verifier_verdict": receipt["verdict"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        if not args.full:
            raise SystemExit("first receipt write requires --full")
        OUTPUT.write_text(
            json.dumps(build_full(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.check:
        print(json.dumps(check_receipt(), sort_keys=True))


if __name__ == "__main__":
    main()
