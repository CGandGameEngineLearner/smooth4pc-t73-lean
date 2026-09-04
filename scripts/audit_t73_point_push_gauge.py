#!/usr/bin/env python3
"""Audit gauge changes of the auxiliary T73 point-push detector.

Two changes must not be conflated:

* a change of endpoint coordinates conjugates W and transports the cup and
  cap simultaneously, so the matrix coefficient is exactly unchanged;
* composing the chosen point-push loop with another returned pure loop left
  multiplies W while leaving a fixed endpoint cup/cap unchanged.  This is not
  a conjugation and changes the cubic in general.

The inverse loop is a concrete counterexample: W^{-1} followed by W has the
same returned endpoints, permutation and writhe as an admissible loop, but its
detector is zero rather than 2624.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECOMPUTE = ROOT / "scripts" / "recompute_t73_delta3.py"
PUBLIC = ROOT / "data" / "T73_DELTA3_PUBLIC_INPUT.json"
OUTPUT = ROOT / "audit" / "t73_point_push_gauge.json"


def load_recompute():
    spec = importlib.util.spec_from_file_location("recompute_t73_delta3", RECOMPUTE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RECOMPUTE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def free_reduce_word(word: list[int]) -> list[int]:
    stack: list[int] = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return stack


def exponent_sum(word: list[int]) -> int:
    return sum(1 if letter > 0 else -1 for letter in word)


def cubic_for_word(module: Any, word: list[int], u_terms: list[list[int]], ell_terms: list[list[int]]) -> int:
    degree = 6
    vector = module.sparse_vector(88, degree, u_terms)
    delta = module.delta_apply(word, vector)
    epsilon_scalar = module.apply_covector(delta, ell_terms)
    return module.substitute_epsilon_with_h(epsilon_scalar, degree)[3]


def generate() -> dict[str, Any]:
    module = load_recompute()
    data = json.loads(PUBLIC.read_text(encoding="utf-8"))
    b44, _ = module.build_oriented_b44(data)
    word = module.cable_word(b44)

    endpoint_builder = module.load_script("build_t73_endpoint_transport")
    convention = json.loads(
        (ROOT / "data" / "T73_ENDPOINT_CONVENTION.json").read_text(encoding="utf-8")
    )
    pairing = endpoint_builder.public_pairing_terms(convention)
    u_terms = pairing["u_terms"]
    ell_terms = pairing["ell_terms"]

    inverse_loop = module.inverse_word(word)
    changed_word = inverse_loop + word
    reduced_changed = free_reduce_word(changed_word)
    original_cubic = cubic_for_word(module, word, u_terms, ell_terms)
    changed_cubic = cubic_for_word(module, reduced_changed, u_terms, ell_terms)
    result = {
        "schema": "t73_point_push_gauge_audit/v1",
        "original": {
            "word_length": len(word),
            "word_sha256": module.canonical_sha(word),
            "permutation": "identity (pure braid, independently checked upstream)",
            "writhe": exponent_sum(word),
            "h3_cubic": original_cubic,
        },
        "inverse_loop_composition": {
            "word": "W^{-1}W",
            "unreduced_length": len(changed_word),
            "free_reduced_length": len(reduced_changed),
            "writhe": exponent_sum(changed_word),
            "same_returned_endpoint_condition": True,
            "same_first_order_normal_return_condition": True,
            "h3_cubic": changed_cubic,
        },
        "naturality_calculation": {
            "coordinate_change": {
                "transform": [
                    "A -> P A P^{-1}",
                    "u -> P u",
                    "ell -> ell P^{-1}",
                ],
                "identity": "(ell P^{-1})(P A P^{-1}-I)(P u)=ell(A-I)u",
                "invariant": True,
            },
            "loop_composition": {
                "transform": "A -> P A with u,ell fixed",
                "order_three_formula": "K_{PW}=K_P+K_W when P,W are I+O(h^3)",
                "cubic_change": "ell K_P u",
                "invariant": False,
            },
        },
        "adjudication": {
            "bpw_mww_naturality_forces_zero": False,
            "simultaneous_conjugation_is_gauge_invariant": True,
            "chosen_loop_isotopy_invariant": False,
            "original_minus_inverse_composed_cubic": original_cubic - changed_cubic,
            "required_geometric_anchor": (
                "a relative isotopy/surface-cobordism class determined by the embedded AR collar, "
                "with proof that every permitted presentation change acts by simultaneous conjugation"
            ),
        },
    }
    if original_cubic != 2624:
        raise AssertionError("current point-push cubic changed")
    if reduced_changed or changed_cubic != 0:
        raise AssertionError("inverse-loop gauge counterexample did not reduce to identity")
    if exponent_sum(word) != 0 or exponent_sum(changed_word) != 0:
        raise AssertionError("gauge audit changed the zero-writhe condition")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != result:
            raise AssertionError("committed point-push gauge audit differs from rebuild")
    print("T73_POINT_PUSH_GAUGE=NONINVARIANT_UNDER_LOOP_CHOICE")
    print(f"ORIGINAL_H3={result['original']['h3_cubic']}")
    print(f"INVERSE_COMPOSED_H3={result['inverse_loop_composition']['h3_cubic']}")
    print("CONJUGATION_GAUGE=INVARIANT")


if __name__ == "__main__":
    main()
