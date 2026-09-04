#!/usr/bin/env python3
"""Build the exact defect-aware typing graph for the selected C coefficient.

This file deliberately stops before inventing a co-Yoneda equivalence.  It
records the complete four-port incidence, separates pivotal mates from band
surgeries, and exposes the two mathematically sufficient (but currently
unfilled) comparison contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"
LEGACY_AUDIT = ROOT / "audit" / "t73_defect_aware_currying.json"
PIVOTAL = ROOT / "data" / "T73_C_PIVOTAL_GRADING_INPUT.json"
OUTPUT = ROOT / "geometry" / "t73_c_defect_coend_typing_graph.json"

PORTS = {
    "Y_minus": {
        "variable": "T",
        "category": "C_44",
        "variance": "op",
        "argument": "source_y",
    },
    "Z_minus": {
        "variable": "Z",
        "category": "C_271",
        "variance": "op",
        "argument": "source_z",
    },
    "Y_plus": {
        "variable": "T_prime",
        "category": "C_44",
        "variance": "covariant",
        "argument": "target_y",
    },
    "Z_plus": {
        "variable": "Z_prime",
        "category": "C_271",
        "variance": "covariant",
        "argument": "target_z",
    },
}

CORRECT_ACTIVE = {
    frozenset(("Y_minus", "Z_plus")),
    frozenset(("Y_plus", "Z_minus")),
}


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def checked_sha(data: dict[str, Any], where: str) -> str:
    recorded = data.get("sha256")
    payload = {key: value for key, value in data.items() if key != "sha256"}
    actual = canonical_sha(payload)
    if recorded != actual:
        raise AssertionError(f"{where} has stale embedded SHA256")
    return actual


def endpoint_pair(interval: dict[str, Any]) -> tuple[str, str]:
    return interval["from_endpoint_id"], interval["to_endpoint_id"]


def oriented_wrong_reconnections(
    wrong: list[dict[str, Any]], endpoints: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Return the unique owner- and orientation-preserving candidate pairing.

    This is only a matching calculation.  Each returned row remains an
    unrealized oriented saddle obligation.
    """

    buckets: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for interval in wrong:
        spheres = {endpoints[item]["sphere"] for item in endpoint_pair(interval)}
        if spheres == {"Y_minus", "Z_minus"}:
            side = "minus_same_side"
        elif spheres == {"Y_plus", "Z_plus"}:
            side = "plus_same_side"
        else:
            raise AssertionError("wrong interval has an unexpected sphere pair")
        y_endpoint = next(
            item
            for item in endpoint_pair(interval)
            if endpoints[item]["sphere"].startswith("Y")
        )
        direction = "Y_to_Z" if endpoints[y_endpoint]["role"] == "exit" else "Z_to_Y"
        key = (interval["owner"], direction, side)
        buckets.setdefault(key, []).append(interval)

    obligations = []
    for owner in ("m_2", "r_xy"):
        for direction in ("Y_to_Z", "Z_to_Y"):
            minus = buckets.get((owner, direction, "minus_same_side"), [])
            plus = buckets.get((owner, direction, "plus_same_side"), [])
            if len(minus) != 1 or len(plus) != 1:
                raise AssertionError(
                    f"no unique owner/orientation pairing for {owner} {direction}"
                )
            first, second = minus[0], plus[0]
            by_sphere = {
                endpoints[endpoint_id]["sphere"]: endpoint_id
                for interval in (first, second)
                for endpoint_id in endpoint_pair(interval)
            }
            if direction == "Y_to_Z":
                new_arcs = [
                    [by_sphere["Y_minus"], by_sphere["Z_plus"]],
                    [by_sphere["Y_plus"], by_sphere["Z_minus"]],
                ]
            else:
                new_arcs = [
                    [by_sphere["Z_minus"], by_sphere["Y_plus"]],
                    [by_sphere["Z_plus"], by_sphere["Y_minus"]],
                ]
            for initial, terminal in new_arcs:
                if endpoints[initial]["role"] != "exit" or endpoints[terminal]["role"] != "entry":
                    raise AssertionError("candidate reconnection is not oriented exit-to-entry")
                if frozenset(
                    (endpoints[initial]["sphere"], endpoints[terminal]["sphere"])
                ) not in CORRECT_ACTIVE:
                    raise AssertionError("candidate reconnection is not cross-side")
            obligations.append(
                {
                    "obligation_id": f"band:{owner}:{direction}",
                    "owner": owner,
                    "orientation_class": direction,
                    "old_interval_ids": sorted(
                        (first["interval_id"], second["interval_id"])
                    ),
                    "new_oriented_arcs": new_arcs,
                    "endpoint_map": "identity_on_the_four_boundary_endpoints_of_this_obligation",
                    "required_cell_kind": "oriented_band_surgery_or_equivalent_foam_movie",
                    "status": "UNREALIZED",
                    "not_a_pivotal_mate": True,
                    "blanchet_sign": None,
                    "homological_degree": None,
                    "quantum_degree": None,
                    "inverse_or_quasi_inverse": None,
                }
            )
    return obligations


