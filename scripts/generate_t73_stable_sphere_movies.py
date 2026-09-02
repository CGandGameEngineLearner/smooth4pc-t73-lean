#!/usr/bin/env python3
"""Generate stable-copy sphere movie ledgers from the five-owner lifts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


BASE_STATE = {
    "m_2": {"negative": 1, "positive": 1},
    "m_3": {"negative": 0, "positive": 0},
    "r_xy": {"negative": 1, "positive": 1},
    "r_yz": {"negative": 0, "positive": 0},
    "r_zx": {"negative": 0, "positive": 0},
}


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


def copy_labels(owner: str, orientation: str, old: int, new: int) -> list[str]:
    return [f"{owner}:{orientation}:old{index}" for index in range(old)] + [
        f"{owner}:{orientation}:new{index}" for index in range(new)
    ]


def generate_ledger() -> dict[str, Any]:
    owner_lift = load_script("generate_t73_owner_sphere_lift").generate_ledger()
    sphere_slides = load_script("generate_t73_sphere_slide_ledger").generate_ledger()
    owners = owner_lift["owner_order"]
    movies: list[dict[str, Any]] = []

    for sphere_index, lift in enumerate(owner_lift["owner_lifts"], start=1):
        target_copy_order: dict[str, dict[str, list[str]]] = {}
        new_leaf_labels: list[str] = []
        old_labels_before: list[str] = []
        old_labels_after: list[str] = []
        for owner, coefficient in zip(owners, lift):
            positive_new = max(coefficient, 0)
            negative_new = max(-coefficient, 0)
            owner_order: dict[str, list[str]] = {}
            for orientation, new_count in (
                ("negative", negative_new),
                ("positive", positive_new),
            ):
                old_count = BASE_STATE[owner][orientation]
                labels = copy_labels(owner, orientation, old_count, new_count)
                owner_order[orientation] = labels
                old_labels_before.extend(
                    f"{owner}:{orientation}:old{index}" for index in range(old_count)
                )
                old_labels_after.extend(label for label in labels if ":old" in label)
                new_leaf_labels.extend(label for label in labels if ":new" in label)
            target_copy_order[owner] = owner_order

        if old_labels_after != old_labels_before:
            raise AssertionError("stable copy order moved an old detector copy")
        leaf_count = sum(abs(value) for value in lift)
        if len(new_leaf_labels) != leaf_count or leaf_count == 0:
            raise AssertionError("sphere leaf count differs from owner lift")

        movie = {
            "sphere": f"S{sphere_index}",
            "owner_lift": lift,
            "leaf_count": leaf_count,
            "split_bands": leaf_count - 1,
            "root_cap": 1,
            "euler_characteristic": leaf_count - (leaf_count - 1) + 1,
            "target_copy_order": target_copy_order,
            "old_detector_labels": old_labels_after,
            "old_factor_constant_permutation": "identity",
            "new_leaf_label_sha256": canonical_sha(new_leaf_labels),
            "movie_normal_form": {
                "undotted": "Id_old tensor iteratedDelta(1)",
                "dotted": "Id_old tensor iteratedDelta(X)",
                "target_row": "oldRow tensor epsilon^leaf_count",
            },
            "transport": (
                "stable positive shuffles preserve old labels; mixed residuals "
                "are pure framed braids and hence Id+O(h)"
            ),
        }
        if movie["euler_characteristic"] != 2:
            raise AssertionError("stable movie is not a sphere")
        movies.append(movie)

    expected_counts = [9920, 1430, 311]
    if [movie["leaf_count"] for movie in movies] != expected_counts:
        raise AssertionError("registered sphere leaf counts differ")

    ledger = {
        "schema": "t73_stable_owner_copy_sphere_movies/v1",
        "base_state": BASE_STATE,
        "owner_lift_ledger_sha256": owner_lift["ledger_sha256"],
        "nielsen_slide_ledger_sha256": sphere_slides["ledger_sha256"],
        "nielsen_operation_count": sphere_slides["operation_count"],
        "private_movie_sectors": {
            "S1": [8, 9],
            "S2": [10, 11],
            "S3": [12, 13],
            "old_detector": [-4, -3],
        },
        "movies": movies,
        "combinatorial_old_label_permutation": "identity",
        "actual_mww_transport_status": (
            "OPEN: the stable label order does not determine pivotal adapters, "
            "foam signs or the actual qHH0 source/target coordinate maps"
        ),
        "cubic_consequence": (
            "if the actual MWW transports have identity degree-zero term, "
            "CubicJet makes their higher corrections invisible"
        ),
    }
    ledger["ledger_sha256"] = canonical_sha(ledger)
    return ledger


def main() -> None:
    print(json.dumps(generate_ledger(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
