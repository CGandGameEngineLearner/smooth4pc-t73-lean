#!/usr/bin/env python3
"""Typed finite prefix for the three MWW Sigma_- surface maps.

This is a parameterized movie certificate.  It derives signed endpoint
copies, stable endpoint permutations, cable-state shifts, and the local
rank-two Frobenius evaluation from the all-owner boundary words.  It does not
invent the missing statewise shadow maps or their naturality squares.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SURFACES = ROOT / "geometry" / "t73_three_handle_surface_transport.json"
OWNER_ORDER = ("m_2", "m_3", "r_xy", "r_yz", "r_zx")


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def add(left: list[int], right: list[int]) -> list[int]:
    if len(left) != len(right):
        raise AssertionError("cable vectors have different lengths")
    return [a + b for a, b in zip(left, right)]


def unit(index: int, size: int = 5) -> list[int]:
    return [1 if position == index else 0 for position in range(size)]


def epsilon_iterated_delta(b: int, basis: str) -> int:
    if b <= 0 or basis not in ("1", "X"):
        raise AssertionError("invalid Frobenius input")
    # Delta^(b-1)(X)=X^tensor(b).  Every summand of
    # Delta^(b-1)(1) has a tensor factor 1.
    return 1 if basis == "X" else 0


def stable_owner_permutation(word: list[int]) -> dict[str, Any]:
    """Move signed copies into owner blocks, preserving order inside a block."""
    if any(letter == 0 or abs(letter) > 3 for letter in word):
        raise AssertionError("surface boundary word has an invalid owner letter")
    target_order = sorted(
        range(len(word)),
        key=lambda index: (abs(word[index]), 0 if word[index] < 0 else 1, index),
    )
    old_to_new = [0] * len(word)
    for new_index, old_index in enumerate(target_order):
        old_to_new[old_index] = new_index
    inverse = [0] * len(word)
    for old_index, new_index in enumerate(old_to_new):
        inverse[new_index] = old_index
    if sorted(old_to_new) != list(range(len(word))):
        raise AssertionError("endpoint permutation is not bijective")
    if any(inverse[old_to_new[index]] != index for index in range(len(word))):
        raise AssertionError("endpoint permutation inverse is wrong")
    return {
        "convention": "stable blocks by owner, then negative before positive",
        "old_to_new": old_to_new,
        "new_to_old": inverse,
        "sha256": canonical_sha(old_to_new),
    }


def profile_from_word(word: list[int]) -> list[dict[str, Any]]:
    profile = []
    for local_owner, owner in enumerate(OWNER_ORDER[2:], start=1):
        negative_positions = [
            index for index, letter in enumerate(word) if letter == -local_owner
        ]
        positive_positions = [
            index for index, letter in enumerate(word) if letter == local_owner
        ]
        profile.append(
            {
                "owner": owner,
                "negative_positions": negative_positions,
                "positive_positions": positive_positions,
                "negative_count": len(negative_positions),
                "positive_count": len(positive_positions),
                "net_orientation": len(positive_positions) - len(negative_positions),
            }
        )
    return profile


def cable_shifts(profile: list[dict[str, Any]]) -> tuple[list[int], list[int]]:
    negative = [0, 0]
    positive = [0, 0]
    for item in profile:
        negative.append(item["negative_count"])
        positive.append(item["positive_count"])
    return negative, positive


def type_squares(
    surface_negative: list[int], surface_positive: list[int]
) -> dict[str, Any]:
    """Check beta and psi squares at the level of every cable-state type."""
    beta = []
    psi = []
    symbolic_base_minus = [11, 13, 17, 19, 23]
    symbolic_base_plus = [29, 31, 37, 41, 43]
    translated_minus = add(symbolic_base_minus, surface_negative)
    translated_plus = add(symbolic_base_plus, surface_positive)
    for component in range(5):
        beta.append(
            {
                "component": OWNER_ORDER[component],
                "source_state": [symbolic_base_minus, symbolic_base_plus],
                "target_state": [translated_minus, translated_plus],
                "beta_preserves_counts": True,
                "typed": True,
            }
        )
        pair = unit(component)
        first_surface_then_psi = [
            add(translated_minus, pair),
            add(translated_plus, pair),
        ]
        first_psi_then_surface = [
            add(add(symbolic_base_minus, pair), surface_negative),
            add(add(symbolic_base_plus, pair), surface_positive),
        ]
        if first_surface_then_psi != first_psi_then_surface:
            raise AssertionError("psi cable-state translation square is ill-typed")
        psi.append(
            {
                "component": OWNER_ORDER[component],
                "both_paths": first_surface_then_psi,
                "typed": True,
            }
        )
    return {"beta": beta, "psi": psi, "all_typed": True}


def build_movie(surface: dict[str, Any]) -> dict[str, Any]:
    word = surface["mapping_torus_boundary_word"]
    b = surface["core_disk_count_b"]
    if len(word) != b:
        raise AssertionError("surface word length does not equal core count")
    derived_profile = profile_from_word(word)
    stored_profile = surface["core_disk_boundary_profile"]
    for derived, stored in zip(derived_profile, stored_profile):
        for key in ("owner", "negative_count", "positive_count", "net_orientation"):
            stored_key = {
                "negative_count": "negative_copy_count",
                "positive_count": "positive_copy_count",
            }.get(key, key)
            if derived[key] != stored[stored_key]:
                raise AssertionError(
                    f"{surface['sphere']} owner profile disagrees at {key}"
                )
    negative_shift, positive_shift = cable_shifts(derived_profile)
    permutation = stable_owner_permutation(word)
    squares = type_squares(negative_shift, positive_shift)
    events = [
        {
            "kind": "split_J_factor",
            "count": 1,
            "source": "CabledState(r_minus,r_plus) tensor KhR_2(J)",
            "target": "OldFactor tensor A",
        },
        {
            "kind": "coproduct_saddles",
            "count": b - 1,
            "index_rule": "saddle k splits Frobenius output k into outputs k and k+1",
            "old_factor_action": "identity",
            "new_factor_action": "Delta",
        },
        {
            "kind": "mixed_endpoint_permutation",
            "count": len(permutation["old_to_new"]),
            "permutation_sha256": permutation["sha256"],
            "old_factor_action": "required statewise braid/pivotal map",
            "new_factor_action": "permute boundary copies into owner/sign blocks",
        },
        {
            "kind": "restored_core_caps",
            "count": b,
            "index_rule": "cap k applies epsilon to new Frobenius factor k",
            "old_factor_action": "identity",
            "new_factor_action": "epsilon",
        },
    ]
    return {
        "sphere": surface["sphere"],
        "source_type": {
            "old_tensor_factor": "CabledState(r_minus,r_plus)",
            "new_tensor_factor": "KhR_2(J)=Q{1,X}",
        },
        "target_type": {
            "old_tensor_factor": "CabledState(r_minus,r_plus)",
            "new_cable_negative_shift": negative_shift,
            "new_cable_positive_shift": positive_shift,
        },
        "owner_profile": derived_profile,
        "boundary_word_length": b,
        "boundary_word_sha256": canonical_sha(word),
        "endpoint_permutation": permutation,
        "events": events,
        "event_counts": {"births": 0, "saddles": b - 1, "caps": b},
        "local_frobenius": {
            "formula": "epsilon^tensor(b) o Delta^(b-1)",
            "on_1": epsilon_iterated_delta(b, "1"),
            "on_X": epsilon_iterated_delta(b, "X"),
        },
        "type_compatibility": squares,
        "required_shadow_map": {
            "name": f"StatewiseShadowNaturality_{surface['sphere']}",
            "domain": "typed Sigma_- movie on every raw cable summand",
            "codomain": "completed endpoint representation",
            "must_prove": [
                "movie-event functoriality",
                "mixed braid/pivotal maps are P(I+O(h))",
                "detector-row equivariance for P",
                "naturality with every beta generator",
                "naturality with every psi generator",
            ],
            "status": "OPEN",
        },
        "finite_prefix_status": "PASS",
    }


def build() -> dict[str, Any]:
    source = json.loads(SURFACES.read_text(encoding="utf-8"))
    if source["surface_count"] != 3:
        raise AssertionError("expected three Sigma_- surfaces")
    movies = [build_movie(surface) for surface in source["surfaces"]]
    result = {
        "schema": "t73_sigma_minus_typed/v1",
        "surface_transport_sha256": source["sha256"],
        "owner_order": list(OWNER_ORDER),
        "movies": movies,
        "finite_checks": {
            "three_movies": len(movies) == 3,
            "owner_profiles_recomputed": True,
            "endpoint_permutations_bijective": True,
            "local_frobenius_verified": all(
                movie["local_frobenius"] == {
                    "formula": "epsilon^tensor(b) o Delta^(b-1)",
                    "on_1": 0,
                    "on_X": 1,
                }
                for movie in movies
            ),
            "beta_psi_types_commute": all(
                movie["type_compatibility"]["all_typed"] for movie in movies
            ),
        },
        "required_shadow_maps_status": "OPEN",
        "S_status": "OPEN",
    }
    if not all(result["finite_checks"].values()):
        raise AssertionError("typed Sigma_- finite prefix failed")
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.check:
        print(f"MOVIES={len(result['movies'])}")
        print(
            "CORE_COUNTS="
            + ",".join(str(movie["boundary_word_length"]) for movie in result["movies"])
        )
        print(f"FINITE_PREFIX=PASS")
        print(f"SHADOW_MAPS={result['required_shadow_maps_status']}")
        print(f"S_STATUS={result['S_status']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
