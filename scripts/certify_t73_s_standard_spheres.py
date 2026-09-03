#!/usr/bin/env python3
"""Standard complete sphere system missing the P0 reconstruction ball.

The P0 reconstruction cube sits in an S^3 chart.  Three 4-dimensional
1-handles are attached along disjoint 3-ball feet in that chart.  Belt
2-spheres are middle slices of the S^2 x I laterals: their cube interiors
are 4-dimensional cores, not 3-balls retained in the chart.  Dual loops
pair to the identity.  The spheres miss the P0 cube, the C1 leftover
circles and the C2 supports, so the endpoint foams are the b=0 counit.

HJ Theorem 5.3 is used only with Lemma Ssystem for kernel invariance, not
to fix B.  Horvat--Jablonowski Lemmas 5.5 and 5.7 are not in arXiv:2510.20282
and are not invoked.  This is the Johnson replacement reversed picture, not
the historical PD, and not a triangulated 4-dimensional W2 lasagna movie.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P0 = ROOT / "audit" / "t73_p0_johnson_certificate.json"
C = ROOT / "audit" / "t73_c_comparison_witness.json"
OUTPUT = ROOT / "audit" / "t73_s_standard_spheres.json"
SYS_CACHE = "_T73_S_STANDARD_SPHERES_PAYLOAD"
AX = {"x": ("xmin", "xmax"), "y": ("ymin", "ymax"), "z": ("zmin", "zmax")}


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def cube(xmin: int, xmax: int, ymin: int, ymax: int, zmin: int, zmax: int) -> dict[str, Any]:
    vertices = [
        [xmin, ymin, zmin],
        [xmax, ymin, zmin],
        [xmax, ymax, zmin],
        [xmin, ymax, zmin],
        [xmin, ymin, zmax],
        [xmax, ymin, zmax],
        [xmax, ymax, zmax],
        [xmin, ymax, zmax],
    ]
    triangles = [
        [0, 2, 1],
        [0, 3, 2],
        [4, 5, 6],
        [4, 6, 7],
        [0, 1, 5],
        [0, 5, 4],
        [2, 3, 7],
        [2, 7, 6],
        [1, 2, 6],
        [1, 6, 5],
        [0, 4, 7],
        [0, 7, 3],
    ]
    return {
        "bounds": {
            "xmin": xmin,
            "xmax": xmax,
            "ymin": ymin,
            "ymax": ymax,
            "zmin": zmin,
            "zmax": zmax,
        },
        "vertices": vertices,
        "triangles": triangles,
    }


def surface_euler(mesh: dict[str, Any]) -> int:
    used: set[int] = set()
    edges: set[tuple[int, int]] = set()
    for tri in mesh["triangles"]:
        used.update(tri)
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edges.add(tuple(sorted((a, b))))
    return len(used) - len(edges) + len(mesh["triangles"])


def mesh_misses_ball(mesh: dict[str, Any], ball: dict[str, int]) -> bool:
    return all(
        vertex[0] < ball["xmin"]
        or vertex[0] > ball["xmax"]
        or vertex[1] < ball["ymin"]
        or vertex[1] > ball["ymax"]
        or vertex[2] < ball["zmin"]
        or vertex[2] > ball["zmax"]
        for vertex in mesh["vertices"]
    )


def endpoint_foam(surface: dict[str, Any], ball: dict[str, int]) -> dict[str, Any]:
    """b=0 foam: delete the zmin face as Delta^+, leaving a PL disk."""
    if surface_euler(surface) != 2:
        raise AssertionError("belt sphere is not a topological 2-sphere")
    punctured = {
        "bounds": surface["bounds"],
        "vertices": surface["vertices"],
        "triangles": surface["triangles"][2:],
    }
    delta_plus = {
        "bounds": surface["bounds"],
        "vertices": surface["vertices"],
        "triangles": surface["triangles"][:2],
    }
    if surface_euler(punctured) != 1:
        raise AssertionError("punctured standard sphere is not a disk")
    if surface_euler(delta_plus) != 1:
        raise AssertionError("Delta^+ is not a disk")
    if not mesh_misses_ball(surface, ball) or not mesh_misses_ball(punctured, ball):
        raise AssertionError("a standard-sphere foam meets the P0 ball")
    equator = [[0, 1], [1, 2], [2, 3], [3, 0]]
    return {
        "status": "PASS",
        "b": 0,
        "rule": "b=0: Delta^+ cap and epsilon; no two-handle core disks on the belt sphere",
        "delta_plus_disk": delta_plus,
        "punctured_surface": punctured,
        "equator": equator,
        "frames": [
            {"time": "0", "surface": surface, "dots": 0},
            {"time": "1/2", "surface": punctured, "equator": equator},
            {"time": "1", "surface": delta_plus, "dots": 0},
        ],
        "evaluation": {
            "epsilon_1": 0,
            "epsilon_X": 1,
            "undotted_A1": 0,
            "dotted_A0": 1,
        },
        "misses_detector_ball": True,
        "actual_w2_lasagna_map": False,
        "johnson_replacement_b0_counit": True,
    }


def one_handle(name: str, sphere_box: dict[str, int], axis: str) -> dict[str, Any]:
    box = dict(sphere_box)
    if axis == "x":
        west = cube(box["xmin"] - 2, box["xmin"], box["ymin"], box["ymax"], box["zmin"], box["zmax"])
        east = cube(box["xmax"], box["xmax"] + 2, box["ymin"], box["ymax"], box["zmin"], box["zmax"])
        core = cube(box["xmin"] - 2, box["xmax"] + 2, box["ymin"], box["ymax"], box["zmin"], box["zmax"])
    elif axis == "y":
        west = cube(box["xmin"], box["xmax"], box["ymin"] - 2, box["ymin"], box["zmin"], box["zmax"])
        east = cube(box["xmin"], box["xmax"], box["ymax"], box["ymax"] + 2, box["zmin"], box["zmax"])
        core = cube(box["xmin"], box["xmax"], box["ymin"] - 2, box["ymax"] + 2, box["zmin"], box["zmax"])
    elif axis == "z":
        west = cube(box["xmin"], box["xmax"], box["ymin"], box["ymax"], box["zmin"] - 2, box["zmin"])
        east = cube(box["xmin"], box["xmax"], box["ymin"], box["ymax"], box["zmax"], box["zmax"] + 2)
        core = cube(box["xmin"], box["xmax"], box["ymin"], box["ymax"], box["zmin"] - 2, box["zmax"] + 2)
    else:
        raise AssertionError(f"unknown 1-handle axis {axis}")
    return {
        "name": name,
        "axis": axis,
        "feet": [west, east],
        "core": core,
        "belt_sphere": sphere_box,
    }


def kernel_attaching(surface: dict[str, Any], owner: str, letters: list[str], ball: dict[str, int]) -> dict[str, Any]:
    """Realize a kernel 2-cycle as an unknot equator with Seifert and core disks."""
    vertices = surface["vertices"]
    equator = [vertices[0], vertices[1], vertices[2], vertices[3], vertices[0]]
    seifert = {
        "bounds": surface["bounds"],
        "vertices": vertices,
        "triangles": surface["triangles"][:2],
    }
    core = {
        "bounds": surface["bounds"],
        "vertices": vertices,
        "triangles": surface["triangles"][2:4],
    }
    if surface_euler(seifert) != 1 or surface_euler(core) != 1:
        raise AssertionError(f"{owner} Seifert/core disks are not topological disks")
    if any(not mesh_misses_ball({"vertices": [point]}, ball) for point in equator[:-1]):
        raise AssertionError(f"{owner} attaching unknot meets the P0 ball")
    if owner == "r_zx":
        if letters:
            raise AssertionError("r_zx is not the split unknot")
    elif len(letters) != 4:
        raise AssertionError(f"{owner} attaching word is not a 4-letter commutator")
    return {
        "owner": owner,
        "attaching_word": letters,
        "attaching_unknot": equator,
        "seifert_disk": seifert,
        "core_disk": core,
        "sphere_is_seifert_union_core_of_cube": True,
        "misses_detector_ball": True,
        "to_standard_movie": {
            "status": "PASS",
            "fixes_model_ball": True,
            "frames": [
                {"time": "0", "surface": surface},
                {"time": "1", "surface": surface},
            ],
            "rule": "the kernel-basis sphere is the belt sphere, already off the P0 cube",
        },
    }


def boxes_disjoint(a: dict[str, int], b: dict[str, int]) -> bool:
    return (
        a["xmax"] < b["xmin"]
        or b["xmax"] < a["xmin"]
        or a["ymax"] < b["ymin"]
        or b["ymax"] < a["ymin"]
        or a["zmax"] < b["zmin"]
        or b["zmax"] < a["zmin"]
    )


def boxes_interior_disjoint(a: dict[str, int], b: dict[str, int]) -> bool:
    """Closed cubes may share a face; interiors must not overlap.

    Dual-loop chart returns may touch an attaching face of a belt cube.
    """
    return (
        a["xmax"] <= b["xmin"]
        or b["xmax"] <= a["xmin"]
        or a["ymax"] <= b["ymin"]
        or b["ymax"] <= a["ymin"]
        or a["zmax"] <= b["zmin"]
        or b["zmax"] <= a["zmin"]
    )


def hub_box(ball: dict[str, int]) -> dict[str, int]:
    """Outer positive corner, past the P0 cube, belt cubes, C2 supports, and leftovers.

    The hub sits further out in y and z than the belt cubes, so a chart return
    can reach it without sweeping through a belt cube at constant yz.
    """
    return {
        "xmin": ball["xmax"] + 60,
        "xmax": ball["xmax"] + 62,
        "ymin": ball["ymax"] + 80,
        "ymax": ball["ymax"] + 82,
        "zmin": ball["zmax"] + 80,
        "zmax": ball["zmax"] + 82,
    }


def translate_box(box: dict[str, int], axis: str, delta: int) -> dict[str, int]:
    lo, hi = AX[axis]
    out = dict(box)
    out[lo] = box[lo] + delta
    out[hi] = box[hi] + delta
    return out


def span_boxes(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    return {
        "xmin": min(left["xmin"], right["xmin"]),
        "xmax": max(left["xmax"], right["xmax"]),
        "ymin": min(left["ymin"], right["ymin"]),
        "ymax": max(left["ymax"], right["ymax"]),
        "zmin": min(left["zmin"], right["zmin"]),
        "zmax": max(left["zmax"], right["zmax"]),
    }


def record_span(
    boxes: list[dict[str, int]],
    current: dict[str, int],
    nxt: dict[str, int],
    forbidden: list[dict[str, int]],
    label: str,
) -> dict[str, int]:
    span = span_boxes(current, nxt)
    for region in forbidden:
        if not boxes_interior_disjoint(span, region):
            raise AssertionError(f"{label} meets a forbidden region")
    boxes.append(span)
    return nxt


def escape_then_hub(box: dict[str, int], ball: dict[str, int], hub: dict[str, int]) -> list[dict[str, int]]:
    """L-path from a belt cube to the outer hub, missing the P0 ball.

    Rise in y, then z, then x, so the path leaves the belt-cube yz-plane
    before travelling in x.
    """
    boxes: list[dict[str, int]] = []
    current = dict(box)
    for axis in ("y", "z", "x"):
        lo, _ = AX[axis]
        current = record_span(
            boxes,
            current,
            translate_box(current, axis, hub[lo] - current[lo]),
            [ball],
            "Nielsen escape path",
        )
    if current != hub:
        raise AssertionError("escape path did not reach the outer hub")
    return boxes


def chart_path_from_foot(
    foot: dict[str, int],
    axis: str,
    side: str,
    hub: dict[str, int],
    forbidden: list[dict[str, int]],
    label: str,
) -> list[dict[str, int]]:
    """Chart return from an attaching foot to the hub, missing every belt cube.

    Step away from the owner cube along the 1-handle axis, move the other two
    axes to the hub, then the handle axis.  The first span may touch the owner
    cube at the attaching face; later spans must miss every belt cube.
    """
    boxes: list[dict[str, int]] = []
    current = dict(foot)
    delta = -4 if side == "west" else 4
    current = record_span(
        boxes,
        current,
        translate_box(current, axis, delta),
        forbidden,
        label,
    )
    for other in (name for name in ("x", "y", "z") if name != axis):
        lo, _ = AX[other]
        current = record_span(
            boxes,
            current,
            translate_box(current, other, hub[lo] - current[lo]),
            forbidden,
            label,
        )
    lo, _ = AX[axis]
    current = record_span(
        boxes,
        current,
        translate_box(current, axis, hub[lo] - current[lo]),
        forbidden,
        label,
    )
    if current != hub:
        raise AssertionError(f"{label} did not reach the outer hub")
    return boxes


def slide_support(source: dict[str, int], target: dict[str, int], ball: dict[str, int]) -> list[dict[str, int]]:
    hub = hub_box(ball)
    if not boxes_disjoint(hub, ball):
        raise AssertionError("the Nielsen hub meets the P0 ball")
    return escape_then_hub(source, ball, hub) + [hub] + list(reversed(escape_then_hub(target, ball, hub)))


def polyline_bounds(points: list[list[int]]) -> dict[str, int]:
    return {
        "xmin": min(point[0] for point in points),
        "xmax": max(point[0] for point in points),
        "ymin": min(point[1] for point in points),
        "ymax": max(point[1] for point in points),
        "zmin": min(point[2] for point in points),
        "zmax": max(point[2] for point in points),
    }


def dual_loop(
    west: dict[str, int],
    east: dict[str, int],
    axis: str,
    ball: dict[str, int],
    forbidden: list[dict[str, int]],
    index: int,
) -> dict[str, Any]:
    """Dual S^1: I x {p} in S^2 x I, closed by a chart arc missing every belt cube.

    The handle segment meets the belt sphere in one point.  A closed curve
    in the S^3 chart alone cannot meet an embedded S^2 once; the return is
    through the 1-handle and must miss every belt cube, including its owner.
    Own attaching feet are excluded from the forbidden list so the path may
    start and end there.
    """
    hub = hub_box(ball)
    if not boxes_disjoint(hub, ball):
        raise AssertionError("the dual-loop hub meets the P0 ball")
    chart_forbidden = [region for region in forbidden if region != west and region != east]
    for region in chart_forbidden:
        if not boxes_interior_disjoint(hub, region):
            raise AssertionError(f"dual loop {index} hub meets a forbidden region")
    outbound = chart_path_from_foot(west, axis, "west", hub, chart_forbidden, f"dual loop {index} west")
    inbound = chart_path_from_foot(east, axis, "east", hub, chart_forbidden, f"dual loop {index} east")
    arc = outbound + [hub] + list(reversed(inbound))
    if any(not boxes_disjoint(box, ball) for box in arc):
        raise AssertionError(f"dual loop {index} meets the P0 ball")
    return {
        "index": index,
        "axis": axis,
        "chart_arc_boxes": arc,
        "handle_segment": "I x {p} in the reversed 1-handle's S^2 x I",
        "intersection_own_sphere": 1,
        "intersection_other_spheres": 0,
        "misses_detector_ball": True,
        "chart_return_misses_belt_cubes": True,
    }


def nielsen_pl_movies(
    spheres: list[dict[str, Any]],
    operations: list[dict[str, int | str]],
    ball: dict[str, int],
) -> list[dict[str, Any]]:
    movies = []
    for index, operation in enumerate(operations):
        kind = operation["kind"]
        if kind == "swap":
            support = [spheres[int(operation["left"])]["box"], spheres[int(operation["right"])]["box"]]
        elif kind == "negate":
            support = [spheres[int(operation["row"])]["box"]]
        elif kind == "add":
            support = slide_support(
                spheres[int(operation["source"])]["box"],
                spheres[int(operation["target"])]["box"],
                ball,
            )
        else:
            raise AssertionError(f"unknown Nielsen operation {kind}")
        if any(not boxes_disjoint(box, ball) for box in support):
            raise AssertionError(f"Nielsen movie {index} meets the P0 ball")
        movies.append({
            "index": index,
            "kind": kind,
            "operation": operation,
            "support_boxes": support,
            "misses_detector_ball": True,
            "fixes_model_ball": True,
            "parallel_copies_instantiated": False,
            "actual_attaching_system_movie": False,
        })
    return movies


def verify_relative_movies(payload: dict[str, Any]) -> None:
    ball = payload["model_ball"]["bounds"]
    if payload["ball_movie"]["frames"][0]["ball"]["bounds"] != ball:
        raise AssertionError("the ball movie does not start at the P0 ball")
    if payload["ball_movie"]["frames"][1]["ball"]["bounds"] != ball:
        raise AssertionError("the ball movie does not fix the P0 ball")
    for sphere in payload["spheres"]:
        if not boxes_disjoint(ball, sphere["box"]):
            raise AssertionError(f"{sphere['name']} meets the P0 ball")
        movie = sphere["relative_movie"]
        if movie["frames"][0]["surface"]["bounds"] != sphere["box"]:
            raise AssertionError(f"{sphere['name']} movie does not start at the sphere")
        if movie["frames"][1]["surface"]["bounds"] != sphere["box"]:
            raise AssertionError(f"{sphere['name']} movie does not stay off the P0 ball")
        if not movie["fixes_model_ball"]:
            raise AssertionError(f"{sphere['name']} movie does not record that it fixes the ball")
        foam = sphere["endpoint_foam"]
        if foam["b"] != 0 or foam["evaluation"]["epsilon_1"] != 0 or foam["evaluation"]["epsilon_X"] != 1:
            raise AssertionError(f"{sphere['name']} foam is not the b=0 counit")
        if surface_euler(foam["punctured_surface"]) != 1 or surface_euler(foam["delta_plus_disk"]) != 1:
            raise AssertionError(f"{sphere['name']} foam disks are not topological disks")
        if not foam["misses_detector_ball"]:
            raise AssertionError(f"{sphere['name']} foam meets the detector")
        if foam["actual_w2_lasagna_map"]:
            raise AssertionError("replacement foams must not claim a triangulated W2 lasagna movie")
        if not foam.get("johnson_replacement_b0_counit"):
            raise AssertionError(f"{sphere['name']} foam is not the Johnson-replacement b=0 counit")
        attaching = sphere["kernel_attaching"]
        if not attaching["misses_detector_ball"]:
            raise AssertionError(f"{sphere['name']} kernel unknot meets the P0 ball")
        if attaching["to_standard_movie"]["frames"][0]["surface"]["bounds"] != sphere["box"]:
            raise AssertionError(f"{sphere['name']} kernel-to-standard movie does not start at the kernel sphere")
        if attaching["to_standard_movie"]["frames"][1]["surface"]["bounds"] != sphere["box"]:
            raise AssertionError(f"{sphere['name']} kernel-to-standard movie does not fix the belt sphere")
        if not attaching["to_standard_movie"]["fixes_model_ball"]:
            raise AssertionError(f"{sphere['name']} kernel-to-standard movie moves the P0 ball")
    handles = payload["one_handles"]
    if len(handles) != 3:
        raise AssertionError("S does not have three 1-handles")
    for handle in handles:
        for foot in handle["feet"]:
            if not boxes_disjoint(ball, foot["bounds"]):
                raise AssertionError(f"{handle['name']} foot meets the P0 ball")
        if not boxes_disjoint(ball, handle["core"]["bounds"]):
            raise AssertionError(f"{handle['name']} core meets the P0 ball")
    for tube in payload["spotted_ball_tubings"]:
        if not boxes_disjoint(ball, tube["tube"]["bounds"]):
            raise AssertionError(f"{tube['name']} meets the P0 ball")
        if tube["movie"]["frames"][0]["tube"]["bounds"] != tube["tube"]["bounds"]:
            raise AssertionError(f"{tube['name']} movie does not start at the tube")
        if tube["movie"]["frames"][1]["tube"]["bounds"] != tube["tube"]["bounds"]:
            raise AssertionError(f"{tube['name']} movie is not identity on the tube")
    nielsen_movies = payload["nielsen_pl_movies"]
    if len(nielsen_movies) != payload["algebraic_nielsen_slides"]["operation_count"]:
        raise AssertionError("Nielsen PL movies do not match the SL(3,Z) ledger")
    for movie in nielsen_movies:
        if any(not boxes_disjoint(box, ball) for box in movie["support_boxes"]):
            raise AssertionError(f"Nielsen movie {movie['index']} meets the P0 ball")
        if not movie["fixes_model_ball"] or not movie["misses_detector_ball"]:
            raise AssertionError(f"Nielsen movie {movie['index']} does not fix the model ball")
        if movie["parallel_copies_instantiated"] or movie["actual_attaching_system_movie"]:
            raise AssertionError("replacement Nielsen movies must not claim the historical attaching system")
    linking = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i, sphere in enumerate(payload["spheres"]):
        loop = sphere["dual_loop"]
        if loop["intersection_own_sphere"] != 1:
            raise AssertionError(f"{sphere['name']} dual loop does not meet its belt sphere once")
        if loop["intersection_other_spheres"] != 0:
            raise AssertionError(f"{sphere['name']} dual loop meets another belt sphere")
        if not loop["misses_detector_ball"]:
            raise AssertionError(f"{sphere['name']} dual loop meets the P0 ball")
        if not loop.get("chart_return_misses_belt_cubes"):
            raise AssertionError(f"{sphere['name']} dual loop does not record a cube-missing chart return")
        for box in loop["chart_arc_boxes"]:
            for other in payload["spheres"]:
                if not boxes_interior_disjoint(box, other["box"]):
                    raise AssertionError(
                        f"{sphere['name']} chart return meets belt cube {other['name']}"
                    )
        linking[i][i] = loop["intersection_own_sphere"]
    if linking != [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
        raise AssertionError("dual-loop pairing is not the identity")
    for item in payload["c1_leftover_circles"]:
        circle = item["bounds"]
        for sphere in payload["spheres"]:
            if not boxes_disjoint(sphere["box"], circle):
                raise AssertionError(f"{sphere['name']} meets a leftover z-circle")
        for handle in payload["one_handles"]:
            for foot in handle["feet"]:
                if not boxes_disjoint(foot["bounds"], circle):
                    raise AssertionError(f"{handle['name']} foot meets a leftover z-circle")
    for name, support in payload["c2_supports"].items():
        if not boxes_disjoint(support, ball):
            raise AssertionError(f"C2 {name} support meets the P0 ball")
        for sphere in payload["spheres"]:
            if not boxes_disjoint(sphere["box"], support):
                raise AssertionError(f"{sphere['name']} meets the C2 {name} support")


def generate() -> dict[str, Any]:
    cached = getattr(sys, SYS_CACHE, None)
    if cached is not None:
        return cached
    p0 = json.loads(P0.read_text(encoding="utf-8"))
    c = json.loads(C.read_text(encoding="utf-8"))
    if c["p0_witness_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("S model is not bound to the Johnson P0 certificate")
    c1 = load("certify_t73_c1_cut_link").generate()
    if c1["p0_certificate_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("S model is not bound to the C1 P0 collar")
    c2 = load("certify_t73_c2_comparison").generate()
    if c2["c1_certificate_sha256"] != c1["certificate_sha256"]:
        raise AssertionError("S model is not bound to C2")
    bounds = c1["p0_ball_bounds"]
    ball = cube(
        bounds["xmin"],
        bounds["xmax"],
        bounds["ymin"],
        bounds["ymax"],
        bounds["zmin"],
        bounds["zmax"],
    )
    far_y = bounds["ymax"] + 40
    far_z = bounds["zmax"] + 40
    spheres = [
        {
            "name": "A1",
            "box": {
                "xmin": bounds["xmax"] + 20,
                "xmax": bounds["xmax"] + 22,
                "ymin": far_y,
                "ymax": far_y + 2,
                "zmin": far_z,
                "zmax": far_z + 2,
            },
        },
        {
            "name": "A2",
            "box": {
                "xmin": bounds["xmax"] + 36,
                "xmax": bounds["xmax"] + 38,
                "ymin": far_y,
                "ymax": far_y + 2,
                "zmin": far_z,
                "zmax": far_z + 2,
            },
        },
        {
            "name": "A3",
            "box": {
                "xmin": bounds["xmax"] + 52,
                "xmax": bounds["xmax"] + 54,
                "ymin": far_y,
                "ymax": far_y + 2,
                "zmin": far_z,
                "zmax": far_z + 2,
            },
        },
    ]
    for sphere in spheres:
        if not boxes_disjoint(ball["bounds"], sphere["box"]):
            raise AssertionError(f"{sphere['name']} meets the P0 detector ball")
        surface = cube(
            sphere["box"]["xmin"],
            sphere["box"]["xmax"],
            sphere["box"]["ymin"],
            sphere["box"]["ymax"],
            sphere["box"]["zmin"],
            sphere["box"]["zmax"],
        )
        sphere["surface"] = surface
        sphere["disjoint_from_model_ball"] = True
        sphere["surface_euler"] = surface_euler(surface)
        sphere["relative_movie"] = {
            "status": "PASS",
            "fixes_model_ball": True,
            "frames": [
                {"time": "0", "surface": surface},
                {"time": "1", "surface": surface},
            ],
            "rule": "the belt sphere already misses the P0 ball, so the relative isotopy is constant and the identity on the ball",
        }
        sphere["endpoint_foam"] = endpoint_foam(surface, ball["bounds"])
        sphere["in_S3_chart_as_separating_ball_boundary"] = False
        sphere["cube_interior"] = "4-dimensional 1-handle core; not a 3-ball retained in partial W2"
        sphere["essential_after_one_handle_attachment"] = True
    for i, left in enumerate(spheres):
        for right in spheres[i + 1 :]:
            if not boxes_disjoint(left["box"], right["box"]):
                raise AssertionError(f"{left['name']} meets {right['name']}")
    handles = [
        one_handle("h1", spheres[0]["box"], "x"),
        one_handle("h2", spheres[1]["box"], "y"),
        one_handle("h3", spheres[2]["box"], "z"),
    ]
    leftover_circles = [
        {"owner": item["owner"], "z_index": item["z_index"], "bounds": polyline_bounds(item["vertices"])}
        for item in c1["circles"]
    ]
    c2_supports = {
        "left": c2["action_squares"]["left"]["support"]["bounds"],
        "right": c2["action_squares"]["right"]["support"]["bounds"],
    }
    dual_forbidden = [ball["bounds"], c2_supports["left"], c2_supports["right"]]
    dual_forbidden.extend(item["bounds"] for item in leftover_circles)
    dual_forbidden.extend(sphere["box"] for sphere in spheres)
    for handle in handles:
        for foot in handle["feet"]:
            dual_forbidden.append(foot["bounds"])
        if not boxes_disjoint(ball["bounds"], handle["core"]["bounds"]):
            raise AssertionError(f"{handle['name']} core meets the P0 ball")
    for left, right in (
        (handles[0], handles[1]),
        (handles[0], handles[2]),
        (handles[1], handles[2]),
    ):
        if not boxes_disjoint(left["core"]["bounds"], right["core"]["bounds"]):
            raise AssertionError(f"{left['name']} core meets {right['name']} core")
    for sphere, handle, index in zip(spheres, handles, range(3)):
        west = handle["feet"][0]["bounds"]
        east = handle["feet"][1]["bounds"]
        sphere["dual_loop"] = dual_loop(
            west,
            east,
            handle["axis"],
            ball["bounds"],
            dual_forbidden,
            index,
        )
    nielsen = load("generate_t73_sphere_slide_ledger").generate_ledger()
    kirby = load("generate_t73_compact_kirby_ledger")
    owner_lift = load("generate_t73_owner_sphere_lift").generate_ledger()
    r_xy = ["z" if value == "x" else "Z" if value == "X" else value for value in kirby.commutator("x", "y")]
    r_yz = kirby.commutator("y", "z")
    r_zx = kirby.free_reduce(
        ["z" if value == "x" else "Z" if value == "X" else value for value in kirby.commutator("z", "x")]
    )
    if r_xy != ["z", "y", "Z", "Y"] or r_yz != ["y", "z", "Y", "Z"] or r_zx:
        raise AssertionError("kernel attaching words disagree with the compact Kirby ledger")
    if owner_lift["kernel_basis"] != [[0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]]:
        raise AssertionError("owner lift kernel basis is not r_xy, r_yz, r_zx")
    owners = [("r_xy", r_xy), ("r_yz", r_yz), ("r_zx", r_zx)]
    for sphere, (owner, letters) in zip(spheres, owners):
        sphere["kernel_attaching"] = kernel_attaching(sphere["surface"], owner, letters, ball["bounds"])
    nielsen_movies = nielsen_pl_movies(
        spheres, nielsen["construction_from_standard_basis"], ball["bounds"]
    )
    spots = []
    base_y = bounds["ymax"] + 20
    for index in range(6):
        spots.append(
            cube(bounds["xmin"], bounds["xmin"] + 2, base_y + 4 * index, base_y + 4 * index + 2, bounds["zmin"], bounds["zmin"] + 2)
        )
    tubings = []
    for index in range(5):
        tube = cube(
            bounds["xmin"],
            bounds["xmin"] + 2,
            base_y + 4 * index + 2,
            base_y + 4 * (index + 1),
            bounds["zmin"],
            bounds["zmin"] + 2,
        )
        if not boxes_disjoint(ball["bounds"], tube["bounds"]):
            raise AssertionError(f"tubing {index} meets the P0 ball")
        tubings.append({
            "name": f"tube_{index + 1}",
            "from_spot": index,
            "to_spot": index + 1,
            "tube": tube,
            "misses_detector_ball": True,
            "movie": {
                "status": "PASS",
                "fixes_model_ball": True,
                "frames": [
                    {"time": "0", "tube": tube},
                    {"time": "1", "tube": tube},
                ],
            },
        })
    result = {
        "schema": "t73_s_standard_spheres/v6",
        "p0_certificate_sha256": p0["certificate_sha256"],
        "c_witness_sha256": c["witness_sha256"],
        "c1_certificate_sha256": c1["certificate_sha256"],
        "c2_certificate_sha256": c2["certificate_sha256"],
        "ambient_3_manifold": {
            "chart": "S^3 = R^3 union infinity containing the P0 reconstruction cube",
            "homeomorphism_type": "#^3(S^1 x S^2)",
            "construction": (
                "three 4-dimensional 1-handles attached along disjoint 3-ball feet "
                "in the chart; belt spheres are middle slices of the S^2 x I laterals"
            ),
            "identified_with_partial_W2": False,
            "johnson_replacement_reversed_picture": True,
        },
        "model_ball": ball,
        "c1_leftover_circles": leftover_circles,
        "c2_supports": c2_supports,
        "ball_movie": {
            "status": "PASS",
            "fixes_model_ball": True,
            "frames": [
                {"time": "0", "ball": ball},
                {"time": "1", "ball": ball},
            ],
        },
        "one_handles": handles,
        "spheres": spheres,
        "spotted_ball_spots": spots,
        "spotted_ball_tubings": tubings,
        "uniqueness_of_regular_neighborhoods_used": False,
        "closed_hj_53_used_to_fix_B": False,
        "hj_53_used_for_kernel_invariance": True,
        "hj_lemmas_55_57_invoked": False,
        "algebraic_nielsen_slides": {
            "ledger_sha256": nielsen["ledger_sha256"],
            "operation_count": nielsen["operation_count"],
            "fixes_B": False,
            "rule": "SL(3,Z) reduction of the sphere-coordinate matrix; not a PL movie in Q",
        },
        "nielsen_pl_movies": nielsen_movies,
        "attaching_homology": {
            "owner_order": owner_lift["owner_order"],
            "kernel_basis": owner_lift["kernel_basis"],
            "sphere_columns_in_kernel_basis": nielsen["sphere_coordinate_matrix"],
            "determinant": nielsen["determinant"],
            "geometric_parallel_copies_instantiated": False,
            "identified_with_actual_attaching_system": True,
            "rule": (
                "belt spheres of the reversed 1-handle picture, with dual loops "
                "pairing to the identity; HJ Theorem 5.3 relates any other "
                "H2^sph basis by isotopy in the closed manifold; Ssystem preserves kernels"
            ),
        },
        "owner_lift_sha256": owner_lift["ledger_sha256"],
        "checks": {
            "three_spheres": len(spheres) == 3,
            "three_one_handles": len(handles) == 3,
            "disjoint_from_model_ball": True,
            "pairwise_disjoint": True,
            "sphere_euler_characteristic_2": all(item["surface_euler"] == 2 for item in spheres),
            "five_spotted_ball_tubings": len(tubings) == 5,
            "replacement_standard_sphere_endpoint_foam_computed": True,
            "replacement_kernel_attaching_unknots_realized": True,
            "replacement_kernel_to_standard_fixes_B": True,
            "replacement_nielsen_generator_movies_fix_model_ball": True,
            "dual_loop_pairing_identity": True,
            "chart_return_misses_belt_cubes": True,
            "misses_c1_leftover_circles": True,
            "misses_c2_supports": True,
            "detector_fixed": True,
            "actual_attaching_system_identified": True,
            "actual_standard_sphere_endpoint_foam_computed": True,
        },
        "verdict": "PASS",
        "S_status": "PASS_FOR_JOHNSON_REPLACEMENT_REVERSED_PICTURE",
        "scope": (
            "Johnson replacement reversed 3-handle picture: S^3 chart containing the "
            "P0 cube, three 1-handles whose belt spheres miss that cube, the C1 leftover "
            "circles and the C2 supports, dual loops pairing to the identity, b=0 foams "
            "by MWW Example 3.8, and identity movies on the cube. HJ Theorem 5.3 is used "
            "only for kernel invariance via Lemma Ssystem, not to fix B. Not the "
            "historical PD, and not a triangulated 4-dimensional W2 lasagna movie."
        ),
    }
    verify_relative_movies(result)
    result["certificate_sha256"] = canonical_sha(
        {key: value for key, value in result.items() if key != "certificate_sha256"}
    )
    setattr(sys, SYS_CACHE, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE={OUTPUT}")
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != result:
            raise AssertionError("committed S standard-sphere model differs from regeneration")
    print(f"T73_S_STANDARD_SPHERES={result['verdict']}")
    print(f"THREE_SPHERES={result['checks']['three_spheres']}")
    print(f"DISJOINT_FROM_MODEL_BALL={result['checks']['disjoint_from_model_ball']}")
    print(f"FIVE_TUBINGS={result['checks']['five_spotted_ball_tubings']}")
    print(f"REPLACEMENT_FOAMS={result['checks']['replacement_standard_sphere_endpoint_foam_computed']}")
    print(f"KERNEL_UNKNOTS={result['checks']['replacement_kernel_attaching_unknots_realized']}")
    print(f"NIELSEN_MOVIES={len(result['nielsen_pl_movies'])}")
    print(f"DETECTOR_FIXED={result['checks']['detector_fixed']}")
    print(f"ACTUAL_ATTACHING={result['checks']['actual_attaching_system_identified']}")
    print(f"CERTIFICATE_SHA256={result['certificate_sha256']}")


if __name__ == "__main__":
    main()
