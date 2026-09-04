#!/usr/bin/env python3
"""Build and inventory the complete selected-C geometry bundle.

This is deliberately a fail-closed orchestrator.  It distinguishes exact
reconstruction of a committed JSON artifact from completion of the
mathematical source-to-target proof.  In particular, reconstructing a target
template can never change an OPEN proof obligation into VERIFIED.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_complete_geometry_bundle_manifest.v1.json"
SCHEMA = ROOT / "data" / "T73_COMPLETE_GEOMETRY_BUNDLE_MANIFEST.schema.json"

ARTIFACTS = (
    {
        "id": "selected_source_exterior",
        "path": "geometry/t73_selected_source_exterior.json",
        "schema": "t73_selected_source_exterior/v1",
        "generator": "scripts/build_t73_selected_source_exterior.py",
        "verifier": "scripts/verify_t73_selected_source_exterior.py",
    },
    {
        "id": "selected_canopolis_target_v2",
        "path": "geometry/t73_selected_canopolis_normal_form.json",
        "schema": "t73_selected_canopolis_normal_form/v2",
        "generator": "scripts/build_t73_selected_canopolis_normal_form.py",
        "verifier": "scripts/verify_t73_selected_canopolis_normal_form.py",
    },
    {
        "id": "single_hom_defect_target",
        "path": "geometry/t73_single_hom_defect_target.json",
        "schema": "t73_single_hom_defect_target/v1",
        "generator": "scripts/build_t73_single_hom_defect_target.py",
        "verifier": "scripts/verify_t73_single_hom_defect_target.py",
    },
    {
        "id": "defect_aware_currying_audit",
        "path": "audit/t73_defect_aware_currying.json",
        "schema": "t73_defect_aware_currying_audit/v1",
        "generator": "scripts/audit_t73_defect_aware_currying.py",
        "verifier": "scripts/audit_t73_defect_aware_currying.py --check",
    },
)


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def bytes_sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def load_module(relative_path: str, stem: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def load_artifacts() -> dict[str, dict[str, Any]]:
    return {
        spec["id"]: json.loads((ROOT / spec["path"]).read_text(encoding="utf-8"))
        for spec in ARTIFACTS
    }


def reconstruct_artifacts(write: bool = False) -> dict[str, dict[str, Any]]:
    """Run the four lower-level constructors in dependency order."""
    built: dict[str, dict[str, Any]] = {}
    for spec in ARTIFACTS:
        module = load_module(spec["generator"], f"t73_bundle_{spec['id']}")
        value = module.build()
        if value.get("schema") != spec["schema"]:
            raise AssertionError(
                f"{spec['id']} produced {value.get('schema')!r}, expected {spec['schema']!r}"
            )
        built[spec["id"]] = value
        if write:
            write_json(ROOT / spec["path"], value)
    return built


def geometry_counts(artifact_id: str, data: dict[str, Any]) -> dict[str, Any]:
    if artifact_id == "selected_source_exterior":
        return {
            "cable_component_cycles": len(data["cycles"]),
            "cyclic_seams": data["cyclic_seam_count"],
            "endpoints_per_insertion_sphere": data["endpoint_counts_per_sphere"],
            "exterior_intervals": data["exterior_interval_count"],
            "total_boundary_endpoints": data["total_boundary_endpoint_count"],
        }
    if artifact_id == "selected_canopolis_target_v2":
        return {
            "active_yz_arcs_per_closure": data["active_corridor_count_per_closure"],
            "closure_balls": len(data["closure_balls"]),
            "endpoints_per_insertion_ball": data["endpoint_counts_per_insertion_ball"],
            "residual_zz_arcs_per_closure": data["added_z_arc_count_per_closure"],
            "target_arcs": data["target_strand_count"],
            "target_primitives": data["primitive_count"],
            "total_boundary_endpoints": data["total_boundary_endpoint_count"],
        }
    if artifact_id == "single_hom_defect_target":
        return {
            "bottom_endpoints": data["bottom_endpoint_count"],
            "cups": data["cup_count"],
            "source_exterior_intervals": data["source_exterior_interval_count"],
            "source_to_target_interval_map_entries": len(
                data["source_to_target_interval_map"]
            ),
            "target_cells": len(data["cells"]),
            "through_strands": data["through_strand_count"],
            "top_endpoints": data["top_endpoint_count"],
            "z_coend_gluing_cells": len(data["z_coend_gluing_cells"]),
        }
    if artifact_id == "defect_aware_currying_audit":
        return {
            "active_intervals": data["active_interval_count"],
            "correct_side_intervals": data["correct_side_count"],
            "minimum_independent_reconnections": data[
                "minimum_independent_reconnections"
            ],
            "p86_to_p88_boundary_endpoints": data["P86_to_P88_boundary_endpoints"],
            "wrong_side_intervals": data["wrong_side_count"],
        }
    raise AssertionError(f"unknown artifact {artifact_id}")


def open_obligations(artifact_id: str, data: dict[str, Any]) -> list[str]:
    """Return proof obligations; an empty list would require new certificate logic."""
    if artifact_id == "selected_source_exterior":
        return [
            "actual AR coefficient exterior to the saved canonical representative: relative ambient isotopy",
            "full framed-link/handlebody input suitable for an independent complement computation",
        ]
    if artifact_id == "selected_canopolis_target_v2":
        return [
            "relative source isotopy is explicitly not claimed",
            "eight wrong-side source connectors obstruct the literal split-target interpretation",
        ]
    if artifact_id == "single_hom_defect_target":
        return [
            data["first_missing_map"],
            "Euler characteristic and quantum shift of the missing gluing cobordism",
        ]
    if artifact_id == "defect_aware_currying_audit":
        return [
            "choose and verify all pivotal mates, Blanchet signs, and Euler degrees",
            "derive the P86-to-P88 single defect from the saved 630-interval source incidence",
        ]
    raise AssertionError(f"unknown artifact {artifact_id}")


def verify_artifacts(
    artifacts: dict[str, dict[str, Any]], check_pairwise: bool = True
) -> dict[str, dict[str, str]]:
    """Run exact semantic verifiers without conflating them with proof completion."""
    results: dict[str, dict[str, str]] = {}

    def run(
        artifact_id: str,
        verifier: Callable[[], None],
        requires_pairwise: bool = False,
    ) -> None:
        try:
            verifier()
        except Exception as exc:  # fail closed and preserve a machine-readable manifest
            results[artifact_id] = {
                "reconstruction_status": "OPEN",
                "diagnostic": f"{type(exc).__name__}: {exc}",
            }
        else:
            status = "VERIFIED"
            diagnostic = "exact semantic verifier accepted the reconstructed artifact"
            if requires_pairwise and not check_pairwise:
                status = "OPEN"
                diagnostic = "pairwise PL-disjointness verification was explicitly skipped"
            results[artifact_id] = {
                "reconstruction_status": status,
                "diagnostic": diagnostic,
            }

    primitives = json.loads(
        (ROOT / "geometry" / "t73_all_owner_product_primitives.json").read_text(
            encoding="utf-8"
        )
    )
    source_verifier = load_module(
        "scripts/verify_t73_selected_source_exterior.py", "t73_bundle_verify_source"
    )
    run(
        "selected_source_exterior",
        lambda: source_verifier.validate(
            artifacts["selected_source_exterior"],
            primitives,
            check_route_pairs=check_pairwise,
        ),
        requires_pairwise=True,
    )

    target_verifier = load_module(
        "scripts/verify_t73_selected_canopolis_normal_form.py",
        "t73_bundle_verify_target",
    )
    run(
        "selected_canopolis_target_v2",
        lambda: target_verifier.validate(
            artifacts["selected_canopolis_target_v2"],
            primitives,
            check_pairwise=check_pairwise,
        ),
        requires_pairwise=True,
    )

    def verify_single_hom() -> None:
        value = artifacts["single_hom_defect_target"]
        if value["morphism_type"] != {"source": "P86", "target": "P88"}:
            raise AssertionError("single-Hom target type changed")
        if (
            value["bottom_endpoint_count"],
            value["top_endpoint_count"],
            value["through_strand_count"],
            value["cup_count"],
        ) != (86, 88, 86, 1):
            raise AssertionError("single-Hom endpoint or cell counts changed")
        if value["source_exterior_sha256"] != artifacts[
            "selected_source_exterior"
        ]["sha256"]:
            raise AssertionError("single-Hom target is stale relative to source exterior")
        if value["source_to_target_status"] != "OPEN":
            raise AssertionError("unproved single-Hom map was promoted")
        if value["source_to_target_interval_map"] or value["z_coend_gluing_cells"]:
            raise AssertionError("uncertified source/gluing cells were inserted")

    run("single_hom_defect_target", verify_single_hom)

    def verify_defect_audit() -> None:
        value = artifacts["defect_aware_currying_audit"]
        if value["source_exterior_sha256"] != artifacts[
            "selected_source_exterior"
        ]["sha256"]:
            raise AssertionError("defect audit is stale relative to source exterior")
        if (
            value["active_interval_count"],
            value["correct_side_count"],
            value["wrong_side_count"],
            value["minimum_independent_reconnections"],
        ) != (176, 168, 8, 4):
            raise AssertionError("defect incidence classification changed")
        if value["verdict"] != "NO_SINGLE_DEFECT_CURRYING_FROM_CURRENT_INCIDENCE":
            raise AssertionError("defect audit overclaims the current incidence")

    run("defect_aware_currying_audit", verify_defect_audit)
    return results


def build_manifest(
    artifacts: dict[str, dict[str, Any]],
    verification: dict[str, dict[str, str]],
) -> dict[str, Any]:
    entries = []
    for spec in ARTIFACTS:
        artifact_id = spec["id"]
        data = artifacts[artifact_id]
        raw = json_bytes(data)
        obligations = open_obligations(artifact_id, data)
        reconstruction = verification[artifact_id]["reconstruction_status"]
        # Version 1 has no proof-certificate field.  Nonempty obligations are
        # therefore always OPEN, even when reconstruction itself is VERIFIED.
        completion = "OPEN"
        entry = {
            "id": artifact_id,
            "path": spec["path"],
            "schema": data["schema"],
            "generator": spec["generator"],
            "verifier": spec["verifier"],
            "content_sha256": bytes_sha(raw),
            "content_bytes": len(raw),
            "embedded_payload_sha256": data.get("sha256"),
            "geometry_counts": geometry_counts(artifact_id, data),
            "reconstruction_status": reconstruction,
            "completion_status": completion,
            "status": "OPEN" if completion == "OPEN" else reconstruction,
            "verification_diagnostic": verification[artifact_id]["diagnostic"],
            "open_obligations": obligations,
        }
        entries.append(entry)

    source = artifacts["selected_source_exterior"]
    single = artifacts["single_hom_defect_target"]
    defect = artifacts["defect_aware_currying_audit"]
    dependencies = [
        {
            "from": "selected_source_exterior",
            "to": "single_hom_defect_target",
            "kind": "embedded source payload SHA256",
            "status": (
                "VERIFIED"
                if single["source_exterior_sha256"] == source["sha256"]
                else "OPEN"
            ),
        },
        {
            "from": "selected_source_exterior",
            "to": "defect_aware_currying_audit",
            "kind": "embedded source payload SHA256",
            "status": (
                "VERIFIED"
                if defect["source_exterior_sha256"] == source["sha256"]
                else "OPEN"
            ),
        },
        {
            "from": "selected_source_exterior",
            "to": "selected_canopolis_target_v2",
            "kind": "relative ambient isotopy / defect-aware replacement",
            "status": "OPEN",
        },
        {
            "from": "selected_source_exterior",
            "to": "single_hom_defect_target",
            "kind": "coend gluing and pivotal currying",
            "status": "OPEN",
        },
    ]
    result = {
        "schema": "t73_complete_geometry_bundle_manifest/v1",
        "schema_file": str(SCHEMA.relative_to(ROOT)),
        "bundle_version": 1,
        "bundle_status": "OPEN",
        "policy": {
            "allowed_status_values": ["VERIFIED", "OPEN"],
            "fail_closed": True,
            "reconstruction_is_not_proof_completion": True,
            "open_cannot_be_promoted_without_new_checked_certificate_fields": True,
        },
        "artifacts": entries,
        "dependency_edges": dependencies,
        "closed_facts": {
            "saved_boundary_endpoint_count": 1260,
            "saved_source_exterior_interval_count": 630,
            "target_template_arc_count": 630,
            "wrong_side_active_interval_count": 8,
        },
        "first_open_gate": (
            "construct and verify a relative source-to-target cobordism/currying map "
            "from all 630 saved source intervals, including the eight wrong-side intervals"
        ),
    }
    result["manifest_payload_sha256"] = canonical_sha(result)
    return result


def validate_manifest(
    manifest: dict[str, Any], artifacts: dict[str, dict[str, Any]] | None = None
) -> None:
    if manifest["schema"] != "t73_complete_geometry_bundle_manifest/v1":
        raise AssertionError("unexpected bundle manifest schema")
    if manifest["bundle_version"] != 1 or manifest["bundle_status"] != "OPEN":
        raise AssertionError("version-1 bundle must remain OPEN")
    expected_policy = {
        "allowed_status_values": ["VERIFIED", "OPEN"],
        "fail_closed": True,
        "reconstruction_is_not_proof_completion": True,
        "open_cannot_be_promoted_without_new_checked_certificate_fields": True,
    }
    if manifest["schema_file"] != str(SCHEMA.relative_to(ROOT)):
        raise AssertionError("bundle manifest schema path changed")
    if manifest["policy"] != expected_policy:
        raise AssertionError("bundle fail-closed policy changed")
    payload = {key: value for key, value in manifest.items() if key != "manifest_payload_sha256"}
    if manifest["manifest_payload_sha256"] != canonical_sha(payload):
        raise AssertionError("bundle manifest payload SHA256 mismatch")
    if artifacts is None:
        artifacts = load_artifacts()
    specs = {spec["id"]: spec for spec in ARTIFACTS}
    entries = {entry["id"]: entry for entry in manifest["artifacts"]}
    if set(entries) != set(specs) or len(entries) != len(manifest["artifacts"]):
        raise AssertionError("bundle manifest does not inventory exactly four artifacts")
    for artifact_id, spec in specs.items():
        entry, data = entries[artifact_id], artifacts[artifact_id]
        raw_path = ROOT / spec["path"]
        raw = raw_path.read_bytes()
        if entry["path"] != spec["path"] or entry["schema"] != spec["schema"]:
            raise AssertionError(f"{artifact_id} path or schema changed")
        if json.loads(raw) != data or raw != json_bytes(data):
            raise AssertionError(f"{artifact_id} is not canonical deterministic JSON")
        if entry["content_sha256"] != bytes_sha(raw) or entry["content_bytes"] != len(raw):
            raise AssertionError(f"{artifact_id} content digest or byte count mismatch")
        if data.get("sha256") is not None:
            embedded_payload = {
                key: value for key, value in data.items() if key != "sha256"
            }
            if data["sha256"] != canonical_sha(embedded_payload):
                raise AssertionError(f"{artifact_id} embedded payload SHA256 mismatch")
            if entry["embedded_payload_sha256"] != data["sha256"]:
                raise AssertionError(f"{artifact_id} embedded SHA inventory mismatch")
        if entry["geometry_counts"] != geometry_counts(artifact_id, data):
            raise AssertionError(f"{artifact_id} geometry counts are stale")
        if entry["reconstruction_status"] not in {"VERIFIED", "OPEN"}:
            raise AssertionError(f"{artifact_id} has an invalid reconstruction status")
        if not entry["open_obligations"]:
            raise AssertionError(f"{artifact_id} silently discarded its open obligations")
        if entry["completion_status"] != "OPEN" or entry["status"] != "OPEN":
            raise AssertionError(f"{artifact_id} improperly promotes an open proof claim")
    if any(
        edge["status"] not in {"VERIFIED", "OPEN"}
        for edge in manifest["dependency_edges"]
    ):
        raise AssertionError("dependency edge used a non fail-closed status")
    source = artifacts["selected_source_exterior"]
    single = artifacts["single_hom_defect_target"]
    defect = artifacts["defect_aware_currying_audit"]
    expected_edges = [
        {
            "from": "selected_source_exterior",
            "to": "single_hom_defect_target",
            "kind": "embedded source payload SHA256",
            "status": (
                "VERIFIED"
                if single["source_exterior_sha256"] == source["sha256"]
                else "OPEN"
            ),
        },
        {
            "from": "selected_source_exterior",
            "to": "defect_aware_currying_audit",
            "kind": "embedded source payload SHA256",
            "status": (
                "VERIFIED"
                if defect["source_exterior_sha256"] == source["sha256"]
                else "OPEN"
            ),
        },
        {
            "from": "selected_source_exterior",
            "to": "selected_canopolis_target_v2",
            "kind": "relative ambient isotopy / defect-aware replacement",
            "status": "OPEN",
        },
        {
            "from": "selected_source_exterior",
            "to": "single_hom_defect_target",
            "kind": "coend gluing and pivotal currying",
            "status": "OPEN",
        },
    ]
    if manifest["dependency_edges"] != expected_edges:
        raise AssertionError("bundle dependency edges or their gates changed")
    expected_closed_facts = {
        "saved_boundary_endpoint_count": source["total_boundary_endpoint_count"],
        "saved_source_exterior_interval_count": source["exterior_interval_count"],
        "target_template_arc_count": artifacts["selected_canopolis_target_v2"][
            "target_strand_count"
        ],
        "wrong_side_active_interval_count": defect["wrong_side_count"],
    }
    if manifest["closed_facts"] != expected_closed_facts:
        raise AssertionError("bundle closed-fact counts are stale")
    expected_gate = (
        "construct and verify a relative source-to-target cobordism/currying map "
        "from all 630 saved source intervals, including the eight wrong-side intervals"
    )
    if manifest["first_open_gate"] != expected_gate:
        raise AssertionError("bundle first open gate changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--write", action="store_true", help="rebuild and save all artifacts and manifest"
    )
    mode.add_argument(
        "--check", action="store_true", help="rebuild everything and compare committed bytes"
    )
    mode.add_argument(
        "--check-files",
        action="store_true",
        help="quickly verify the committed manifest, hashes, counts, and fail-closed gates",
    )
    parser.add_argument(
        "--skip-pairwise",
        action="store_true",
        help="skip expensive pairwise PL-disjointness checks (never changes completion OPEN)",
    )
    args = parser.parse_args()

    if args.check_files or not (args.write or args.check):
        manifest = json.loads(OUTPUT.read_text(encoding="utf-8"))
        validate_manifest(manifest)
        print("T73_COMPLETE_GEOMETRY_BUNDLE=FILES_VERIFIED")
        print(f"BUNDLE_STATUS={manifest['bundle_status']}")
        print(f"MANIFEST_SHA256={manifest['manifest_payload_sha256']}")
        return

    built = reconstruct_artifacts(write=args.write)
    verification = verify_artifacts(built, check_pairwise=not args.skip_pairwise)
    manifest = build_manifest(built, verification)
    validate_manifest(manifest, built)
    if args.write:
        write_json(OUTPUT, manifest)
        print(f"WROTE={OUTPUT}")
    else:
        for spec in ARTIFACTS:
            if (ROOT / spec["path"]).read_bytes() != json_bytes(built[spec["id"]]):
                raise AssertionError(f"committed {spec['path']} differs from reconstruction")
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != manifest:
            raise AssertionError("committed geometry bundle manifest differs from reconstruction")
    print("T73_COMPLETE_GEOMETRY_BUNDLE=RECONSTRUCTED")
    for entry in manifest["artifacts"]:
        print(
            f"{entry['id']}={entry['reconstruction_status']}/{entry['completion_status']}"
        )
    print(f"BUNDLE_STATUS={manifest['bundle_status']}")
    print(f"MANIFEST_SHA256={manifest['manifest_payload_sha256']}")


if __name__ == "__main__":
    main()
