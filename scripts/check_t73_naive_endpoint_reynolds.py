#!/usr/bin/env python3
"""Negative control: full endpoint Reynolds averaging kills the T73 signal.

This is intentionally *not* the MWW physical-copy beta average.  It prevents
an invalid replacement of coefficient-trace cyclicity by averaging all 44
even and all 44 odd gate passages.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


def load_recompute():
    path = REPOSITORY / "scripts" / "recompute_t73_delta3.py"
    spec = importlib.util.spec_from_file_location("recompute_delta3", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import public recomputation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check() -> dict[str, object]:
    module = load_recompute()
    data = json.loads(
        (REPOSITORY / "data" / "T73_DELTA3_PUBLIC_INPUT.json").read_text(
            encoding="utf-8"
        )
    )
    word44, _ = module.build_oriented_b44(data)
    word88 = module.cable_word(word44)
    degree = data["endpoint_model"]["truncation_degree"]

    invariant_vector = module.sparse_vector(
        88,
        degree,
        [(index, 1) for index in range(0, 88, 2)]
        + [(index, -1) for index in range(1, 88, 2)],
    )
    invariant_covector = (
        [[index, -1] for index in range(0, 88, 2)]
        + [[index, 1] for index in range(1, 88, 2)]
    )
    delta = module.delta_apply(word88, invariant_vector)
    epsilon_value = module.apply_covector(delta, invariant_covector)
    h_value = module.substitute_epsilon_with_h(epsilon_value, degree)
    if h_value != [0] * (degree + 1):
        raise AssertionError("naive full-endpoint Reynolds control is nonzero")
    return {
        "schema": "t73_naive_endpoint_reynolds_negative_control/v1",
        "averaged_groups": ["even gate indices", "odd gate indices"],
        "h_coefficients_0_to_6": h_value,
        "verdict": "ZERO_AS_EXPECTED",
        "warning": (
            "do not replace BPW coefficient-trace cyclicity or MWW owner-copy "
            "beta averaging by full endpoint Reynolds averaging"
        ),
    }


def main() -> None:
    print(json.dumps(check(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
