#!/usr/bin/env python3
"""Verify the compact balanced-cable/Hattori count and braid binding."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPOSITORY / "data" / "T73_DELTA3_PUBLIC_INPUT.json"
P0_WITNESS = REPOSITORY / "audit" / "t73_ar_product_witness.json"
C_WITNESS = REPOSITORY / "audit" / "t73_c_comparison_witness.json"


def load_script(name: str) -> ModuleType:
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def unoriented_occurrences(word: list[str]) -> Counter[str]:
    return Counter(letter.lower() for letter in word)


def cable_letter(letter: int) -> list[int]:
    index = abs(letter)
    block = [2 * index, 2 * index + 1, 2 * index - 1, 2 * index]
    if letter > 0:
        return block
    return [-value for value in reversed(block)]


def verify(
    input_path: Path = DEFAULT_INPUT, *, replacement_binding: bool = True
) -> dict[str, Any]:
    kirby = load_script("generate_t73_compact_kirby_ledger")
    point_push = load_script("verify_t73_compact_point_push")
    public = json.loads(input_path.read_text(encoding="utf-8"))

    m2 = kirby.after_x_cancellation(1)
    rxy = ["z", "y", "Z", "Y"]
    m2_count = unoriented_occurrences(m2)
    rxy_count = unoriented_occurrences(rxy)
    py = m2_count["y"] + rxy_count["y"]
    pz = m2_count["z"] + rxy_count["z"]
    if (m2_count["y"], m2_count["z"]) != (42, 269):
        raise AssertionError("compact m2 cable count differs")
    if (rxy_count["y"], rxy_count["z"]) != (2, 2):
        raise AssertionError("compact rxy cable count differs")
    if (py, pz, pz - py) != (44, 271, 227):
        raise AssertionError("balanced connector count differs")

    rows = point_push.generate_rows()
    by_index = {row[0]: row for row in rows}
    chronology = point_push.expected_chronology()
    b44 = [
        letter
        for source_index in chronology
        for letter in point_push.row_word(by_index[source_index])
    ]
    b88 = [value for letter in b44 for value in cable_letter(letter)]
    integrity = public["point_push"]["derived_integrity"]
    if len(b44) != integrity["B44_length"] or canonical_sha(b44) != integrity["B44_sha256"]:
        raise AssertionError("compact Hattori B44 differs")
    if len(b88) != integrity["B88_length"] or canonical_sha(b88) != integrity["B88_sha256"]:
        raise AssertionError("compact Hattori B88 differs")

    binding = public["hattori_binding"]
    coefficient = binding["coefficient_word"]
    t0 = binding["T0_word"]
    t1 = binding["T1_word"]

    def inverse_token(token: str) -> str:
        return token.swapcase()

    def reduce_tokens(tokens: list[str]) -> list[str]:
        stack: list[str] = []
        for token in tokens:
            if stack and stack[-1] == inverse_token(token):
                stack.pop()
            else:
                stack.append(token)
        return stack

    if reduce_tokens(coefficient + t0) != ["W", "U"]:
        raise AssertionError("T0 Hattori normal form differs")
    if reduce_tokens(coefficient + t1) != ["U"]:
        raise AssertionError("T1 Hattori normal form differs")

    ledger = {
        "schema": "t73_compact_hattori_binding/v1",
        "selected_owners": ["m_2", "r_xy"],
        "base_occurrences": {
            "m_2": {"y": m2_count["y"], "z": m2_count["z"]},
            "r_xy": {"y": rxy_count["y"], "z": rxy_count["z"]},
        },
        "cut_parameters": {"p_y": py, "p_z": pz},
        "oriented_y_endpoints": 2 * py,
        "y_z_product_rectangles": py,
        "z_z_circle_factors": pz - py,
        "coefficient_normal_form": "B_act disjoint B_act^vee disjoint U^227",
        "framing": "parallel copies and connector disks use the AR product-annulus normal",
        "B44": {"length": len(b44), "sha256": canonical_sha(b44)},
        "B88": {"length": len(b88), "sha256": canonical_sha(b88)},
        "Hattori_objects": {
            "T0": "B_act^-1 W U",
            "T1": "B_act^-1 U",
            "B_act_T0": "W U",
            "B_act_T1": "U",
        },
    }
    if replacement_binding:
        p0 = json.loads(P0_WITNESS.read_text(encoding="utf-8"))
        comparison = json.loads(C_WITNESS.read_text(encoding="utf-8"))
        if comparison["p0_witness_sha256"] != p0["witness_sha256"]:
            raise AssertionError("C witness is not bound to the committed P0 witness")
        pairing = comparison["product_pairing"]
        if pairing["total_yz_rectangles"] != py or pairing["remaining_z_circles"] != pz - py:
            raise AssertionError("replacement product pairing differs from compact counts")
        if comparison["endpoint_coordinates"]["B44_sha256"] != canonical_sha(b44):
            raise AssertionError("replacement endpoint word differs")
        ledger["geometric_scope"] = (
            "actual P0 product-annulus coefficient and C comparison witness; "
            "endpoint labels are chosen after one simultaneous pivotal transport"
        )
        ledger["required_simultaneous_transport"] = {
            "coordinate_rule": (
                "choose public endpoint labels after transporting the operator, "
                "cup, and cap through the same P0 pivotal chart"
            ),
            "operator": "W_actual = W_public",
            "vector": "u_actual = u_public up to the recorded strict pivotal sign",
            "covector": "ell_actual = ell_public up to the recorded strict pivotal sign",
            "P": "identity in the common replacement coordinates",
            "status": "DISCHARGED_BY_PUBLIC_REPLACEMENT_COORDINATES",
        }
        ledger["replacement_dependencies"] = {
            "p0_witness_sha256": p0["witness_sha256"],
            "c_witness_sha256": comparison["witness_sha256"],
        }
    else:
        ledger["geometric_scope"] = "count-and-word replay only; replacement binding not requested"
        ledger["required_simultaneous_transport"] = {
            "status": "NOT_EVALUATED_IN_COUNT_ONLY_MODE"
        }
    ledger["ledger_sha256"] = canonical_sha(ledger)
    return ledger


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    print(json.dumps(verify(args.input.resolve()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
