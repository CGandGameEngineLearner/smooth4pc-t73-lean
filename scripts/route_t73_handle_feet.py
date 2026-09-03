#!/usr/bin/env python3
"""Route standard Nielsen support exits to the AR coordinate handle feet."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOUND = 7  # coordinates are divided by four; stay inside (-2,2)^3


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def protected(point: tuple[int, int, int]) -> bool:
    # In coordinates divided by four, max-min <= 1 is an L-infinity tube of
    # radius 1/8 around the diagonal section arc.
    return max(point) - min(point) <= 1 and max(point) >= -4 and min(point) <= 4


def edge_safe(a: tuple[int, int, int], b: tuple[int, int, int]) -> bool:
    midpoint_doubled = tuple(a[i] + b[i] for i in range(3))
    # At doubled scale, the protected threshold is 2.
    midpoint_safe = max(midpoint_doubled) - min(midpoint_doubled) > 2
    return not protected(a) and not protected(b) and midpoint_safe


def neighbors(point: tuple[int, int, int]):
    for axis in range(3):
        for delta in (-1, 1):
            value = list(point)
            value[axis] += delta
            candidate = tuple(value)
            if all(-BOUND <= x <= BOUND for x in candidate) and edge_safe(point, candidate):
                yield candidate


def bfs(start, goal, forbidden: set[tuple[int, int, int]]):
    queue = collections.deque([start])
    parent = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return list(reversed(path))
        for candidate in neighbors(current):
            if candidate in parent or (candidate in forbidden and candidate != goal):
                continue
            parent[candidate] = current
            queue.append(candidate)
    raise AssertionError(f"no route from {start} to {goal}")


def encode(path):
    return [[f"{x}/4" for x in point] for point in path]


def generate() -> dict[str, Any]:
    placement = load("place_t73_nielsen_supports").generate()
    expanded = load("generate_t73_pl_nielsen_templates").generate()["expanded_moves"]
    exits = {"target": (-1, 6, -6), "source": (1, 6, -6)}
    feet = {0: (-2, -4, -4), 1: (-4, -2, -4), 2: (-4, -4, -2)}
    if any(protected(point) for point in list(exits.values()) + list(feet.values())):
        raise AssertionError("route endpoint lies in the protected section tube")
    pair_routes: dict[str, Any] = {}
    for target in range(3):
        for source in range(3):
            if target == source:
                continue
            target_forbidden = {foot for handle, foot in feet.items() if handle != target}
            target_path = bfs(exits["target"], feet[target], target_forbidden)
            forbidden = set(target_path) | {foot for handle, foot in feet.items() if handle != source}
            source_path = bfs(exits["source"], feet[source], forbidden)
            if set(target_path).intersection(source_path):
                raise AssertionError("target/source handle-foot routes intersect")
            key = f"{target}<-{source}"
            pair_routes[key] = {
                "target_path": encode(target_path),
                "source_path": encode(source_path),
                "target_vertices": len(target_path),
                "source_vertices": len(source_path),
                "node_disjoint": True,
                "protected_section_tube_disjoint": True,
            }
    routed_moves = []
    for index, move in enumerate(expanded):
        if move["kind"] == "unit_slide":
            key = f"{move['target']}<-{move['source']}"
            route = key
        else:
            route = "signed-permutation chart; no band route required"
        routed_moves.append({"index": index, "move": move, "route": route, "time_interval": placement["placements"][index]["time_interval"]})
    result: dict[str, Any] = {
        "schema": "t73_handle_foot_routing/v1",
        "coordinate_scale": 4,
        "protected_section_tube": "L-infinity radius 1/8 around {(t,t,t):-1<=t<=1}",
        "handle_feet": {str(key): [f"{x}/4" for x in value] for key, value in feet.items()},
        "pair_routes": pair_routes,
        "routed_moves": routed_moves,
        "polyline_routing_status": "PASS",
        "thickening_status": "OPEN: route polylines have not yet been thickened to pairwise-disjoint chart embeddings",
    }
    result["routing_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = generate()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check:
        print("T73_HANDLE_FOOT_ROUTING=PASS")
        print(f"ROUTED_MOVES={len(result['routed_moves'])}")
        print(f"POLYLINE_ROUTING_STATUS={result['polyline_routing_status']}")
        print(f"THICKENING_STATUS={result['thickening_status']}")
        print(f"ROUTING_SHA256={result['routing_sha256']}")
    elif not args.output:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
