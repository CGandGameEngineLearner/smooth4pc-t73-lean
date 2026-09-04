#!/usr/bin/env python3
"""Inventory the complete T73 geometry pipeline, including prefixes and gates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_complete_geometry_bundle_manifest.v2.json"
SCHEMA = ROOT / "data" / "T73_COMPLETE_GEOMETRY_BUNDLE_V2.schema.json"

SPECS = (
    ("selected_c_v1_bundle", "geometry/t73_complete_geometry_bundle_manifest.v1.json", "VERIFIED_CORE_BUNDLE"),
    ("defect_coend_typing", "geometry/t73_c_defect_coend_typing_graph.json", "VERIFIED_TYPING_ONLY"),
    ("ar_source_coordinate_atlas", "geometry/t73_ar_source_coordinate_atlas.json", "VERIFIED_PREFIX_ONLY"),
    ("pd_truth_input", "geometry/examples/seven_component_framed_unlink_input.json", "VERIFIED_FIXTURE_ONLY"),
    ("pd_truth_export", "geometry/examples/seven_component_framed_unlink_export.json", "VERIFIED_FIXTURE_ONLY"),
    ("pd_open_source_receipt", "geometry/examples/seven_component_framed_unlink_open_source_receipt.json", "VERIFIED_FIXTURE_ONLY"),
    ("tetgen_source_prefix10", "geometry/examples/t73_selected_source_tetrahedral_prefix10.json", "VERIFIED_PREFIX_ONLY"),
    ("gmsh_source_prefix20_receipt", "audit/t73_selected_source_gmsh_prefix20.json", "VERIFIED_RESOURCE_RECEIPT_ONLY"),
    ("gmsh_source_prefix10_frame", "geometry/examples/t73_selected_source_gmsh_prefix10_frame.json", "VERIFIED_PREFIX_ONLY"),
    ("gmsh_source_prefix10_verification", "audit/t73_selected_source_gmsh_prefix10_frame_verification.json", "VERIFIED_PREFIX_RECEIPT_ONLY"),
)


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def embedded_sha(data: dict[str, Any], field: str = "sha256") -> str | None:
    recorded = data.get(field)
    if recorded is None:
        return None
    payload = {key: value for key, value in data.items() if key != field}
    if recorded != canonical_sha(payload):
        raise AssertionError(f"embedded {field} is stale")
    return recorded


def verify_live_artifacts() -> dict[str, dict[str, Any]]:
    data = {
        artifact_id: json.loads((ROOT / relative).read_text(encoding="utf-8"))
        for artifact_id, relative, _status in SPECS
    }
    v1_builder = load_module(
        "scripts/build_t73_complete_geometry_bundle.py", "t73_bundle_v1_for_v2"
    )
    v1_artifacts = v1_builder.load_artifacts()
    v1_builder.validate_manifest(data["selected_c_v1_bundle"], v1_artifacts)

    coend_builder = load_module(
        "scripts/build_t73_c_defect_coend_typing_graph.py", "t73_coend_for_v2"
    )
    if data["defect_coend_typing"] != coend_builder.build():
        raise AssertionError("defect coend typing graph is stale")

    atlas_builder = load_module(
        "scripts/build_t73_ar_source_coordinate_atlas.py", "t73_atlas_for_v2"
    )
    if data["ar_source_coordinate_atlas"] != atlas_builder.build(write=False):
        raise AssertionError("AR source atlas is stale")

    tetra_verifier = load_module(
        "scripts/verify_t73_selected_source_tetrahedral_frame.py",
        "t73_tetra_prefix_for_v2",
    )
    tetra_result = tetra_verifier.inspect(
        ROOT / "geometry/examples/t73_selected_source_tetrahedral_prefix10.json"
    )
    if tetra_result.get("verdict") != "PASS_PREFIX_ONLY":
        raise AssertionError(f"TetGen prefix is not independently verified: {tetra_result}")
    gmsh_frame_receipt = load_module(
        "scripts/build_t73_gmsh_frame_verification_receipt.py",
        "t73_gmsh_frame_receipt_for_v2",
    )
    gmsh_frame_receipt.check_files(data["gmsh_source_prefix10_verification"])

    gmsh_verifier = load_module(
        "scripts/verify_t73_selected_source_gmsh_probe.py",
        "t73_gmsh_probe_for_v2",
    )
    if gmsh_verifier.verify(data["gmsh_source_prefix20_receipt"])["verdict"] != "PASS_RECEIPT_ONLY":
        raise AssertionError("Gmsh prefix-20 resource receipt is not verified")

    export = data["pd_truth_export"]
    receipt = data["pd_open_source_receipt"]
    if export.get("status") != "PASS" or export.get("component_order") != [
        "m_2", "m_3", "r_xy", "r_yz", "r_zx", "dotted_y", "dotted_z"
    ]:
        raise AssertionError("PD truth export is not the seven-component contract fixture")
    if receipt.get("export_sha256") != export.get("sha256"):
        raise AssertionError("open-source receipt is stale relative to PD export")
    if (
        receipt.get("spherogram_components") != 7
        or receipt.get("snappy_cusps") != 7
        or receipt.get("snappy_tetrahedra") != 36
        or receipt.get("regina_tetrahedra") != 36
    ):
        raise AssertionError("open-source topology receipt counts changed")
    for artifact_id in data:
        if artifact_id == "selected_c_v1_bundle":
            embedded_sha(data[artifact_id], "manifest_payload_sha256")
        else:
            embedded_sha(data[artifact_id])
    return data


def build() -> dict[str, Any]:
    data = verify_live_artifacts()
    entries = []
    for artifact_id, relative, evidence_status in SPECS:
        path = ROOT / relative
        payload_field = (
            "manifest_payload_sha256"
            if artifact_id == "selected_c_v1_bundle"
            else "sha256"
        )
        entries.append(
            {
                "id": artifact_id,
                "path": relative,
                "schema": data[artifact_id].get("schema"),
                "content_sha256": file_sha(path),
                "payload_sha256": data[artifact_id].get(payload_field),
                "evidence_status": evidence_status,
                "t73_completion_status": "OPEN",
            }
        )
    source = json.loads(
        (ROOT / "geometry/t73_selected_source_exterior.json").read_text(
            encoding="utf-8"
        )
    )
    gates = [
        {
            "id": "actual_defect_coend_chain_equivalence",
            "required_path": "geometry/t73_c_defect_coend_witness.json",
            "status": "OPEN",
            "reason": "no R1 representability or R2 connected-bar chain-equivalence witness",
        },
        {
            "id": "actual_complete_kirby_input",
            "required_path": "geometry/t73_full_handle_diagram_input.json",
            "status": "OPEN",
            "reason": "AR charts have no common cut/surgery dotted-circle presentation and band splices",
        },
        {
            "id": "complete_630_ribbon_tetrahedral_frame",
            "required_path": "geometry/t73_selected_source_tetrahedral_frame.json",
            "status": "OPEN",
            "reason": "ten-ribbon prefix passes; monolithic 20-ribbon TetGen exceeds safe memory",
        },
        {
            "id": "actual_ar_relative_binding",
            "required_path": "geometry/t73_actual_to_selected_source_isotopy.json",
            "status": "OPEN",
            "reason": "canonical selected source still records actual_ar_relative_isotopy_proved=false",
        },
    ]
    appeared = [
        gate["required_path"]
        for gate in gates
        if (ROOT / gate["required_path"]).exists()
    ]
    if appeared:
        raise AssertionError(
            "a v2 completion witness appeared and must receive its own verifier/version: "
            + ", ".join(appeared)
        )
    result = {
        "schema": "t73_complete_geometry_bundle_manifest/v2",
        "bundle_version": 2,
        "bundle_status": "OPEN",
        "artifacts": entries,
        "t73_completion_gates": gates,
        "verified_counts": {
            "source_endpoints": source["total_boundary_endpoint_count"],
            "source_intervals": source["exterior_interval_count"],
            "source_ruled_ribbon_triangles": sum(
                len(item["ruled_ribbon_triangles"])
                for item in source["exterior_intervals"]
            ),
            "coend_wrong_side_intervals": data["defect_coend_typing"]["counts"][
                "wrong_side_intervals"
            ],
            "coend_oriented_band_obligations": data["defect_coend_typing"][
                "counts"
            ]["oriented_reconnection_obligations"],
            "tetgen_prefix_ribbons": data["tetgen_source_prefix10"][
                "verification"
            ]["ribbons"],
            "pd_fixture_core_components": data["pd_open_source_receipt"][
                "spherogram_components"
            ],
            "gmsh_probe_ribbons": data["gmsh_source_prefix20_receipt"][
                "route_prefix"
            ],
            "gmsh_frame_ribbons": data["gmsh_source_prefix10_frame"][
                "verification"
            ]["ribbons"],
        },
        "policy": {
            "fixture_or_prefix_is_not_t73_completion": True,
            "typing_is_not_chain_equivalence": True,
            "all_completion_gates_must_pass_before_bundle_completion": True,
        },
    }
    result["manifest_payload_sha256"] = canonical_sha(result)
    return result


def validate(stored: dict[str, Any]) -> None:
    rebuilt = build()
    if stored != rebuilt:
        raise AssertionError("stored v2 geometry bundle differs from live reconstruction")
    if stored["bundle_status"] != "OPEN":
        raise AssertionError("v2 bundle overclaims completion")
    if any(item["t73_completion_status"] != "OPEN" for item in stored["artifacts"]):
        raise AssertionError("fixture/prefix was promoted to T73 completion")
    if any(item["status"] != "OPEN" for item in stored["t73_completion_gates"]):
        raise AssertionError("an absent completion witness was promoted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        validate(json.loads(OUTPUT.read_text(encoding="utf-8")))
    print("T73_COMPLETE_GEOMETRY_BUNDLE_V2=VERIFIED")
    print(f"BUNDLE_STATUS={result['bundle_status']}")
    print(f"GATES={len(result['t73_completion_gates'])}")
    print(f"SHA256={result['manifest_payload_sha256']}")


if __name__ == "__main__":
    main()
