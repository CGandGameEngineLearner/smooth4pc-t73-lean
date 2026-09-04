#!/usr/bin/env python3
"""Fail-closed gate for the missing G-S1 and G-P3 topology.

The current repository has no admissible witness.  This verifier checks all
finite simplicial predicates for which data are present, and refuses to
promote a status string, a hash binding, or a homeomorphism-type label into a
normal-surgery proof.  A cut-and-cap step is defined by an explicitly embedded
canonical prism neighbourhood S^2 x I.  The verifier reconstructs and removes
that neighbourhood, cones off its two boundary copies, and compares the exact
resulting triangulation.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "audit" / "t73_gs1_gp3_schema.json"
CURRENT_W2 = ROOT / "geometry" / "t73_actual_W2_boundary.json"


class WitnessError(ValueError):
    pass


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def fail(message: str) -> None:
    raise WitnessError(message)


def require_object(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{where} must be an object")
    return value


def require_fields(value: dict[str, Any], fields: list[str], where: str) -> None:
    missing = [field for field in fields if field not in value]
    if missing:
        fail(f"{where} missing required fields: {missing}")


def simplex(raw: Any, size: int, vertex_count: int, where: str) -> tuple[int, ...]:
    if (
        not isinstance(raw, list)
        or len(raw) != size
        or not all(isinstance(item, int) and not isinstance(item, bool) for item in raw)
        or len(set(raw)) != size
        or any(item < 0 or item >= vertex_count for item in raw)
    ):
        fail(f"{where} is not a nondegenerate {size - 1}-simplex")
    return tuple(raw)


def faces(simplex_value: tuple[int, ...]) -> list[tuple[int, ...]]:
    return [
        tuple(sorted(simplex_value[:index] + simplex_value[index + 1 :]))
        for index in range(len(simplex_value))
    ]


def connected_simplices(simplices: list[tuple[int, ...]]) -> bool:
    if not simplices:
        return False
    adjacency = [set() for _ in simplices]
    for left in range(len(simplices)):
        for right in range(left + 1, len(simplices)):
            if len(set(simplices[left]) & set(simplices[right])) == len(simplices[left]) - 1:
                adjacency[left].add(right)
                adjacency[right].add(left)
    seen: set[int] = set()
    stack = [0]
    while stack:
        item = stack.pop()
        if item in seen:
            continue
        seen.add(item)
        stack.extend(adjacency[item] - seen)
    return len(seen) == len(simplices)


def validate_closed_3_complex(value: dict[str, Any], where: str) -> dict[str, Any]:
    require_fields(value, ["vertices", "tetrahedra"], where)
    vertices = value["vertices"]
    if not isinstance(vertices, list) or len(vertices) < 5:
        fail(f"{where}.vertices must be an explicit list of at least five vertices")
    tetrahedra = [
        simplex(raw, 4, len(vertices), f"{where}.tetrahedra[{index}]")
        for index, raw in enumerate(value["tetrahedra"])
    ] if isinstance(value["tetrahedra"], list) else fail(f"{where}.tetrahedra must be a list")
    if len(set(tuple(sorted(tet)) for tet in tetrahedra)) != len(tetrahedra):
        fail(f"{where} contains a duplicate tetrahedron")
    face_counts = Counter(face for tet in tetrahedra for face in faces(tet))
    if not face_counts or set(face_counts.values()) != {2}:
        fail(f"{where} is not a closed face-paired 3-dimensional pseudomanifold")
    if not connected_simplices(tetrahedra):
        fail(f"{where} has disconnected tetrahedron adjacency")
    used_vertices = {vertex for tet in tetrahedra for vertex in tet}
    if used_vertices != set(range(len(vertices))):
        fail(f"{where} has unused vertices")
    for vertex in range(len(vertices)):
        link_triangles = [
            tuple(sorted(item for item in tet if item != vertex))
            for tet in tetrahedra
            if vertex in tet
        ]
        if len(set(link_triangles)) != len(link_triangles):
            fail(f"{where} vertex {vertex} has duplicate triangles in its link")
        link_edges = Counter(
            edge for triangle in link_triangles for edge in faces(triangle)
        )
        link_vertices = {
            item for triangle in link_triangles for item in triangle
        }
        link_chi = len(link_vertices) - len(link_edges) + len(link_triangles)
        if (
            not link_edges
            or set(link_edges.values()) != {2}
            or link_chi != 2
            or not connected_simplices(link_triangles)
        ):
            fail(f"{where} vertex {vertex} does not have a triangulated S2 link")
    return {
        "vertices": vertices,
        "tetrahedra": tetrahedra,
        "face_set": set(face_counts),
        "sha256": canonical_sha({"vertices": vertices, "tetrahedra": value["tetrahedra"]}),
    }


def validate_sphere(
    value: dict[str, Any], ambient: dict[str, Any], where: str
) -> dict[str, Any]:
    require_fields(value, ["name", "triangles"], where)
    if not isinstance(value["name"], str) or not value["name"]:
        fail(f"{where}.name must be nonempty")
    if not isinstance(value["triangles"], list):
        fail(f"{where}.triangles must be a list")
    triangles = [
        simplex(raw, 3, len(ambient["vertices"]), f"{where}.triangles[{index}]")
        for index, raw in enumerate(value["triangles"])
    ]
    canonical = [tuple(sorted(triangle)) for triangle in triangles]
    if len(set(canonical)) != len(canonical):
        fail(f"{where} contains duplicate triangles")
    if any(triangle not in ambient["face_set"] for triangle in canonical):
        fail(f"{where} is not a triangle subcomplex of w2_boundary")
    edge_counts = Counter(edge for triangle in triangles for edge in faces(triangle))
    if not edge_counts or set(edge_counts.values()) != {2}:
        fail(f"{where} is not a closed triangulated surface")
    used_vertices = {vertex for triangle in triangles for vertex in triangle}
    chi = len(used_vertices) - len(edge_counts) + len(triangles)
    if chi != 2 or not connected_simplices(triangles):
        fail(f"{where} is not a connected triangulated 2-sphere")
    return {
        "name": value["name"],
        "triangles": triangles,
        "vertices": used_vertices,
        "sha256": canonical_sha({"name": value["name"], "triangles": value["triangles"]}),
    }


def canonical_prism_tetrahedra(
    sphere: dict[str, Any], parallel: dict[int, int]
) -> list[tuple[int, ...]]:
    """Staircase triangulation of the product of a triangulated S2 with I."""
    product: list[tuple[int, ...]] = []
    for triangle in sphere["triangles"]:
        a, b, c = sorted(triangle)
        ua, ub, uc = parallel[a], parallel[b], parallel[c]
        product.extend(
            [
                tuple(sorted((a, b, c, uc))),
                tuple(sorted((a, b, ub, uc))),
                tuple(sorted((a, ua, ub, uc))),
            ]
        )
    if len(set(product)) != len(product):
        fail(f"normal neighbourhood of {sphere['name']} has duplicate tetrahedra")
    return product


def replay_cut_cap_step(
    current_raw: dict[str, Any],
    sphere: dict[str, Any],
    step: dict[str, Any],
    where: str,
    forbidden_vertices: set[int] | None = None,
) -> dict[str, Any]:
    """Replay surgery on a two-sided S2 with a certified product neighbourhood."""
    require_fields(
        step,
        [
            "sphere_name",
            "parallel_vertex_map",
            "product_tetrahedra",
            "cap_vertices",
            "result",
        ],
        where,
    )
    if step["sphere_name"] != sphere["name"]:
        fail(f"{where}.sphere_name does not match the trace order")
    current = validate_closed_3_complex(current_raw, f"{where}.source")
    pairs = step["parallel_vertex_map"]
    if not isinstance(pairs, list):
        fail(f"{where}.parallel_vertex_map must be a list")
    lower_vertices = sphere["vertices"]
    parallel: dict[int, int] = {}
    for index, raw in enumerate(pairs):
        if (
            not isinstance(raw, list)
            or len(raw) != 2
            or not all(isinstance(vertex, int) for vertex in raw)
        ):
            fail(f"{where}.parallel_vertex_map[{index}] is not [lower, upper]")
        lower, upper = raw
        if (
            lower not in lower_vertices
            or lower in parallel
            or upper < 0
            or upper >= len(current["vertices"])
            or upper in lower_vertices
        ):
            fail(f"{where}.parallel_vertex_map is not a disjoint map on sphere vertices")
        parallel[lower] = upper
    if set(parallel) != lower_vertices or len(set(parallel.values())) != len(parallel):
        fail(f"{where}.parallel_vertex_map is not a bijection to a disjoint copy")

    expected_product = canonical_prism_tetrahedra(sphere, parallel)
    if forbidden_vertices is not None:
        neighbourhood_vertices = {
            vertex for tet in expected_product for vertex in tet
        }
        if neighbourhood_vertices & forbidden_vertices:
            fail(f"{where}.product neighbourhood meets protected data")
    supplied = step["product_tetrahedra"]
    if not isinstance(supplied, list):
        fail(f"{where}.product_tetrahedra must be a list")
    supplied_product = [
        tuple(sorted(simplex(raw, 4, len(current["vertices"]), f"{where}.product_tetrahedra[{index}]")))
        for index, raw in enumerate(supplied)
    ]
    if supplied_product != expected_product:
        fail(f"{where}.product_tetrahedra is not the canonical S2 x I triangulation")
    current_tets = [tuple(sorted(tet)) for tet in current["tetrahedra"]]
    current_set = set(current_tets)
    if not set(expected_product) <= current_set:
        fail(f"{where}.product neighbourhood is not a tetrahedron subcomplex")

    # The boundary of the proposed neighbourhood must be exactly the lower
    # sphere and its parallel upper copy.  This detects missing/extra prism
    # tetrahedra and makes the local replacement a genuine S2 x I cut.
    product_face_counts = Counter(
        face for tet in expected_product for face in faces(tet)
    )
    product_boundary = {
        face for face, count in product_face_counts.items() if count == 1
    }
    if set(product_face_counts.values()) - {1, 2}:
        fail(f"{where}.product neighbourhood has nonmanifold face incidence")
    lower_boundary = {tuple(sorted(triangle)) for triangle in sphere["triangles"]}
    upper_boundary = {
        tuple(sorted(parallel[vertex] for vertex in triangle))
        for triangle in sphere["triangles"]
    }
    if product_boundary != lower_boundary | upper_boundary:
        fail(f"{where}.product neighbourhood boundary is not two copies of the sphere")

    cap_vertices = step["cap_vertices"]
    if not isinstance(cap_vertices, list) or len(cap_vertices) != 2:
        fail(f"{where}.cap_vertices must contain two new vertex records")
    encoded_existing = {
        json.dumps(vertex, sort_keys=True, separators=(",", ":"))
        for vertex in current["vertices"]
    }
    encoded_caps = [
        json.dumps(vertex, sort_keys=True, separators=(",", ":"))
        for vertex in cap_vertices
    ]
    if len(set(encoded_caps)) != 2 or any(item in encoded_existing for item in encoded_caps):
        fail(f"{where}.cap_vertices are not two distinct new vertices")
    lower_cap = len(current["vertices"])
    upper_cap = lower_cap + 1
    retained = [
        list(tet)
        for tet in current_tets
        if tet not in set(expected_product)
    ]
    lower_cones = [
        sorted((*triangle, lower_cap)) for triangle in sphere["triangles"]
    ]
    upper_cones = [
        sorted((*tuple(parallel[vertex] for vertex in triangle), upper_cap))
        for triangle in sphere["triangles"]
    ]
    generated_raw = {
        "vertices": list(current["vertices"]) + cap_vertices,
        "tetrahedra": retained + lower_cones + upper_cones,
    }
    generated = validate_closed_3_complex(generated_raw, f"{where}.generated_result")
    result_raw = require_object(step["result"], f"{where}.result")
    result = validate_closed_3_complex(result_raw, f"{where}.result")
    if generated_raw != {
        "vertices": result_raw["vertices"],
        "tetrahedra": result_raw["tetrahedra"],
    }:
        fail(f"{where}.result does not equal the replayed cut-and-cap complex")
    if generated["sha256"] != result["sha256"]:
        fail(f"{where}.result digest mismatch after replay")
    return generated_raw


def replay_normal_surgery_trace(
    ambient_raw: dict[str, Any],
    ambient: dict[str, Any],
    spheres: list[dict[str, Any]],
    trace: dict[str, Any],
    detector_vertices: set[int],
) -> dict[str, Any]:
    if len(trace["steps"]) != len(spheres):
        fail("normal_surgery_trace must contain one step per attaching sphere")
    current_raw = {
        "vertices": ambient_raw["vertices"],
        "tetrahedra": ambient_raw["tetrahedra"],
    }
    for index, (sphere, raw_step) in enumerate(zip(spheres, trace["steps"])):
        step = require_object(raw_step, f"normal_surgery_trace.steps[{index}]")
        other_sphere_vertices = set().union(
            *[
                other["vertices"]
                for other_index, other in enumerate(spheres)
                if other_index != index
            ]
        )
        current_raw = replay_cut_cap_step(
            current_raw,
            sphere,
            step,
            f"normal_surgery_trace.steps[{index}]",
            detector_vertices | other_sphere_vertices,
        )
    result = validate_closed_3_complex(current_raw, "normal_surgery_trace.final")
    if result["sha256"] != trace["result_sha256"]:
        fail("normal_surgery_trace.result_sha256 disagrees with replay")
    return current_raw


def validate_detector(
    value: dict[str, Any], ambient: dict[str, Any], sphere_vertices: set[int]
) -> dict[str, Any]:
    require_fields(value, ["tetrahedra", "shelling_order"], "detector_ball")
    if not isinstance(value["tetrahedra"], list) or not value["tetrahedra"]:
        fail("detector_ball.tetrahedra must be a nonempty list of ambient tetrahedron indices")
    indices = value["tetrahedra"]
    if (
        not all(isinstance(index, int) and 0 <= index < len(ambient["tetrahedra"]) for index in indices)
        or len(set(indices)) != len(indices)
    ):
        fail("detector_ball.tetrahedra has invalid or repeated indices")
    detector_vertices = {
        vertex for index in indices for vertex in ambient["tetrahedra"][index]
    }
    if detector_vertices & sphere_vertices:
        fail("detector_ball is not disjoint from the attaching spheres")
    order = value["shelling_order"]
    if not isinstance(order, list) or sorted(order) != sorted(indices):
        fail("detector_ball.shelling_order must be a permutation of its tetrahedra")
    # A fail-closed shelling check: at each removal before the final tetrahedron,
    # the removed tetrahedron must meet the remaining subcomplex in exactly one
    # full triangular face.  This is sufficient for a ball, though restrictive.
    remaining = list(order)
    while len(remaining) > 1:
        removed = ambient["tetrahedra"][remaining.pop(0)]
        remainder_faces = {
            face for index in remaining for face in faces(ambient["tetrahedra"][index])
        }
        common = set(faces(removed)) & remainder_faces
        if len(common) != 1:
            fail("detector_ball.shelling_order is not a verified one-face shelling")
    return {"vertices": detector_vertices, "tetrahedra": indices}


def boundary_of_4_complex(value: dict[str, Any]) -> dict[str, Any]:
    require_fields(value, ["vertices", "pentachora"], "four_ball")
    vertices = value["vertices"]
    if not isinstance(vertices, list) or len(vertices) < 5:
        fail("four_ball.vertices must be an explicit list")
    if not isinstance(value["pentachora"], list) or not value["pentachora"]:
        fail("four_ball.pentachora must be a nonempty list")
    pentachora = [
        simplex(raw, 5, len(vertices), f"four_ball.pentachora[{index}]")
        for index, raw in enumerate(value["pentachora"])
    ]
    facet_counts = Counter(face for pent in pentachora for face in faces(pent))
    if set(facet_counts.values()) - {1, 2}:
        fail("four_ball has a nonmanifold tetrahedral facet multiplicity")
    boundary = [facet for facet, count in facet_counts.items() if count == 1]
    # We certify a 4-ball only by a restrictive elementary shelling.
    if len(pentachora) != 1:
        fail("v1 accepts only the canonical one-pentachoron 4-ball; no 4D shelling proof supplied")
    return {"vertices": vertices, "tetrahedra": boundary}


def validate_simplicial_isomorphism(
    source: dict[str, Any], target: dict[str, Any], value: dict[str, Any]
) -> None:
    require_fields(value, ["vertex_map"], "attaching_isomorphism")
    mapping = value["vertex_map"]
    if not isinstance(mapping, list) or len(mapping) != len(source["vertices"]):
        fail("attaching_isomorphism.vertex_map has the wrong size")
    if (
        not all(isinstance(item, int) and 0 <= item < len(target["vertices"]) for item in mapping)
        or len(set(mapping)) != len(mapping)
        or len(target["vertices"]) != len(mapping)
    ):
        fail("attaching_isomorphism.vertex_map is not a vertex bijection")
    image_tets = {
        tuple(sorted(mapping[vertex] for vertex in tet)) for tet in source["tetrahedra"]
    }
    target_tets = {tuple(sorted(tet)) for tet in target["tetrahedra"]}
    if image_tets != target_tets:
        fail("attaching_isomorphism does not carry boundary tetrahedra onto surgery_result")


def validate_standard_s3_recognition(
    target: dict[str, Any], value: Any
) -> None:
    recognition = require_object(value, "surgery_result.s3_recognition")
    require_fields(recognition, ["kind", "vertex_map"], "surgery_result.s3_recognition")
    if recognition["kind"] != "simplicial_isomorphism_to_boundary_4_simplex":
        fail(
            "v1 recognises S3 only by an explicit simplicial isomorphism "
            "to the boundary of the 4-simplex"
        )
    standard = {
        "vertices": list(range(5)),
        "tetrahedra": [
            tuple(vertex for vertex in range(5) if vertex != omitted)
            for omitted in range(5)
        ],
    }
    validate_simplicial_isomorphism(
        standard,
        target,
        {"vertex_map": recognition["vertex_map"]},
    )


def verify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    if payload.get("schema") != schema["schema"]:
        fail("input is not a t73_gs1_gp3_witness/v1 witness")
    require_fields(payload, schema["required_top_level"], "witness")
    ambient = validate_closed_3_complex(
        require_object(payload["w2_boundary"], "w2_boundary"), "w2_boundary"
    )
    raw_spheres = payload["attaching_spheres"]
    if not isinstance(raw_spheres, list) or len(raw_spheres) != 3:
        fail("attaching_spheres must contain exactly three spheres")
    spheres = [
        validate_sphere(require_object(raw, f"attaching_spheres[{index}]"), ambient, f"attaching_spheres[{index}]")
        for index, raw in enumerate(raw_spheres)
    ]
    all_sphere_vertices: set[int] = set()
    for sphere in spheres:
        if all_sphere_vertices & sphere["vertices"]:
            fail("attaching_spheres are not pairwise vertex-disjoint")
        all_sphere_vertices |= sphere["vertices"]
    detector = validate_detector(
        require_object(payload["detector_ball"], "detector_ball"),
        ambient,
        all_sphere_vertices,
    )

    trace = require_object(payload["normal_surgery_trace"], "normal_surgery_trace")
    require_fields(trace, schema["normal_surgery_trace"]["required"], "normal_surgery_trace")
    if trace["format"] != schema["normal_surgery_trace"]["format"]:
        fail("normal_surgery_trace has an unsupported format")
    if trace["source_sha256"] != ambient["sha256"]:
        fail("normal_surgery_trace is not bound to w2_boundary")
    if trace["sphere_sha256s"] != [sphere["sha256"] for sphere in spheres]:
        fail("normal_surgery_trace is not bound to the attaching spheres")
    if not isinstance(trace["steps"], list) or not trace["steps"]:
        fail("normal_surgery_trace.steps must contain explicit cut-and-cap moves")

    surgery_raw = require_object(payload["surgery_result"], "surgery_result")
    require_fields(surgery_raw, ["vertices", "tetrahedra", "s3_recognition"], "surgery_result")
    surgery = validate_closed_3_complex(surgery_raw, "surgery_result")
    if trace["result_sha256"] != surgery["sha256"]:
        fail("normal_surgery_trace is not bound to surgery_result")
    validate_standard_s3_recognition(surgery, surgery_raw["s3_recognition"])
    four_boundary = boundary_of_4_complex(
        require_object(payload["four_ball"], "four_ball")
    )
    validate_simplicial_isomorphism(
        four_boundary,
        surgery,
        require_object(payload["attaching_isomorphism"], "attaching_isomorphism"),
    )

    replayed_raw = replay_normal_surgery_trace(
        payload["w2_boundary"], ambient, spheres, trace, detector["vertices"]
    )
    if replayed_raw != {
        "vertices": surgery_raw["vertices"],
        "tetrahedra": surgery_raw["tetrahedra"],
    }:
        fail("surgery_result does not equal the final replayed surgery complex")
    return {"verdict": "PASS", "G_S1": "PROVED", "G_P3": "PROVED"}


def inspect_current() -> dict[str, Any]:
    payload = json.loads(CURRENT_W2.read_text(encoding="utf-8"))
    try:
        verify_payload(payload)
    except WitnessError as error:
        return {
            "schema": "t73_gs1_gp3_gate/v1",
            "verdict": "OPEN",
            "G_S1": "OPEN",
            "G_P3": "OPEN",
            "reason": str(error),
            "current_input": str(CURRENT_W2.relative_to(ROOT)),
        }
    raise AssertionError("current W2 metadata unexpectedly passed the fail-closed gate")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("witness", nargs="?", type=Path)
    parser.add_argument("--check-current", action="store_true")
    args = parser.parse_args()
    if args.check_current or args.witness is None:
        result = inspect_current()
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    payload = json.loads(args.witness.read_text(encoding="utf-8"))
    try:
        result = verify_payload(payload)
    except WitnessError as error:
        result = {"verdict": "OPEN", "G_S1": "OPEN", "G_P3": "OPEN", "reason": str(error)}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
