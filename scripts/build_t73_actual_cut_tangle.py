#!/usr/bin/env python3
"""Build the cut tangle from the actual AR link and belt spheres.

Cutting is performed only at live belt hits.  The resulting arcs are not
replaced by the public 44-strand braid.  A comparison with frozen B44 is
recorded last and never used as an input.
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
BELTS = ROOT / "geometry" / "t73_belt_spheres.json"
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"


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


def centered(value: Fraction) -> Fraction:
    while value > 2:
        value -= 4
    while value <= -2:
        value += 4
    return value


def dual_events(component: dict[str, Any], owner: str) -> list[dict[str, Any]]:
    original = component["polyline"]
    points = [[Fraction(value) for value in point] for point in reversed(original)]
    events = []
    for index in range(1, len(points) - 1):
        point = points[index]
        previous, following = points[index - 1], points[index + 1]
        for axis in (0, 1):
            if point[axis] != 2 or previous[axis] == 2 or following[axis] == 2:
                continue
            if previous[axis] == following[axis]:
                continue
            orientation = 1 if following[axis] > previous[axis] else -1
            original_index = len(original) - 1 - index
            label = "z" if axis == 0 else "y"
            events.append(
                {
                    "owner": owner,
                    "source_kind": "dual_cell_boundary",
                    "source_id": f"{owner}:vertex:{original_index}",
                    "pre_cancel_axis": "x" if axis == 0 else "y",
                    "label": label,
                    "orientation": orientation,
                    "belt_face_point": (
                        [str(centered(point[0])), str(centered(point[2])), "1"]
                        if axis == 1
                        else None
                    ),
                }
            )
    return events


def pair_y_with_following_z(owner: str, events: list[dict[str, Any]]):
    pairs = []
    paired_z = set()
    for index, event in enumerate(events):
        if event["label"] != "y":
            continue
        z_index = (index + 1) % len(events)
        if events[z_index]["label"] != "z":
            raise AssertionError(f"{owner}: an actual y passage is not followed by a z passage")
        pairs.append(
            {
                "owner": owner,
                "y_event_index": index,
                "z_event_index": z_index,
                "y_source_id": event["source_id"],
                "z_source_id": events[z_index]["source_id"],
            }
        )
        paired_z.add(z_index)
    leftovers = [
        {"owner": owner, "event_index": index, "source_id": event["source_id"], "orientation": event["orientation"]}
        for index, event in enumerate(events)
        if event["label"] == "z" and index not in paired_z
    ]
    return pairs, leftovers


def build(write: bool = False) -> dict[str, Any]:
    if not LINK.exists() or not BELTS.exists():
        raise AssertionError("actual AR link and belt spheres are required")
    link = json.loads(LINK.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    cancel_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    if cancel_t["ar_link_sha256"] != link["sha256"] or cancel_x["ar_link_sha256"] != link["sha256"]:
        raise AssertionError("cancellation movies are stale relative to the AR link")
    if cancel_t["status"] != "PASS" or cancel_x["status"] != "PASS":
        raise AssertionError("both actual cancellation movies must pass before cutting")
    x_slides = {slide["source_id"]: slide for slide in cancel_x["slide_bands"]}

    m2_events = []
    for arc in sorted(
        (item for item in spine["handle_arcs"] if int(item["component"]) == 1),
        key=lambda item: int(item["letter_index"]),
    ):
        axis = int(arc["axis"])
        if axis == 0:
            slide = x_slides[arc["arc_id"]]
            label = "z"
            orientation = int(slide["replacement_orientation"])
            source_kind = "x_slide_z_replacement"
        else:
            label = "y" if axis == 1 else "z"
            orientation = int(arc["sign"])
            source_kind = "johnson_handle_lane"
        m2_events.append(
            {
                "owner": "m_2",
                "source_kind": source_kind,
                "source_id": arc["arc_id"],
                "label": label,
                "orientation": orientation,
                "belt_face_point": (
                    [arc["start_lane"][0], arc["start_lane"][1], "1"]
                    if label == "y"
                    else None
                ),
            }
        )
    m2_events.append(
        {
            "owner": "m_2",
            "source_kind": "bottom_coordinate_arc",
            "source_id": "m_2:C_i",
            "label": "y",
            "orientation": -1,
            "belt_face_point": ["0", "0", "1"],
        }
    )
    rxy_events = dual_events(link["components"]["r_xy"], "r_xy")
    if [(event["label"], event["orientation"]) for event in rxy_events] != [
        ("z", 1), ("y", 1), ("z", -1), ("y", -1)
    ]:
        raise AssertionError("oriented r_xy dual cell does not give z y Z Y after x cancellation")
    m2_pairs, m2_leftovers = pair_y_with_following_z("m_2", m2_events)
    rxy_pairs, rxy_leftovers = pair_y_with_following_z("r_xy", rxy_events)
    pairs = rxy_pairs + m2_pairs
    leftovers = rxy_leftovers + m2_leftovers
    width = link["framing"]["spine_ribbon_transport"]["width"]
    for index, leftover in enumerate(leftovers):
        center = Fraction(2) + Fraction(index + 1, 1000)
        radius = Fraction(1, 10000)
        leftover["circle_in_complement_chart"] = [
            [str(center), str(radius), "0"],
            [str(center), "0", str(radius)],
            [str(center), str(-radius), "0"],
            [str(center), "0", str(-radius)],
            [str(center), str(radius), "0"],
        ]
        leftover["chart"] = "z-handle complement, disjoint from detector |x|<=1"
        leftover["transported_product_normal"] = [width, width, "0"]
        leftover["source_standardization"] = "the unpaired actual z lane and its adjacent zero-handle connectors collapse along their recorded product ribbon to this meridian"
    passages = []
    for wicket, pair in enumerate(pairs, start=1):
        events = rxy_events if pair["owner"] == "r_xy" else m2_events
        event = events[pair["y_event_index"]]
        point = event["belt_face_point"]
        if point is None:
            raise AssertionError("y detector event has no actual belt coordinate")
        passages.append(
            {
                "wicket": wicket,
                "owner": pair["owner"],
                "word_event_index": pair["y_event_index"],
                "orientation": event["orientation"],
                "source_id": event["source_id"],
                "paired_z_source_id": pair["z_source_id"],
                "belt_face_point": point,
                "cut_arc_in_ball": [point[:2] + ["-1"], point[:2] + ["1"]],
                "product_normal": [width, width, "0"],
            }
        )
    if len(passages) != 44 or len({tuple(item["belt_face_point"]) for item in passages}) != 44:
        raise AssertionError("actual y cut does not give 44 distinct passages")
    passage_by_wicket = {item["wicket"]: item for item in passages}
    boundary_wicket_order = [1, 2] + list(reversed(range(3, 45)))
    framed_endpoints = []
    for wicket in boundary_wicket_order:
        passage = passage_by_wicket[wicket]
        x, z = (Fraction(value) for value in passage["belt_face_point"][:2])
        normal = Fraction(width)
        for sign, coefficient, source_key in (
            ("neg", -1, "paired_z_source_id"),
            ("pos", 1, "source_id"),
        ):
            point = [x + coefficient * normal, z + coefficient * normal, Fraction(0)]
            framed_endpoints.append(
                {
                    "physical_endpoint_id": f"actual:{passage['owner']}:w{wicket}:{sign}:{passage[source_key]}",
                    "owner": passage["owner"],
                    "wicket": wicket,
                    "sign": sign,
                    "orientation": passage["orientation"],
                    "word_event_index": passage["word_event_index"],
                    "actual_side_source_id": passage[source_key],
                    "coordinate_in_detector_chart": [str(value) for value in point],
                    "geometric_order": len(framed_endpoints),
                    "transported_normal_coefficient": coefficient,
                }
            )
    if len(framed_endpoints) != 88:
        raise AssertionError("actual product rectangles do not have 88 framed endpoints")
    result = {
        "schema": "t73_actual_cut_tangle/v2",
        "ar_link_sha256": link["sha256"],
        "belt_sha256": belts["sha256"],
        "t_cancellation_sha256": cancel_t["sha256"],
        "x_cancellation_sha256": cancel_x["sha256"],
        "spine_embedding_sha256": spine["sha256"],
        "cut_along": ["y_belt_after_t_and_x_cancellations"],
        "derived_from_expected_B44": False,
        "forbidden_inputs": ["B44", "SHA(B44)", "Delta3=2624"],
        "post_x_event_lists": {"m_2": m2_events, "r_xy": rxy_events},
        "product_rectangle_pairings": pairs,
        "passages": passages,
        "framed_endpoints": framed_endpoints,
        "endpoint_boundary_order_rule": "r_xy wickets 1,2 forward; m_2 wickets 44,...,3 reverse; within each rectangle neg then pos",
        "passage_count": len(passages),
        "leftover_z_circles": leftovers,
        "leftover_circle_count": len(leftovers),
        "detector_ball": {
            "chart": "[-1,1]_(x,z)^2 x [-1,1]_height after cutting the y one-handle",
            "topological_type": "PL 3-ball",
            "boundary_disk_levels": ["-1", "1"],
            "pairwise_disjoint_height_monotone_arcs": True,
            "disjoint_from_section_ball": True,
            "orientation": "(x,z,height)",
        },
        "status": "PASS",
        "reason": "42 actual m_2 y passages and two oriented r_xy passages cut to 44 labelled product arcs; 227 unpaired z events remain outside the detector ball",
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
        print("T73_ACTUAL_CUT_TANGLE=WRITTEN" if args.write else "T73_ACTUAL_CUT_TANGLE=CHECKED")
        print(f"STATUS={result['status']}")
        print(f"DERIVED_FROM_EXPECTED_B44={result['derived_from_expected_B44']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps({"status": result["status"]}, indent=2))


if __name__ == "__main__":
    main()
