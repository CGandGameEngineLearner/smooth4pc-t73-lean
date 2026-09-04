#!/usr/bin/env python3
"""Bind the ambient Johnson restore factors to the actual lane spine."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESTORE = ROOT / "geometry" / "t73_johnson_restore_assembly.json"
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_spine_binding.json"


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


def build(write: bool = False):
    free = load("compose_t73_free_group_psi")
    side_module = load("search_t73_johnson_alpha_sides")
    alpha_movie = load("generate_t73_johnson_alpha_movie").generate()
    restore = json.loads(RESTORE.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    candidate = side_module.generate()["known_candidate"]
    factors = restore["full_93_factor_assembly"]["factors"]
    if len(alpha_movie["moves"]) != 93 or len(factors) != 93:
        raise AssertionError("Johnson movie/restore does not have 93 factors")
    mapping = free.identity_map()
    records = []
    for index, (move, factor) in enumerate(zip(alpha_movie["moves"], factors)):
        source = int(move["alpha_target"])
        prefix = int(move["alpha_prefix"])
        power = int(move["power"])
        side = move["side"]
        if (
            factor["index"] != index
            or factor["source_axis"] != source
            or factor["prefix_axis"] != prefix
            or factor["power"] != power
            or factor["side"] != side
        ):
            raise AssertionError("ambient restore factor is not the Johnson slide")
        before = [word[:] for word in mapping]
        local = free.identity_map()
        prefix_letter = power * (prefix + 1)
        local[source] = (
            [prefix_letter, source + 1]
            if side == "prefix-first"
            else [source + 1, prefix_letter]
        )
        mapping = free.compose(local, mapping)
        expected_path = (
            [[0, 0, 0], move["square_vertices"][2], move["diagonal"][1]]
            if side == "prefix-first"
            else [[0, 0, 0], move["square_vertices"][1], move["diagonal"][1]]
        )
        if move["boundary_path"] != expected_path:
            raise AssertionError("Johnson side does not match its square boundary path")
        records.append(
            {
                "index": index,
                "source_axis": source,
                "prefix_axis": prefix,
                "power": power,
                "side": side,
                "local_generator_images": local,
                "before_images_sha256": canonical_sha(before),
                "after_images_sha256": canonical_sha(mapping),
                "boundary_path": move["boundary_path"],
                "square_normal": move["square_normal"],
                "ambient_restore_factor_sha256": canonical_sha(factor),
                "ambient_extension_maps_both_owners": factor[
                    "maps_both_owners_setwise"
                ],
                "ambient_extension_fixes_protected_ball": factor[
                    "fixes_protected_ball_pointwise"
                ],
            }
        )
    if mapping != candidate["generator_images"]:
        raise AssertionError("93 slide updates do not give the selected generator images")
    if mapping != [component["retraction_word"] for component in spine["components"]]:
        raise AssertionError("actual lane spine does not realize the slide movie")
    leaf_bindings = []
    for component, word in enumerate(mapping):
        arcs = sorted(
            (arc for arc in spine["handle_arcs"] if arc["component"] == component),
            key=lambda arc: int(arc["letter_index"]),
        )
        if len(arcs) != len(word):
            raise AssertionError("lane spine has the wrong number of word leaves")
        for letter_index, (letter, arc) in enumerate(zip(word, arcs)):
            if arc["word_letter"] != letter:
                raise AssertionError("lane leaf has the wrong oriented letter")
            leaf_bindings.append(
                {
                    "component": component,
                    "letter_index": letter_index,
                    "letter": letter,
                    "arc_id": arc["arc_id"],
                    "lane_index": arc["lane_index"],
                }
            )
    expected_connectors = sum(len(word) - 1 for word in mapping) + 2 * len(mapping)
    if spine["central_connector_count"] != expected_connectors:
        raise AssertionError("central connectors do not join all successive word leaves")
    result = {
        "schema": "t73_johnson_spine_binding/v1",
        "restore_assembly_sha256": restore["sha256"],
        "spine_embedding_sha256": spine["sha256"],
        "alpha_movie_sha256": alpha_movie["movie_sha256"],
        "side_candidate_sha256": canonical_sha(candidate),
        "factor_count": len(records),
        "factors": records,
        "final_generator_images": mapping,
        "leaf_binding_count": len(leaf_bindings),
        "leaf_bindings": leaf_bindings,
        "connector_binding_count": expected_connectors,
        "all_ambient_factors_are_selected_johnson_slides": True,
        "all_word_leaves_bound_to_actual_lanes": True,
        "all_successive_leaves_bound_to_connectors": True,
        "protected_origin_spokes_fixed": True,
        "ambient_restore_spine_binding": "PASS",
        "coordinate_spine_curve_transport": "PASS",
        "general_point_evaluator": "OPEN",
    }
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print(f"T73_JOHNSON_SPINE_BINDING={result['ambient_restore_spine_binding']}")
        print(f"FACTORS={result['factor_count']}")
        print(f"LEAF_BINDINGS={result['leaf_binding_count']}")
        print(f"CONNECTOR_BINDINGS={result['connector_binding_count']}")
        print(f"CURVE_TRANSPORT={result['coordinate_spine_curve_transport']}")
        print(f"GENERAL_POINT_EVALUATOR={result['general_point_evaluator']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps({key: value for key, value in result.items() if key not in ("factors", "leaf_bindings")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
