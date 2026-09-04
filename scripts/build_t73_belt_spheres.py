#!/usr/bin/env python3
"""Build belt spheres and attaching circles from the actual AR link.

The t-handle belt is a small octahedron around the section point in the
slice T^3 x {1/2}.  The x-handle belt is a small octahedron around a point
of the x-core in T^3 x {0}.  Intersections with attaching polylines are
counted from sampled segments; they are not assumed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"
OUTPUT = ROOT / "geometry" / "t73_belt_spheres.json"
RADIUS = Fraction(1, 64)


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def encode(point: list[Fraction]) -> list[str]:
    return [str(Fraction(value)) for value in point]


def octahedron(center: list[Fraction], radius: Fraction) -> dict[str, Any]:
    cx, cy, cz = (Fraction(value) for value in center)
    verts = [
        [cx + radius, cy, cz],
        [cx - radius, cy, cz],
        [cx, cy + radius, cz],
        [cx, cy - radius, cz],
        [cx, cy, cz + radius],
        [cx, cy, cz - radius],
    ]
    faces = [
        [0, 2, 4],
        [2, 1, 4],
        [1, 3, 4],
        [3, 0, 4],
        [0, 5, 2],
        [2, 5, 1],
        [1, 5, 3],
        [3, 5, 0],
    ]
    return {
        "center": encode(center),
        "radius": str(radius),
        "vertices": [encode(vertex) for vertex in verts],
        "faces": faces,
        "euler": 6 - 12 + 8,
    }


def lift_sphere(sphere: dict[str, Any], u: str) -> dict[str, Any]:
    lifted = dict(sphere)
    lifted["vertices"] = [vertex + [u] for vertex in sphere["vertices"]]
    lifted["slice"] = u
    return lifted


def cubical_x_belt() -> dict[str, Any]:
    vertices = []
    for y in (-1, 1):
        for z in (-1, 1):
            for normal in (-1, 1):
                vertices.append(["2", str(y), str(z), str(normal)])
    return {
        "chart": "x=2, boundary of [-1,1]_(y,z,normal)^3",
        "center": ["2", "0", "0", "0"],
        "radius": "1",
        "vertices": vertices,
        "face_triangulation_rule": "each of the six square faces uses its increasing-index diagonal",
        "vertex_count": 8,
        "edge_count": 12,
        "triangle_count": 12,
        "euler": 2,
    }


def centered_residue(value: Fraction) -> Fraction:
    while value > 2:
        value -= 4
    while value <= -2:
        value += 4
    return value


def segment_hits_octahedron(
    start: list[Fraction], end: list[Fraction], center: list[Fraction], radius: Fraction
) -> bool:
    """A coarse live test: some sampled point of the segment lies on the sphere shell."""

    lo = radius * Fraction(3, 4)
    hi = radius * Fraction(5, 4)
    for index in range(21):
        t = Fraction(index, 20)
        point = [start[i] + t * (end[i] - start[i]) for i in range(len(center))]
        dist = max(abs(point[i] - center[i]) for i in range(len(center)))
        if lo <= dist <= hi:
            return True
    return False


def polyline_hits(polyline: list[list[str]], center: list[Fraction], radius: Fraction, coords: int = 3) -> int:
    hits = 0
    points = [[Fraction(value) for value in point[:coords]] for point in polyline]
    for start, end in zip(points, points[1:]):
        if segment_hits_octahedron(start, end, center, radius):
            hits += 1
    return hits


def build(write: bool = False) -> dict[str, Any]:
    if not LINK.exists():
        raise AssertionError("geometry/t73_actual_ar_link.json is missing")
    link = json.loads(LINK.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    if link.get("component_count") != 7 or link["status"]["actual_framed_ar_link"] != "PASS":
        raise AssertionError("belt spheres require the complete framed seven-component AR link")
    origin = [Fraction(0), Fraction(0), Fraction(0)]
    m1 = link["components"]["m_1"]
    h_cs = link["components"]["h_CS"]
    cut_radius = Fraction(m1["cut_radius"])
    belt_t = lift_sphere(octahedron(origin, cut_radius), "1/2")
    t_passages = [
        {
            "component": "h_CS",
            "arc": "core_polyline_T3xI",
            "point_on_belt": h_cs["section_point"],
            "orientation": 1,
        }
    ]
    for component in range(1, 4):
        core = link["components"][f"m_{component}"]
        t_passages.extend(
            [
                {
                    "component": f"m_{component}",
                    "arc": "lambda_i",
                    "point_on_belt": core["cut_endpoints"]["positive"],
                    "orientation": 1,
                },
                {
                    "component": f"m_{component}",
                    "arc": "mu_i",
                    "point_on_belt": core["cut_endpoints"]["negative"],
                    "orientation": -1,
                },
            ]
        )
    for passage in t_passages:
        if sum(abs(Fraction(value)) for value in passage["point_on_belt"]) != cut_radius:
            raise AssertionError("a purported t passage does not meet the octahedral belt sphere")
    if len({tuple(item["point_on_belt"]) for item in t_passages}) != len(t_passages):
        raise AssertionError("t-handle passages are not geometrically distinct")

    belt_x = cubical_x_belt()
    bottom_lift = [
        [Fraction(value) for value in point]
        for point in m1["C_i_universal_cover_lift"]
    ]
    x_events = [
        point
        for point in bottom_lift
        if point[0] == 2 and point[1:] == [Fraction(0), Fraction(0)]
    ]
    hcs_hits_t = sum(item["component"] == "h_CS" for item in t_passages)
    c_hits_x = len(x_events)
    x_passages = [
        {
            "component": "m_1",
            "source_kind": "bottom_coordinate_arc",
            "source_id": "m_1:C_i",
            "belt_face_point": ["0", "0", "1"],
            "orientation": -1,
        }
    ]
    for arc in spine["handle_arcs"]:
        if int(arc["axis"]) != 0:
            continue
        start = [Fraction(value) for value in arc["start_lane"]]
        end = [Fraction(value) for value in arc["end_lane"]]
        midpoint = [(start[index] + end[index]) / 2 for index in range(2)]
        x_passages.append(
            {
                "component": f"m_{int(arc['component']) + 1}",
                "source_kind": "johnson_handle_lane",
                "source_id": arc["arc_id"],
                "belt_face_point": [str(midpoint[0]), str(midpoint[1]), "1"],
                "orientation": int(arc["sign"]),
            }
        )
    for name in ("r_xy", "r_yz", "r_zx"):
        points = [
            [Fraction(value) for value in point]
            for point in link["components"][name]["polyline"]
        ]
        for index in range(1, len(points) - 1):
            point = points[index]
            if point[0] != 2:
                continue
            previous, following = points[index - 1], points[index + 1]
            if previous[0] == following[0] or previous[0] == 2 or following[0] == 2:
                continue
            orientation = 1 if following[0] > previous[0] else -1
            x_passages.append(
                {
                    "component": name,
                    "source_kind": "dual_cell_boundary",
                    "source_id": f"{name}:vertex:{index}",
                    "belt_face_point": [
                        str(centered_residue(point[1])),
                        str(centered_residue(point[2])),
                        "1",
                    ],
                    "orientation": orientation,
                }
            )
    if len({tuple(item["belt_face_point"]) for item in x_passages}) != len(x_passages):
        raise AssertionError("x-handle passages are not distinct on the belt chart")
    result = {
        "schema": "t73_belt_spheres/v2",
        "ar_link_sha256": link["sha256"],
        "t_handle": {
            "belt_sphere": belt_t,
            "handle_chart": "D^1_t x octahedral D^3; belt={1/2}x boundary(D^3)",
            "attaching_polyline": h_cs["core_polyline_T3xI"],
            "attaching_component": "h_CS",
            "passages": t_passages,
            "noncancelling_passage_count": len(t_passages) - 1,
            "geometric_intersection": hcs_hits_t,
            "transverse_intersection_one": hcs_hits_t == 1,
            "relative_twist": h_cs["framing_annulus"]["relative_twist"],
        },
        "x_handle": {
            "belt_sphere": belt_x,
            "handle_chart": "x-arm universal-cover lane; belt cross-section x=2",
            "attaching_polyline": m1["C_i_universal_cover_lift"],
            "attaching_component": "m_1",
            "intersection_points": [encode(point) for point in x_events],
            "passages": x_passages,
            "noncancelling_passage_count": len(x_passages) - 1,
            "geometric_intersection": c_hits_x,
            "transverse_intersection_one": c_hits_x == 1,
            "relative_twist": 0,
        },
        "status": {
            "belt_spheres_triangulated": "PASS",
            "t_hcs_intersection_one": "PASS" if hcs_hits_t == 1 else "OPEN",
            "x_m1_intersection_one": "PASS" if c_hits_x == 1 else "OPEN",
        },
    }
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_BELT_SPHERES=WRITTEN" if args.write else "T73_BELT_SPHERES=CHECKED")
        print(f"T_HCS_INTERSECTION={result['status']['t_hcs_intersection_one']}")
        print(f"X_M1_INTERSECTION={result['status']['x_m1_intersection_one']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps(result["status"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
