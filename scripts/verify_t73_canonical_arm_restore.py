#!/usr/bin/env python3
"""Fail-closed verifier for a canonical Johnson ArmRestore PL map.

The legacy restore assembly records layer names and semantic PASS booleans but
does not contain the common triangulations required here.  Consequently the
default command reports OPEN.  An admissible v1 witness must give one global
vertex map on a tetrahedral triangulation for every layer.  Exact arithmetic
then checks the conditions needed for a fixed-boundary PL homeomorphism.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "audit" / "t73_canonical_arm_restore_schema.json"
DEFAULT_INPUT = ROOT / "geometry" / "t73_johnson_restore_assembly.json"
PAIRED_SUPPORT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"
CAP_ASSEMBLY = ROOT / "geometry" / "t73_johnson_cap_collapse_assembly.json"
OUTER_COLLAR = ROOT / "geometry" / "t73_johnson_outer_curve_collar.json"


class WitnessError(ValueError):
    pass


def fail(message: str) -> None:
    raise WitnessError(message)


def q(value: Any) -> Fraction:
    if isinstance(value, bool):
        fail("boolean is not a rational coordinate")
    try:
        return Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise WitnessError(f"invalid rational coordinate {value!r}") from exc


def points(raw: Any, where: str) -> list[tuple[Fraction, Fraction, Fraction]]:
    if not isinstance(raw, list) or len(raw) < 4:
        fail(f"{where} must contain at least four points")
    result = []
    for index, item in enumerate(raw):
        if not isinstance(item, list) or len(item) != 3:
            fail(f"{where}[{index}] is not a three-coordinate point")
        result.append(tuple(q(value) for value in item))
    return result


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def det3(a, b, c) -> Fraction:
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def tet_det(vertices, tet) -> Fraction:
    a, b, c, d = (vertices[index] for index in tet)
    return det3(sub(b, a), sub(c, a), sub(d, a))


def faces(tet: tuple[int, int, int, int]) -> list[tuple[int, int, int]]:
    return [tuple(sorted(tet[:i] + tet[i + 1 :])) for i in range(4)]


def dot(normal, point) -> Fraction:
    return sum(a * b for a, b in zip(normal, point))


def side_of_face(vertices, face, point_index) -> Fraction:
    a, b, c = (vertices[index] for index in face)
    p = vertices[point_index]
    ab, ac, ap = sub(b, a), sub(c, a), sub(p, a)
    normal = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    return dot(normal, ap)


def parse_tets(raw: Any, count: int, where: str) -> list[tuple[int, int, int, int]]:
    if not isinstance(raw, list) or not raw:
        fail(f"{where} must be a nonempty list")
    result = []
    for index, item in enumerate(raw):
        if (
            not isinstance(item, list)
            or len(item) != 4
            or not all(isinstance(v, int) and not isinstance(v, bool) for v in item)
            or len(set(item)) != 4
            or any(v < 0 or v >= count for v in item)
        ):
            fail(f"{where}[{index}] is not a valid tetrahedron")
        result.append(tuple(item))
    if len({tuple(sorted(tet)) for tet in result}) != len(result):
        fail(f"{where} contains duplicate tetrahedra")
    return result


def chart_data(raw: Any):
    if not isinstance(raw, dict) or set(raw) < {"lower", "upper"}:
        fail("layer.chart must contain lower and upper")
    lower = points([raw["lower"], raw["upper"], raw["lower"], raw["upper"]], "chart")[:2]
    lo, hi = lower
    if any(a >= b for a, b in zip(lo, hi)):
        fail("layer.chart is not a positive box")
    return lo, hi


def on_box_boundary(point, lo, hi) -> bool:
    return any(value == lo[i] or value == hi[i] for i, value in enumerate(point))


def bbox_meets_cube(vertices, tet, center, half_width) -> bool:
    for axis in range(3):
        values = [vertices[index][axis] for index in tet]
        if max(values) < center[axis] - half_width or min(values) > center[axis] + half_width:
            return False
    return True


def validate_separators(layer, source, target, tets) -> None:
    provided: dict[tuple[int, int], dict[str, Any]] = {}
    raw = layer.get("pair_separators")
    if not isinstance(raw, list):
        fail("pair_separators must be a list")
    for item in raw:
        if not isinstance(item, dict) or set(item) < {"left", "right", "source", "target"}:
            fail("invalid pair separator")
        pair = tuple(sorted((item["left"], item["right"])))
        if pair[0] == pair[1] or pair[0] < 0 or pair[1] >= len(tets) or pair in provided:
            fail("invalid or duplicate separator pair")
        provided[pair] = item

    for left in range(len(tets)):
        for right in range(left + 1, len(tets)):
            common = set(tets[left]) & set(tets[right])
            if len(common) == 3:
                face = tuple(common)
                extra_left = next(v for v in tets[left] if v not in common)
                extra_right = next(v for v in tets[right] if v not in common)
                for vertices, label in ((source, "source"), (target, "target")):
                    sides = (
                        side_of_face(vertices, face, extra_left),
                        side_of_face(vertices, face, extra_right),
                    )
                    if sides[0] * sides[1] >= 0:
                        fail(f"adjacent tetrahedra overlap on the {label} side")
                continue
            item = provided.get((left, right))
            if item is None:
                fail(f"missing strict separator for tetrahedra {left},{right}")
            for vertices, label in ((source, "source"), (target, "target")):
                cert = item[label]
                if not isinstance(cert, dict) or set(cert) < {"normal", "offset", "margin"}:
                    fail("separator certificate is incomplete")
                normal = points([cert["normal"]] * 4, "separator.normal")[0]
                offset, margin = q(cert["offset"]), q(cert["margin"])
                if margin <= 0:
                    fail("separator margin is not positive")
                common_values = [dot(normal, vertices[v]) for v in common]
                if any(value != offset for value in common_values):
                    fail(f"separator does not contain the common {label} face")
                left_values = [dot(normal, vertices[v]) for v in tets[left] if v not in common]
                right_values = [dot(normal, vertices[v]) for v in tets[right] if v not in common]
                forward = max(left_values) <= offset - margin and min(right_values) >= offset + margin
                reverse = max(right_values) <= offset - margin and min(left_values) >= offset + margin
                if not (forward or reverse):
                    fail(f"separator does not separate the {label} tetrahedra")


def validate_layer(layer: dict[str, Any], previous_hash: str | None) -> str:
    required = {
        "id", "input_state_sha256", "output_state_sha256", "chart",
        "source_vertices", "target_vertices", "tetrahedra", "pair_separators",
        "fixed_boundary_vertices", "source_owner_by_tetrahedron",
        "target_owner_by_tetrahedron", "protected_cube",
    }
    if not isinstance(layer, dict) or set(layer) < required:
        fail(f"layer is missing fields {sorted(required - set(layer or {}))}")
    if previous_hash is not None and layer["input_state_sha256"] != previous_hash:
        fail("successive layer state hashes do not chain")
    source = points(layer["source_vertices"], "source_vertices")
    target = points(layer["target_vertices"], "target_vertices")
    if len(source) != len(target):
        fail("source and target vertex lists have different sizes")
    tets = parse_tets(layer["tetrahedra"], len(source), "tetrahedra")
    lo, hi = chart_data(layer["chart"])
    for label, vertices in (("source", source), ("target", target)):
        if any(any(p[i] < lo[i] or p[i] > hi[i] for i in range(3)) for p in vertices):
            fail(f"{label} vertex lies outside the chart")
    determinants = []
    for index, tet in enumerate(tets):
        ds, dt = tet_det(source, tet), tet_det(target, tet)
        if ds == 0 or dt == 0 or ds * dt <= 0:
            fail(f"tetrahedron {index} is degenerate or orientation reversing")
        determinants.append((ds, dt))
    face_counts = Counter(face for tet in tets for face in faces(tet))
    if set(face_counts.values()) - {1, 2}:
        fail("tetrahedral complex has a face of multiplicity other than one or two")
    boundary_vertices = {v for face, count in face_counts.items() if count == 1 for v in face}
    fixed = layer["fixed_boundary_vertices"]
    if not isinstance(fixed, list) or set(fixed) != boundary_vertices:
        fail("fixed_boundary_vertices must equal the complete triangulated boundary")
    if any(source[v] != target[v] for v in boundary_vertices):
        fail("the PL map is not pointwise fixed on the chart boundary")
    if any(not on_box_boundary(source[v], lo, hi) for v in boundary_vertices):
        fail("a triangulated boundary vertex is not on the chart boundary")
    chart_six_volume = 6 * (hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2])
    if sum(abs(ds) for ds, _ in determinants) != chart_six_volume:
        fail("source tetrahedra do not have the volume of the complete chart")
    if sum(abs(dt) for _, dt in determinants) != chart_six_volume:
        fail("target tetrahedra do not have the volume of the complete chart")
    validate_separators(layer, source, target, tets)
    source_owners = layer["source_owner_by_tetrahedron"]
    target_owners = layer["target_owner_by_tetrahedron"]
    if (
        not isinstance(source_owners, list)
        or not isinstance(target_owners, list)
        or len(source_owners) != len(tets)
        or len(target_owners) != len(tets)
        or any(owner not in (0, 1) for owner in source_owners + target_owners)
        or source_owners != target_owners
    ):
        fail("owner labels do not prove setwise preservation")
    cube = layer["protected_cube"]
    if not isinstance(cube, dict) or set(cube) < {"center", "half_width"}:
        fail("protected_cube is incomplete")
    center = points([cube["center"]] * 4, "protected_cube.center")[0]
    half_width = q(cube["half_width"])
    if half_width <= 0:
        fail("protected_cube half_width is not positive")
    for tet in tets:
        if bbox_meets_cube(source, tet, center, half_width) and any(source[v] != target[v] for v in tet):
            fail("a moving tetrahedron has a bounding box meeting the protected cube")
    return layer["output_state_sha256"]


def verify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not SCHEMA.is_file():
        fail("canonical ArmRestore schema is missing")
    if payload.get("schema") != "t73_canonical_arm_restore_map/v1":
        if payload.get("schema") == "t73_johnson_restore_assembly/v1":
            support = json.loads(PAIRED_SUPPORT.read_text(encoding="utf-8"))
            cap = json.loads(CAP_ASSEMBLY.read_text(encoding="utf-8"))
            outer = json.loads(OUTER_COLLAR.read_text(encoding="utf-8"))
            promoted = (
                support.get("paired_saddle_ambient_cells") == "OPEN"
                and cap.get("paired_saddle_ambient_cells") == "OPEN"
                and cap.get("johnson_restore_ambient_cells") == "OPEN"
                and outer.get("final_restore_assembly") == "OPEN"
                and payload.get("paired_saddle_ambient_cells") == "PASS"
                and payload.get("johnson_arm_restore") == "PASS"
            )
            if promoted:
                fail(
                    "legacy assembler promotes upstream OPEN to PASS; first absent "
                    "coordinate datum is a simplicial self-map of the complete "
                    "paired-support boundary sphere carrying source_patch to "
                    "target_patch and agreeing on the cap curves with the recorded "
                    "cap-product transport; without that boundary map there is no "
                    "fixed-boundary ambient extension or evaluable ArmRestore"
                )
        fail("input is not a canonical ArmRestore map witness")
    required = {"canonical_key", "period", "initial_state_sha256", "final_state_sha256", "layers"}
    if set(payload) < required | {"schema"}:
        fail("ArmRestore witness is missing required top-level fields")
    if not isinstance(payload["layers"], list) or not payload["layers"]:
        fail("ArmRestore witness has no layers")
    state = payload["initial_state_sha256"]
    for layer in payload["layers"]:
        state = validate_layer(layer, state)
    if state != payload["final_state_sha256"]:
        fail("final layer state hash does not match final_state_sha256")
    return {
        "schema": "t73_canonical_arm_restore_gate/v1",
        "verdict": "CERTIFIED",
        "layer_count": len(payload["layers"]),
        "canonical_key": payload["canonical_key"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--allow-open", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = verify_payload(payload)
        code = 0
    except (OSError, json.JSONDecodeError, WitnessError) as exc:
        result = {
            "schema": "t73_canonical_arm_restore_gate/v1",
            "verdict": "OPEN",
            "input": str(args.input),
            "reason": str(exc),
        }
        code = 2
    print(json.dumps(result, indent=2, sort_keys=True))
    if code and not args.allow_open:
        raise SystemExit(code)


if __name__ == "__main__":
    main()
