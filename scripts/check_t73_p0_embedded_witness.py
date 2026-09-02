#!/usr/bin/env python3
"""Validate the structural completeness of a proposed embedded P0 witness.

The checker cannot prove PL embeddedness by itself; individual certificate
types need their own verifiers.  It does prevent a word/framing ledger from
being relabelled as the missing whole-link witness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "audit" / "t73_p0_embedded_witness_schema.json"


def missing_fields(value: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if field not in value]


def validate(candidate: dict[str, Any], schema: dict[str, Any]) -> None:
    if candidate.get("schema") != "t73_p0_embedded_framed_link_witness/v1":
        raise AssertionError("candidate is not an embedded P0 witness v1")

    missing = missing_fields(candidate, schema["required_top_level_fields"])
    if missing:
        raise AssertionError(f"missing top-level embedded-witness fields: {missing}")

    groups = [
        ("actual_framed_link", "required_actual_framed_link_fields"),
        ("ar_provenance", "required_ar_provenance_fields"),
        ("cancellation_movie", "required_cancellation_fields"),
        ("detector_collar", "required_detector_collar_fields"),
    ]
    for candidate_key, schema_key in groups:
        section = candidate[candidate_key]
        if not isinstance(section, dict):
            raise AssertionError(f"{candidate_key} must be an object")
        missing = missing_fields(section, schema[schema_key])
        if missing:
            raise AssertionError(f"{candidate_key} missing fields: {missing}")

    checks = candidate["independent_checks"]
    if not isinstance(checks, list) or not checks:
        raise AssertionError("independent_checks must list public verifier receipts")
    for check in checks:
        if not isinstance(check, dict) or check.get("status") != "PASS":
            raise AssertionError("every independent check must be a structured PASS receipt")
        if not check.get("verifier") or not check.get("input_sha256"):
            raise AssertionError("PASS receipts require verifier and input_sha256")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    validate(candidate, schema)
    print("T73_P0_EMBEDDED_WITNESS_STRUCTURE=PASS")


if __name__ == "__main__":
    main()
