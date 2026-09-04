#!/usr/bin/env python3
"""Route the shrunken Johnson mismatch balls through disjoint PL lanes."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MISMATCH = ROOT / "geometry" / "t73_johnson_arm_mismatch.json"
SHRINKS = ROOT / "geometry" / "t73_johnson_ball_shrinks.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_ball_exchange_routes.json"
SUPPORT_SCALE = Fraction(3, 8)
DETOUR = Fraction(1)


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def decode(values):
    return [Fraction(value) for value in values]


def encode(values):
    return [str(value) for value in values]


def component_by_id(template, component_id):
    matches = [item for item in template["components"] if item["component_id"] == component_id]
    if len(matches) != 1:
        raise AssertionError("component id is not unique")
    return matches[0]


def support_offsets(component):
    center = decode(component["triangulation"]["star_center"])
    box = component["triangulation"]["lift_bounding_box"]
    low = decode(box["min"])
    high = decode(box["max"])
    return (
        [SUPPORT_SCALE * (low[axis] - center[axis]) for axis in range(3)],
        [SUPPORT_SCALE * (high[axis] - center[axis]) for axis in range(3)],
    )


def translated(point, vector, coefficient=Fraction(1)):
    return [point[axis] + coefficient * vector[axis] for axis in range(3)]


def path_for(center, prefix, detour_axis, detour_sign, forward):
    along = [Fraction(0), Fraction(0), Fraction(0)]
    along[prefix] = 2 if forward else -2
    detour = [Fraction(0), Fraction(0), Fraction(0)]
    detour[detour_axis] = detour_sign
    return [
        list(center),
        translated(center, detour),
        translated(translated(center, detour), along),
        translated(center, along),
    ]


def swept_box(route, phase, offsets):
    first = route[phase]
    second = route[phase + 1]
    low_offset, high_offset = offsets
    return (
        [min(first[axis], second[axis]) + low_offset[axis] for axis in range(3)],
        [max(first[axis], second[axis]) + high_offset[axis] for axis in range(3)],
    )


def boxes_overlap_interior(first, second):
    return all(
        max(first[0][axis], second[0][axis]) < min(first[1][axis], second[1][axis])
        for axis in range(3)
    )


def periodic_boxes_overlap(first, second):
    for shift in itertools.product((-4, 0, 4), repeat=3):
        shifted = (
            [second[0][axis] + shift[axis] for axis in range(3)],
            [second[1][axis] + shift[axis] for axis in range(3)],
        )
        if boxes_overlap_interior(first, shifted):
            return True
    return False


def protected_box():
    radius = Fraction(1, 196104)
    return ([-radius, -radius, -radius], [radius, radius, radius])


def build_template(template):
    source = template["source_axis"]
    prefix = template["prefix_axis"]
    third = next(axis for axis in range(3) if axis not in (source, prefix))
    routes = []
    for pair in template["ball_pairs"]:
        excess = component_by_id(template, pair["excess_component_id"])
        deficiency = component_by_id(template, pair["deficiency_component_id"])
        center = decode(excess["triangulation"]["star_center"])
        target_center = decode(deficiency["triangulation"]["star_center"])
        expected = list(center)
        delta = (target_center[prefix] - center[prefix]) % 4
        if delta != 2:
            raise AssertionError("paired star centers are not half a period apart")
        expected[prefix] += 2
        target_center = expected
        if pair["piece_count"] == max(item["piece_count"] for item in template["ball_pairs"]):
            detour_axis = third
            detour_sign = Fraction(1)
        else:
            detour_axis = source
            residue = center[source] % 4
            detour_sign = Fraction(-1) if residue < 2 else Fraction(1)
        forward = path_for(center, prefix, detour_axis, detour_sign, True)
        backward = path_for(target_center, prefix, detour_axis, -detour_sign, False)
        routes.extend(
            [
                {
                    "ball_id": f"pair-{pair['pair_id']}:excess",
                    "pair_id": pair["pair_id"],
                    "component_id": excess["component_id"],
                    "source_owner": 0,
                    "support_offsets": [encode(part) for part in support_offsets(excess)],
                    "path": [encode(point) for point in forward],
                },
                {
                    "ball_id": f"pair-{pair['pair_id']}:deficiency",
                    "pair_id": pair["pair_id"],
                    "component_id": deficiency["component_id"],
                    "source_owner": 1,
                    "support_offsets": [encode(part) for part in support_offsets(deficiency)],
                    "path": [encode(point) for point in backward],
                },
            ]
        )
    phase_checks = []
    protection = protected_box()
    for phase in range(3):
        boxes = {
            route["ball_id"]: swept_box(
                [decode(point) for point in route["path"]],
                phase,
                tuple(decode(part) for part in route["support_offsets"]),
            )
            for route in routes
        }
        collisions = []
        for first, second in itertools.combinations(routes, 2):
            if periodic_boxes_overlap(boxes[first["ball_id"]], boxes[second["ball_id"]]):
                collisions.append([first["ball_id"], second["ball_id"]])
        protected_hits = [
            route["ball_id"]
            for route in routes
            if periodic_boxes_overlap(boxes[route["ball_id"]], protection)
        ]
        phase_checks.append(
            {
                "phase": phase,
                "support_interiors_disjoint": not collisions,
                "collisions": collisions,
                "protected_ball_disjoint": not protected_hits,
                "protected_hits": protected_hits,
                "swept_boxes": {
                    key: [encode(part) for part in box] for key, box in boxes.items()
                },
            }
        )
    passed = all(
        phase["support_interiors_disjoint"] and phase["protected_ball_disjoint"]
        for phase in phase_checks
    )
    return {
        "source_axis": source,
        "prefix_axis": prefix,
        "power": template["power"],
        "support_scale": str(SUPPORT_SCALE),
        "route_count": len(routes),
        "routes": routes,
        "phase_checks": phase_checks,
        "disjoint_exchange_routes": "PASS" if passed else "OPEN",
        "translation_cell_status": "OPEN",
    }


def generate():
    mismatch = json.loads(MISMATCH.read_text(encoding="utf-8"))
    shrinks = json.loads(SHRINKS.read_text(encoding="utf-8"))
    if shrinks["mismatch_sha256"] != mismatch["sha256"]:
        raise AssertionError("ball shrinks are not bound to the mismatch decomposition")
    templates = [build_template(template) for template in mismatch["templates"]]
    result = {
        "schema": "t73_johnson_ball_exchange_routes/v1",
        "mismatch_sha256": mismatch["sha256"],
        "shrinks_sha256": shrinks["sha256"],
        "support_scale": str(SUPPORT_SCALE),
        "templates": templates,
        "all_routes_disjoint": all(
            template["disjoint_exchange_routes"] == "PASS" for template in templates
        ),
        "ball_exchange_status": "OPEN: routes are certified but compact translation cells are not yet attached",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check or args.write:
        print(f"T73_JOHNSON_EXCHANGE_ROUTES={'PASS' if result['all_routes_disjoint'] else 'OPEN'}")
        print(f"BALL_EXCHANGE={result['ball_exchange_status']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
