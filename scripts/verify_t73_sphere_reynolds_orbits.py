#!/usr/bin/env python3
"""Verify the physical-copy Reynolds orbits after each sphere owner lift."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


BASE_COUNTS = {
    "m_2": {"negative": 1, "positive": 1},
    "m_3": {"negative": 0, "positive": 0},
    "r_xy": {"negative": 1, "positive": 1},
    "r_yz": {"negative": 0, "positive": 0},
    "r_zx": {"negative": 0, "positive": 0},
}


def load_owner_lifts() -> ModuleType:
    path = Path(__file__).resolve().parent / "generate_t73_owner_sphere_lift.py"
    spec = importlib.util.spec_from_file_location("owner_lifts", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import owner lift generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def apply_lift(
    owners: list[str], lift: list[int]
) -> dict[str, dict[str, int]]:
    counts = {
        owner: dict(orientations) for owner, orientations in BASE_COUNTS.items()
    }
    for owner, coefficient in zip(owners, lift):
        if coefficient >= 0:
            counts[owner]["positive"] += coefficient
        else:
            counts[owner]["negative"] += -coefficient
    return counts


def detector_selection_count(counts: dict[str, dict[str, int]]) -> int:
    result = 1
    for owner in ("m_2", "r_xy"):
        result *= counts[owner]["negative"] * counts[owner]["positive"]
    return result


def verify() -> dict[str, Any]:
    lift_ledger = load_owner_lifts().generate_ledger()
    owners = lift_ledger["owner_order"]
    rows: list[dict[str, Any]] = []
    for index, lift in enumerate(lift_ledger["owner_lifts"], start=1):
        counts = apply_lift(owners, lift)
        orbit_size = detector_selection_count(counts)
        m2_choices = counts["m_2"]["negative"] * counts["m_2"]["positive"]
        rxy_choices = counts["r_xy"]["negative"] * counts["r_xy"]["positive"]
        if m2_choices != 1:
            raise AssertionError("sphere lift changed the selected m2 choice orbit")
        if orbit_size != rxy_choices:
            raise AssertionError("unexpected detector selection factorization")
        rows.append(
            {
                "sphere": f"S{index}",
                "owner_lift": lift,
                "target_copy_counts": counts,
                "m2_selection_orbit": m2_choices,
                "rxy_selection_orbit": rxy_choices,
                "detector_selection_orbit": orbit_size,
                "beta_group": (
                    f"S_{counts['r_xy']['negative']} x "
                    f"S_{counts['r_xy']['positive']} on r_xy copies"
                ),
                "transitivity": (
                    "the sign-preserving beta permutation group is transitive "
                    "on choices of one negative and one positive r_xy copy"
                ),
                "normalized_pullback": (
                    "every orbit term is simultaneous beta conjugate to the "
                    "canonical detector term; the Reynolds average has value one term"
                ),
            }
        )

    expected = [1312, 190, 42]
    if [row["detector_selection_orbit"] for row in rows] != expected:
        raise AssertionError("registered sphere Reynolds orbit sizes differ")

    ledger = {
        "schema": "t73_sphere_physical_copy_reynolds/v1",
        "base_detector_selection_orbit": detector_selection_count(BASE_COUNTS),
        "sphere_orbits": rows,
        "orbit_sizes": expected,
        "required_naturality": (
            "the cubic detector row must be invariant under simultaneous beta "
            "transport, not under naive averaging of all gate endpoints"
        ),
        "consequence": (
            "assuming beta cubic naturality, cross terms in which a new sphere "
            "copy is selected reproduce the same old detector row"
        ),
    }
    ledger["ledger_sha256"] = canonical_sha(ledger)
    return ledger


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
