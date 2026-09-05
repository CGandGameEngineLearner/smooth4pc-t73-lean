#!/usr/bin/env python3
"""Verify that the actual railroad ledger is not yet a complete planar PD."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_actual_railroad_standard_pd_gap.json"
RAILROAD = ROOT / "geometry/t73_final_railroad_word_binding.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    if data["completion_status"] != "OPEN_RAILROAD_CLOSURE_CROSSINGS_MISSING":
        raise AssertionError("railroad PD gap was incorrectly closed")
    if data["actual_railroad_word_binding_sha256"] != railroad["sha256"] or data["final_component_passage_cycles_sha256"] != cycles["sha256"]:
        raise AssertionError("railroad PD gap has stale sources")
    signed_sums = Counter()
    for crossing in railroad["actual_railroad_crossings"]:
        pair = tuple(sorted((crossing["over_owner"], crossing["under_owner"])))
        signed_sums[pair] += crossing["sign"]
    odd = {
        "/".join(pair): value
        for pair, value in sorted(signed_sums.items())
        if value % 2
    }
    if odd != {"m_2/m_3": -3, "m_3/r_yz": 1}:
        raise AssertionError("railroad odd-pair obstruction changed")
    reduced_letter_count = sum(
        record["reduced_length"] for record in railroad["components"].values()
    )
    if reduced_letter_count != 1779:
        raise AssertionError("actual reduced handle-word length changed")
    expected_candidate_count = 1878 + 2 * reduced_letter_count + 1
    if data["candidate_total_crossing_occurrences"] != expected_candidate_count:
        raise AssertionError("candidate dotted/railroad crossing count changed")
    if data["standard_pd_code"] is not None:
        raise AssertionError("standard PD rows were emitted despite odd mixed parity")
    return {
        "verdict": "PASS_FAIL_CLOSED_ACTUAL_RAILROAD_PD_GAP",
        "actual_railroad_crossings": 1878,
        "reduced_handle_letters": reduced_letter_count,
        "candidate_crossing_occurrences": expected_candidate_count,
        "odd_mixed_pairs": odd,
        "standard_pd_emitted": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
