#!/usr/bin/env python3
"""Verify T73 endpoint transport, unresolved-sign absence, and mutation failures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONVENTION = ROOT / "data" / "T73_ENDPOINT_CONVENTION.json"
AUDIT = ROOT / "audit" / "t73_endpoint_transport.json"
ACTUAL_CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"
ACTUAL_BRAID = ROOT / "geometry" / "t73_actual_geometric_braid.json"


def load_builder():
    path = ROOT / "scripts" / "build_t73_endpoint_transport.py"
    spec = importlib.util.spec_from_file_location("build_t73_endpoint_transport", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expect_fail(builder, convention: dict[str, Any], kind: str) -> str:
    mutant = builder.mutate_convention(convention, kind)
    baseline = builder.transport_from_convention(convention)
    try:
        transport = builder.transport_from_convention(mutant)
    except (ValueError, KeyError, TypeError) as exc:
        return f"FAIL:{type(exc).__name__}:{exc}"
    if transport["P_q_entries"] != baseline["P_q_entries"]:
        return "FAIL:P_changed"
    if transport["derived_public_pairing"] != baseline["derived_public_pairing"]:
        return "FAIL:derived_public_pairing_changed"
    raise AssertionError(f"mutation {kind} did not fail")


def verify(*, write: bool = False) -> dict[str, Any]:
    builder = load_builder()
    payloads = builder.write_outputs() if write else {
        "convention": builder.build_convention(),
        "transport": builder.transport_from_convention(builder.build_convention()),
    }
    convention = payloads["convention"]
    transport = payloads["transport"]
    cut = json.loads(ACTUAL_CUT.read_text(encoding="utf-8"))
    braid = json.loads(ACTUAL_BRAID.read_text(encoding="utf-8"))
    if convention["actual_cut_tangle_sha256"] != cut["sha256"]:
        raise AssertionError("endpoint convention is not bound to the actual detector")
    if convention["actual_geometric_braid_sha256"] != braid["witness_sha256"]:
        raise AssertionError("endpoint convention is not bound to the actual braid")
    if not convention["physical_endpoints_precede_public_table_lookup"]:
        raise AssertionError("public endpoint coordinates were treated as physical input")
    if convention["dimension"] != 88 or len(convention["endpoints"]) != 88:
        raise AssertionError("convention does not record all 88 endpoints")
    required = {
        "physical_endpoint_id",
        "owner",
        "orientation",
        "geometric_order",
        "public_order",
        "pivotal_coefficient",
        "weight_defect_basis_vector",
        "actual_side_source_id",
        "coordinate_in_detector_chart",
        "public_endpoint_id",
    }
    geometric = [None] * 88
    public = [None] * 88
    for endpoint in convention["endpoints"]:
        missing = required.difference(endpoint)
        if missing:
            raise AssertionError(f"endpoint missing {sorted(missing)}")
        if endpoint["pivotal_coefficient"]["sign"] not in (-1, 1):
            raise AssertionError("unresolved pivotal sign")
        if not endpoint["physical_endpoint_id"].startswith("actual:"):
            raise AssertionError("physical endpoint identity came from the public table")
        geo = endpoint["geometric_order"]
        pub = endpoint["public_order"]
        if geometric[geo] is not None or public[pub] is not None:
            raise AssertionError("geometric or public order is not bijective")
        geometric[geo] = endpoint["physical_endpoint_id"]
        public[pub] = endpoint["physical_endpoint_id"]
        if endpoint["weight_defect_basis_vector"][geo] != 1:
            raise AssertionError("weight-defect basis vector is not e_geometric")

    pairing = transport["derived_public_pairing"]
    derived_u = pairing["u_terms"]
    derived_ell = pairing["ell_terms"]
    # Derived, not hardcoded as an input.  The frozen public basis is this
    # pairing; comparing after derivation checks the convention, and D3 uses
    # only the derived terms.
    if {tuple(term) for term in derived_u} != {(2, 1), (87, -1)}:
        raise AssertionError(f"derived u_public is {derived_u}, not e2-e87")
    if {tuple(term) for term in derived_ell} != {(87, 1), (2, -1)}:
        raise AssertionError(f"derived ell_public is {derived_ell}, not e87*-e2*")

    mutations = {
        "pivotal_sign": expect_fail(builder, convention, "pivotal_sign"),
        "unresolved_sign": expect_fail(builder, convention, "unresolved_sign"),
        "geometric_swap": expect_fail(builder, convention, "geometric_swap"),
        "orientation": expect_fail(builder, convention, "orientation"),
    }
    if CONVENTION.is_file():
        committed = json.loads(CONVENTION.read_text(encoding="utf-8"))
        if builder.canonical_sha(committed) != transport["convention_sha256"] and write is False:
            # Rebuilt convention must match the committed bytes when not writing.
            rebuilt_sha = builder.canonical_sha(convention)
            committed_sha = builder.canonical_sha(committed)
            if rebuilt_sha != committed_sha:
                raise AssertionError("committed convention does not rebuild")
    result = {
        "ENDPOINT_TRANSPORT": "PASS",
        "NO_UNRESOLVED_SIGNS": "PASS",
        "ACTUAL_ENDPOINT_BINDING": "PASS",
        "ACTUAL_CUT_SHA256": cut["sha256"],
        "ACTUAL_BRAID_SHA256": braid["witness_sha256"],
        "derived_u_terms": derived_u,
        "derived_ell_terms": derived_ell,
        "failing_mutation_tests": mutations,
        "checks": transport["checks"],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify(write=args.write)
    if args.check and CONVENTION.is_file() and AUDIT.is_file():
        builder = load_builder()
        committed_convention = json.loads(CONVENTION.read_text(encoding="utf-8"))
        committed_audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        rebuilt = builder.build_convention()
        rebuilt_audit = builder.transport_from_convention(rebuilt)
        if builder.canonical_sha(committed_convention) != builder.canonical_sha(rebuilt):
            raise AssertionError("committed T73_ENDPOINT_CONVENTION.json is stale")
        if builder.canonical_sha(committed_audit) != builder.canonical_sha(rebuilt_audit):
            raise AssertionError("committed t73_endpoint_transport.json is stale")
    print(f"ENDPOINT_TRANSPORT={result['ENDPOINT_TRANSPORT']}")
    print(f"NO_UNRESOLVED_SIGNS={result['NO_UNRESOLVED_SIGNS']}")
    print("U_PUBLIC_TERMS=" + json.dumps(result["derived_u_terms"], separators=(",", ":")))
    print("ELL_PUBLIC_TERMS=" + json.dumps(result["derived_ell_terms"], separators=(",", ":")))
    for name, status in result["failing_mutation_tests"].items():
        print(f"MUTATION_{name.upper()}={status.split(':', 1)[0]}")


if __name__ == "__main__":
    main()
