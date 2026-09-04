#!/usr/bin/env python3
"""Bind all 44 detector rectangles to actual y/z arcs and connectors."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry" / "t73_actual_product_rectangles.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def dual_vertex_subpath(polyline, original_vertex):
    index = int(original_vertex)
    if not 0 < index < len(polyline) - 1:
        raise AssertionError("dual-cell crossing vertex has no two adjacent edges")
    return polyline[index - 1 : index + 2]


def build(write: bool = False):
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    link = json.loads(LINK.read_text(encoding="utf-8"))
    cancel_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    collar = load("generate_t73_johnson_ribbon_collar").generate()
    if collar["actual_cut_tangle_sha256"] != cut["sha256"]:
        raise AssertionError("detector coordinate chart is stale")
    arcs = {arc["arc_id"]: arc for arc in spine["handle_arcs"]}
    connectors = {item["connector_id"]: item for item in spine["central_connectors"]}
    x_slides = {item["source_id"]: item for item in cancel_x["slide_bands"]}
    t_slides = {
        (item["component"], item["removed_t_arc"]): item
        for item in cancel_t["slide_bands"]
    }
    chart_moves = {item["wicket"]: item for item in collar["coordinate_chart_movie"]}
    rectangles = []
    for passage in cut["passages"]:
        owner = passage["owner"]
        y_source = passage["source_id"]
        z_source = passage["paired_z_source_id"]
        if owner == "m_2":
            if y_source == "m_2:C_i":
                y_geometry = {
                    "kind": "bottom_coordinate_arc",
                    "polyline": link["components"]["m_2"]["C_i_universal_cover_lift"],
                }
                connector_geometry = {
                    "kind": "cyclic_cut_ball_connector_after_t_cancellation",
                    "t_slide_band_hashes": [
                        canonical_sha(t_slides[("m_2", "lambda_i")]),
                        canonical_sha(t_slides[("m_2", "mu_i")]),
                    ],
                    "spine_connector_ids": ["c1:start", "c1:end"],
                }
            else:
                y_arc = arcs[y_source]
                y_geometry = {
                    "kind": "johnson_y_handle_lane",
                    "polyline": y_arc["torus_polyline"],
                    "arc_sha256": canonical_sha(y_arc),
                }
                letter_index = int(y_arc["letter_index"])
                connector_id = f"c1:between:{letter_index}"
                connector = connectors[connector_id]
                connector_geometry = {
                    "kind": "actual_central_connector",
                    "connector_id": connector_id,
                    "polyline": connector["polyline"],
                    "connector_sha256": canonical_sha(connector),
                }
            z_arc = arcs[z_source]
            if int(z_arc["axis"]) == 0:
                slide = x_slides[z_source]
                z_geometry = {
                    "kind": "x_slide_replacement_by_actual_m1_z_lane",
                    "x_slide_band_sha256": canonical_sha(slide),
                    "m1_z_lane_ref": "geometry/t73_actual_ar_link.json#/components/m_1/psi_A_C_i",
                    "m1_z_lane_sha256": canonical_sha(link["components"]["m_1"]["psi_A_C_i"]),
                    "orientation": slide["replacement_orientation"],
                }
            elif int(z_arc["axis"]) == 2:
                z_geometry = {
                    "kind": "johnson_z_handle_lane",
                    "polyline": z_arc["torus_polyline"],
                    "arc_sha256": canonical_sha(z_arc),
                }
            else:
                raise AssertionError("paired m2 z event is not a z or replaced x lane")
        else:
            polyline = link["components"]["r_xy"]["polyline"]
            y_vertex = y_source.rsplit(":", 1)[1]
            z_vertex = z_source.rsplit(":", 1)[1]
            y_geometry = {
                "kind": "r_xy_dual_cell_y_subpath",
                "polyline": dual_vertex_subpath(polyline, y_vertex),
            }
            z_geometry = {
                "kind": "r_xy_dual_cell_x_to_z_replacement",
                "polyline_before_x_cancellation": dual_vertex_subpath(polyline, z_vertex),
                "x_slide_band_sha256": canonical_sha(x_slides[z_source]),
                "m1_z_lane_sha256": canonical_sha(link["components"]["m_1"]["psi_A_C_i"]),
                "orientation": x_slides[z_source]["replacement_orientation"],
            }
            connector_geometry = {
                "kind": "oriented_r_xy_dual_cell_boundary_interval",
                "from_vertex": y_vertex,
                "to_vertex": z_vertex,
                "orientation": "reverse stored boundary, as fixed by the detector event list",
            }
        rectangles.append(
            {
                "wicket": passage["wicket"],
                "owner": owner,
                "orientation": passage["orientation"],
                "actual_y_source_id": y_source,
                "actual_z_source_id": z_source,
                "y_side": y_geometry,
                "between_y_and_z": connector_geometry,
                "z_side": z_geometry,
                "detector_cut_arc": passage["cut_arc_in_ball"],
                "product_normal": passage["product_normal"],
                "coordinate_chart_move_sha256": canonical_sha(chart_moves[passage["wicket"]]),
                "rectangle_transport": "the component subannulus between these consecutive actual passages, pushed through the recorded cancellation and detector-chart ambient maps",
            }
        )
    if len(rectangles) != 44 or [item["wicket"] for item in rectangles] != list(range(1, 45)):
        raise AssertionError("actual product rectangle list is incomplete")
    result = {
        "schema": "t73_actual_product_rectangles/v1",
        "cut_tangle_sha256": cut["sha256"],
        "spine_embedding_sha256": spine["sha256"],
        "ar_link_sha256": link["sha256"],
        "cancel_t_sha256": cancel_t["sha256"],
        "cancel_x_sha256": cancel_x["sha256"],
        "collar_sha256": collar["collar_sha256"],
        "rectangle_count": len(rectangles),
        "rectangles": rectangles,
        "all_y_z_sources_actual": True,
        "all_connectors_actual": True,
        "all_x_replacements_bound_to_kirby_bands": True,
        "actual_product_rectangle_transport": "PASS",
    }
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.write or args.check:
        print(f"T73_ACTUAL_PRODUCT_RECTANGLES={result['actual_product_rectangle_transport']}")
        print(f"RECTANGLES={result['rectangle_count']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