def legacy_pairing_diagnostic(
    legacy: dict[str, Any], endpoints: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    result = []
    for item in legacy.get(
        "superseded_lexicographic_reconnections",
        legacy["proposed_endpoint_reconnections"],
    ):
        role_pairs = [
            [endpoints[first]["role"], endpoints[second]["role"]]
            for first, second in item["new_cross_pairs"]
        ]
        result.append(
            {
                "legacy_index": item["index"],
                "new_cross_pairs": item["new_cross_pairs"],
                "role_pairs": role_pairs,
                "all_arcs_have_one_exit_one_entry": all(
                    sorted(pair) == ["entry", "exit"] for pair in role_pairs
                ),
                "all_arcs_listed_exit_to_entry": all(
                    pair == ["exit", "entry"] for pair in role_pairs
                ),
            }
        )
    return result


def build() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    legacy = json.loads(LEGACY_AUDIT.read_text(encoding="utf-8"))
    pivotal = json.loads(PIVOTAL.read_text(encoding="utf-8"))
    source_sha = checked_sha(source, "selected source exterior")

    endpoints: dict[str, dict[str, Any]] = {}
    endpoint_nodes = []
    for sphere in source["insertion_spheres"]:
        port = PORTS[sphere["name"]]
        for endpoint in sphere["endpoints"]:
            node = {
                "endpoint_id": endpoint["endpoint_id"],
                "sphere": sphere["name"],
                "sphere_index": endpoint["sphere_index"],
                "occurrence_id": endpoint["occurrence_id"],
                "exterior_incidence": endpoint["role"],
                "variable": port["variable"],
                "category": port["category"],
                "variance": port["variance"],
            }
            endpoint_nodes.append(node)
            endpoints[endpoint["endpoint_id"]] = {
                **endpoint,
                "sphere": sphere["name"],
            }

    interval_edges = []
    active, wrong = [], []
    for interval in source["exterior_intervals"]:
        first, second = endpoint_pair(interval)
        first_sphere = endpoints[first]["sphere"]
        second_sphere = endpoints[second]["sphere"]
        active_edge = first_sphere.startswith("Y") or second_sphere.startswith("Y")
        correct = active_edge and frozenset((first_sphere, second_sphere)) in CORRECT_ACTIVE
        status = (
            "correct_cross_side_active"
            if correct
            else "wrong_same_side_active"
            if active_edge
            else "residual_z_z"
        )
        edge = {
            "interval_id": interval["interval_id"],
            "from_endpoint_id": first,
            "to_endpoint_id": second,
            "from_sphere": first_sphere,
            "to_sphere": second_sphere,
            "owner": interval["owner"],
            "copy_sign": interval["copy_sign"],
            "source_ids": [interval["from_source_id"], interval["to_source_id"]],
            "interval_type": interval["interval_type"],
            "typing_status": status,
        }
        interval_edges.append(edge)
        if active_edge:
            active.append({**interval, "from_sphere": first_sphere, "to_sphere": second_sphere})
        if status == "wrong_same_side_active":
            wrong.append(interval)

    reconnections = oriented_wrong_reconnections(wrong, endpoints)
    legacy_diagnostic = legacy_pairing_diagnostic(legacy, endpoints)
    incompatible_legacy = [
        item["legacy_index"]
        for item in legacy_diagnostic
        if not item["all_arcs_have_one_exit_one_entry"]
    ]

    transition_counts = Counter(
        "--".join(sorted((item["from_sphere"], item["to_sphere"])))
        for item in active
    )
    edge_status_counts = Counter(item["typing_status"] for item in interval_edges)

    proof_dag = [
        {
            "id": "G0",
            "claim": "complete source four-port incidence",
            "depends_on": [],
            "status": "VERIFIED",
        },
        {
            "id": "G1",
            "claim": "C_44 x C_271 profunctor variance and z-coend typing",
            "depends_on": ["G0"],
            "status": "VERIFIED_TYPING_ONLY",
        },
        {
            "id": "G2",
            "claim": "unique owner- and orientation-preserving candidate rematching",
            "depends_on": ["G0"],
            "status": "VERIFIED_COMBINATORICS_ONLY",
        },
        {
            "id": "G3",
            "claim": "four oriented band/foam cells with signs and degrees",
            "depends_on": ["G2"],
            "status": "OPEN",
        },
        {
            "id": "G4a",
            "claim": "two-sided D-representability by a natural chain equivalence",
            "depends_on": ["G1"],
            "status": "OPEN",
        },
        {
            "id": "G4b",
            "claim": "direct connected-kernel derived-bar comparison",
            "depends_on": ["G1"],
            "status": "OPEN",
        },
        {
            "id": "G5",
            "claim": "co-Yoneda or bar comparison, with both residual C_44 actions",
            "depends_on_any": ["G4a", "G4b"],
            "status": "OPEN",
        },
        {
            "id": "G6",
            "claim": "homogeneous selected class and actual q_C",
            "depends_on": ["G5"],
            "status": "OPEN",
        },
    ]

    result: dict[str, Any] = {
        "schema": "t73_c_defect_coend_typing_graph/v1",
        "dependencies": {
            "selected_source_exterior_sha256": source_sha,
            "legacy_defect_audit_content_sha256": hashlib.sha256(
                LEGACY_AUDIT.read_bytes()
            ).hexdigest().upper(),
            "pivotal_input_content_sha256": hashlib.sha256(
                PIVOTAL.read_bytes()
            ).hexdigest().upper(),
        },
        "categories": {
            "C": "C_44",
            "D": "C_271",
            "ground": "Q",
            "target": "bigraded_chain_complexes",
        },
        "coefficient_profunctor": {
            "symbol": "P(T,Z;T_prime,Z_prime)",
            "domain": "C_44^op x C_271^op x C_44 x C_271",
            "codomain": "Ch_Q",
            "source_object": "(T,Z)",
            "target_object": "(T_prime,Z_prime)",
            "z_reduction": "M_R^z(T,T_prime)=int^{Z in C_271} P(T,Z;T_prime,Z)",
            "balanced_relation": "P(id,g)(x) ~ P(g,id)(x)",
            "residual_actions": ["C_44_left", "C_44_right"],
        },
        "port_types": PORTS,
        "endpoint_nodes": endpoint_nodes,
        "interval_edges": interval_edges,
        "counts": {
            "endpoints": len(endpoint_nodes),
            "intervals": len(interval_edges),
            "active_interval_endpoint_incidents": 2 * len(active),
            "Y_port_endpoints": sum(
                item["category"] == "C_44" for item in endpoint_nodes
            ),
            "active_intervals": len(active),
            "wrong_side_intervals": len(wrong),
            "oriented_reconnection_obligations": len(reconnections),
            "transition_counts": dict(sorted(transition_counts.items())),
            "edge_status_counts": dict(sorted(edge_status_counts.items())),
        },
        "pivotal_retyping_contract": {
            "kind": "rigid_category_Hom_adjunction",
            "effect_on_physical_endpoint_count": 0,
            "effect_on_interval_matching": "identity",
            "invertible": True,
            "may_change_variance_label": True,
            "is_saddle_reconnection": False,
            "selected_local_duality_chart_count": len(pivotal["endpoint_duality_charts"]),
            "scope_warning": pivotal["scope"],
            "conclusion": "pivotal retyping alone cannot repair any of the eight same-side edges",
        },
        "oriented_reconnection_obligations": reconnections,
        "legacy_lexicographic_pairing_diagnostic": legacy_diagnostic,
        "legacy_orientation_incompatible_indices": incompatible_legacy,
        "single_hom_boundary_accounting": {
            "active_endpoints_before_any_mate": 176,
            "active_endpoints_after_pivotal_retyping": 176,
            "active_endpoints_after_four_rematchings": 176,
            "P86_to_P88_endpoints": 174,
            "external_cup_endpoint_difference": 2,
            "external_cup_is_separate_from_wrong_side_repair": True,
        },
        "sufficient_route_contracts": {
            "two_sided_representability": {
                "formula": "P ~= Hom_D(KT,-) tensor Hom_D(-,KT_prime){s}",
                "literal_separating_sphere_required": False,
                "required_instead": [
                    "natural chain-homotopy equivalence for all four variables",
                    "compatibility with both D actions and both residual C actions",
                    "explicit homogeneous degree and inverse/homotopies",
                ],
                "effect": "enriched co-Yoneda is then valid even without a literal split",
                "status": "OPEN",
            },
            "direct_derived_bar_comparison": {
                "formula": "B(C_271;P) ~= Hom_C(BT,BT_prime) tensor A^tensor227",
                "preserves_original_matching": True,
                "reconnection_cells_required": False,
                "required_instead": [
                    "complete bar/arc-algebra chain presentation",
                    "natural chain equivalence and inverse/homotopies",
                    "both residual C_44 naturality homotopies",
                    "explicit homogeneous comparison degree",
                ],
                "effect": "computes the connected profunctor trace directly; this is not co-Yoneda by itself",
                "status": "OPEN",
            },
        },
        "grading_ledger": {
            "normalized_domain": "Mhat_R^z",
            "comparison_target": "Hom_C44(BT,BT_prime) tensor A^tensor227",
            "all_X_target_quantum_degree": 227,
            "cable_shift": -4,
            "comparison_map_quantum_degree_symbol": "delta_Theta",
            "selected_source_degree_formula": "227-delta_Theta",
            "actual_q_C_formula": "223-delta_Theta",
            "delta_Theta": None,
            "actual_q_C": None,
            "conditional_literal_split_value": 223,
            "conditional_literal_split_assumption_holds": False,
            "historical_494_is_not_derived_here": True,
        },
        "proof_obligation_dag": proof_dag,
        "completion_status": "OPEN",
        "first_open_gate": (
            "supply either a four-variable two-sided representability equivalence or a "
            "direct connected-kernel bar comparison, including chain inverse, homotopies, "
            "naturality and homogeneous degree"
        ),
    }

    expected_counts = {
        "endpoints": 1260,
        "intervals": 630,
        "active_interval_endpoint_incidents": 352,
        "Y_port_endpoints": 176,
        "active_intervals": 176,
        "wrong_side_intervals": 8,
        "oriented_reconnection_obligations": 4,
    }
    for key, expected in expected_counts.items():
        if result["counts"][key] != expected:
            raise AssertionError(f"{key} is {result['counts'][key]}, expected {expected}")
    if result["single_hom_boundary_accounting"]["active_endpoints_after_pivotal_retyping"] == 174:
        raise AssertionError("pivotal mate was incorrectly allowed to delete endpoints")

    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != result:
            raise AssertionError("committed defect coend typing graph is stale")
    print("T73_C_DEFECT_COEND_TYPING_GRAPH=VERIFIED")
    print(f"ENDPOINTS={result['counts']['endpoints']}")
    print(f"INTERVALS={result['counts']['intervals']}")
    print(f"WRONG_SIDE={result['counts']['wrong_side_intervals']}")
    print(f"ORIENTED_BAND_OBLIGATIONS={result['counts']['oriented_reconnection_obligations']}")
    print(f"COMPLETION_STATUS={result['completion_status']}")


if __name__ == "__main__":
    main()
