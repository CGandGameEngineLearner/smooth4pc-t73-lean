#!/usr/bin/env python3
"""Build disjoint framed overlap mapping cylinders for all x/m1 interfaces."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

from build_t73_x_m1_ejected_band_lanes import affine_image, barycentric, canonical, file_sha, map_segment, point, simplex_chart

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
EJECTION = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"
EJECTION_RECEIPT = ROOT / "audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json"
CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
STUB_RECEIPT = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
MIDDLE_RECEIPT = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
DEFAULT_CACHE = Path("/home/lifesize/.cache/t73_x_m1_ejection_overlap_transitions.jsonl.gz")

sys.set_int_max_str_digits(0)


def canonical_sha(value): return hashlib.sha256(canonical(value).encode()).hexdigest().upper()
def encode(value): return [str(coordinate) for coordinate in value]
def add(left, right): return tuple(left[index] + right[index] for index in range(4))
def scale(factor, value): return tuple(factor * value[index] for index in range(4))


def target_to_local(value, deck=(0, 0, 0)):
    spatial = tuple(value[index] - 4 * deck[index] for index in range(3))
    return (-spatial[0], spatial[1], spatial[2] - 4, Fraction(1))


def map_point(value, charts, targets):
    candidates = [chart for chart in charts if all(weight >= 0 for weight in barycentric(chart, value))]
    if not candidates: raise AssertionError("overlap point is outside cubical product collar")
    return affine_image(candidates[0], targets, value)


def cube_template():
    vertices = [(a, f, t) for t in (0, 1) for f in (0, 1) for a in (0, 1)]
    tetrahedra = []
    for permutation in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)):
        state = [0, 0, 0]; simplex = [0]
        for axis in permutation:
            state[axis] = 1; a, f, t = state; simplex.append(4 * t + 2 * f + a)
        tetrahedra.append(simplex)
    return vertices, tetrahedra


def build(cache_path):
    product = json.loads(PRODUCT.read_text(encoding="utf-8")); foliation = json.loads(FOLIATION.read_text(encoding="utf-8")); ejection = json.loads(EJECTION.read_text(encoding="utf-8")); ejection_receipt = json.loads(EJECTION_RECEIPT.read_text(encoding="utf-8")); cancellation = json.loads(CANCELLATION.read_text(encoding="utf-8")); stubs = json.loads(STUB_RECEIPT.read_text(encoding="utf-8")); middles = json.loads(MIDDLE_RECEIPT.read_text(encoding="utf-8"))
    base = [point(value) for value in foliation["base_vertices"]]; normals = [point(value) for value in foliation["unit_normal_field"]]; displacement = point(ejection["outward_displacement"]); uniform = point(product["exteriorized_uniform_push_vector"])
    source_vertices = [point(value) for value in product["source_vertices"]]; targets = [point(value) for value in product["target_vertex_images"]]; charts = [simplex_chart(source_vertices, simplex) for simplex in product["four_simplices"]]
    half_width = Fraction(1, 4); template_vertices, template_tetrahedra = cube_template(); cache_path.parent.mkdir(parents=True, exist_ok=True)
    header = {"record": "header", "schema": "t73_x_m1_ejection_overlap_transitions/v1", "product_extension_sha256": product["sha256"], "foliation_sha256": foliation["sha256"], "ambient_ejection_sha256": ejection["sha256"], "ambient_ejection_receipt_sha256": ejection_receipt["sha256"], "stub_receipt_sha256": stubs["sha256"], "middle_receipt_sha256": middles["sha256"], "support_half_width": str(half_width), "mapping_cylinder_vertices": [list(value) for value in template_vertices], "mapping_cylinder_tetrahedra": template_tetrahedra}
    digest = hashlib.sha256(); counts = Counter(); interface_count = local_image_segments = 0
    with cache_path.open("wb") as raw_output, gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
        raw = (canonical(header) + "\n").encode(); output.write(raw); digest.update(raw)
        for band in cancellation["slide_bands"]:
            index = band["index"]; level = Fraction(20 * (index + 1)); orientation = band["replacement_orientation"]; deck = (-1, 0, 1) if orientation == 1 else (1, 0, -1)
            for side in ("first", "last"):
                base_index = (4 if orientation == 1 else 2) if side == "first" else (2 if orientation == 1 else 4)
                side_deck = (0, 0, 0) if side == "first" else deck
                support = (level - half_width, level + half_width); global_core = []; global_push = []; local_source_core = []; local_source_push = []
                for support_level in support:
                    value = add(base[base_index], scale(support_level, normals[base_index])); value = tuple(value[axis] + (4 * side_deck[axis] if axis < 3 else 0) for axis in range(4))
                    global_core.append(add(value, displacement)); global_push.append(add(add(value, normals[base_index]), displacement))
                    local = target_to_local(value, side_deck); local_source_core.append(local); local_source_push.append(add(local, uniform))
                local_core_pieces = map_segment(*local_source_core, charts, targets); local_push_pieces = map_segment(*local_source_push, charts, targets)
                center_value = add(base[base_index], scale(level, normals[base_index])); center_value = tuple(center_value[axis] + (4 * side_deck[axis] if axis < 3 else 0) for axis in range(4)); center_local = target_to_local(center_value, side_deck)
                record = {"record": "framed_overlap_transition", "band_index": index, "component": band["component"], "side": side, "orientation": orientation, "parallel_level": int(level), "support_level_interval": [str(value) for value in support], "base_vertex_index": base_index, "closing_deck_removed": list(side_deck), "global_annulus_boundary": {"core_vertices": [encode(value) for value in global_core], "product_push_vertices": [encode(value) for value in global_push], "center_core": encode(add(center_value, displacement)), "center_push": encode(add(add(center_value, normals[base_index]), displacement))}, "local_cubical_boundary": {"source_core_vertices": [encode(value) for value in local_source_core], "source_uniform_push_vertices": [encode(value) for value in local_source_push], "target_core_pieces": local_core_pieces, "target_uniform_push_pieces": local_push_pieces, "center_core": encode(map_point(center_local, charts, targets)), "center_push": encode(map_point(add(center_local, uniform), charts, targets))}, "mapping_cylinder_template": "header/mapping_cylinder", "core_transition_count": 1, "push_transition_count": 1}
                raw = (canonical(record) + "\n").encode(); output.write(raw); digest.update(raw); counts[band["component"]] += 1; interface_count += 1; local_image_segments += len(local_core_pieces) + len(local_push_pieces)
    receipt = {"schema": "t73_x_m1_ejection_overlap_transitions_receipt/v1", "cache_path": str(cache_path), "cache_size": cache_path.stat().st_size, "cache_sha256": file_sha(cache_path), "record_stream_sha256": digest.hexdigest().upper(), "builder_sha256": file_sha(Path(__file__)), "product_extension_sha256": product["sha256"], "foliation_sha256": foliation["sha256"], "ambient_ejection_sha256": ejection["sha256"], "ambient_ejection_receipt_sha256": ejection_receipt["sha256"], "stub_receipt_sha256": stubs["sha256"], "middle_receipt_sha256": middles["sha256"], "interface_count": interface_count, "core_transition_count": interface_count, "push_transition_count": interface_count, "component_interface_counts": dict(sorted(counts.items())), "local_boundary_piece_count": local_image_segments, "mapping_cylinder_tetrahedra_per_interface": 6, "total_mapping_cylinder_tetrahedra": 6 * interface_count, "verdict": "PASS_X_M1_FRAMED_OVERLAP_TRANSITION_CELLS_CONSTRUCTED", "scope_boundary": "transition cells and disjoint level supports constructed; boundary-center equality against F-591/F-594 caches requires independent full verification"}
    receipt["sha256"] = canonical_sha(receipt); OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"); return receipt


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); args = parser.parse_args(); receipt = build(args.output or Path(os.environ.get("T73_X_M1_OVERLAP_CACHE", DEFAULT_CACHE))); print(json.dumps({"verdict": receipt["verdict"], "interfaces": receipt["interface_count"], "tetrahedra": receipt["total_mapping_cylinder_tetrahedra"], "bytes": receipt["cache_size"]}, sort_keys=True))


if __name__ == "__main__": main()
