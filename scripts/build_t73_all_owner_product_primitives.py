#!/usr/bin/env python3
"""Build the all-owner y/z product primitives in the Johnson collar.

Scope is deliberately conditional.  The source arcs are bound to the current
Johnson spine, AR link, and the two explicit cancellation movies.  The output
does not assert that this normalized collar is embedded in the actual
``partial W2``; that is the separate P0 ambient-inclusion obligation.

For ``m_3`` the bottom coordinate Z arc cancels the terminal z arc after the
x-to-z replacement.  For ``r_zx`` both product bigons cancel.  These free
reductions retain their source IDs in ``free_reduction_pairs`` instead of
silently deleting provenance.
"""

from __future__ import annotations

import argparse
import copy
from collections import Counter
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry" / "t73_all_owner_product_primitives.json"

OWNERS = ("m_2", "m_3", "r_xy", "r_yz", "r_zx")
EXPECTED_N_Y = (42, 189, 2, 2, 0)
EXPECTED_N_Z = (269, 1271, 2, 2, 0)
DUAL_AXES = {
    "r_xy": (0, 1),
    "r_yz": (1, 2),
    "r_zx": (2, 0),
}
AXIS_LABEL = {0: "x", 1: "y", 2: "z"}


def load_script(name: str):
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


def oriented_letter(event: dict[str, Any]) -> str:
    label = event["label"]
    return label if int(event["orientation"]) > 0 else label.upper()


def freely_reduce_events(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stack: list[dict[str, Any]] = []
    cancellations: list[dict[str, Any]] = []
    for event in events:
        if (
            stack
            and stack[-1]["label"] == event["label"]
            and int(stack[-1]["orientation"]) == -int(event["orientation"])
        ):
            left = stack.pop()
            cancellations.append(
                {
                    "left_source_id": left["source_id"],
                    "right_source_id": event["source_id"],
                    "letters": [oriented_letter(left), oriented_letter(event)],
                    "geometric_reason": "registered zero-twist product bigon after x-to-z replacement",
                }
            )
        else:
            stack.append(event)
    return stack, cancellations


def spine_events(
    owner: str,
    component: int,
    bottom_label: str,
    spine: dict[str, Any],
    link: dict[str, Any],
    x_slides: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    arcs = sorted(
        (arc for arc in spine["handle_arcs"] if int(arc["component"]) == component),
        key=lambda arc: int(arc["letter_index"]),
    )
    events: list[dict[str, Any]] = []
    for arc in arcs:
        axis = int(arc["axis"])
        source_id = arc["arc_id"]
        geometry: dict[str, Any] = {
            "kind": "johnson_handle_lane",
            "spine_arc_sha256": canonical_sha(arc),
            "torus_polyline": arc["torus_polyline"],
            "original_axis": AXIS_LABEL[axis],
        }
        if axis == 0:
            slide = x_slides[source_id]
            label = "z"
            orientation = int(slide["replacement_orientation"])
            geometry.update(
                {
                    "kind": "x_slide_z_replacement",
                    "x_slide_band_sha256": canonical_sha(slide),
                    "replacement_curve_ref": slide["replacement_curve_ref"],
                    "replacement_orientation": orientation,
                    "relative_twist": int(slide["relative_twist"]),
                }
            )
        else:
            label = "y" if axis == 1 else "z"
            orientation = int(arc["sign"])
        events.append(
            {
                "owner": owner,
                "source_id": source_id,
                "source_order": int(arc["letter_index"]),
                "label": label,
                "orientation": orientation,
                "source_geometry": geometry,
            }
        )
    bottom = link["components"][owner]
    events.append(
        {
            "owner": owner,
            "source_id": f"{owner}:C_i",
            "source_order": len(arcs),
            "label": bottom_label,
            "orientation": -1,
            "source_geometry": {
                "kind": "bottom_coordinate_arc",
                "component_ref": f"geometry/t73_actual_ar_link.json#/components/{owner}/C_i",
                "polyline": bottom["C_i"],
                "universal_cover_lift": bottom["C_i_universal_cover_lift"],
            },
        }
    )
    return freely_reduce_events(events)


def dual_events(
    owner: str,
    component: dict[str, Any],
    x_slides: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    original = component["polyline"]
    points = [[Fraction(value) for value in point] for point in reversed(original)]
    events: list[dict[str, Any]] = []
    for traversal_index in range(1, len(points) - 1):
        point = points[traversal_index]
        previous, following = points[traversal_index - 1], points[traversal_index + 1]
        for axis in DUAL_AXES[owner]:
            if (
                point[axis] != 2
                or previous[axis] == 2
                or following[axis] == 2
                or previous[axis] == following[axis]
            ):
                continue
            # The actual attaching orientation used by the cut-tangle builder
            # is the reverse of the stored dual-disk boundary.  In contrast,
            # build_t73_belt_spheres scans the stored boundary forwards when
            # it records the x-slide orientation.  Thus an x replacement must
            # reverse that stored slide sign; mixing the two traversals gives
            # the erroneous r_xy word Z y z Y.
            orientation = 1 if following[axis] > previous[axis] else -1
            original_index = len(original) - 1 - traversal_index
            source_id = f"{owner}:vertex:{original_index}"
            original_label = AXIS_LABEL[axis]
            geometry: dict[str, Any] = {
                "kind": "dual_cell_boundary_subarc",
                "component_ref": f"geometry/t73_actual_ar_link.json#/components/{owner}",
                "original_axis": original_label,
                "vertex_index": original_index,
                "local_polyline": [
                    [str(value) for value in previous],
                    [str(value) for value in point],
                    [str(value) for value in following],
                ],
            }
            if axis == 0:
                slide = x_slides[source_id]
                label = "z"
                stored_forward_orientation = int(slide["replacement_orientation"])
                if orientation != -stored_forward_orientation:
                    raise AssertionError(
                        f"{owner}: x-slide orientation is incompatible with reverse component traversal"
                    )
                geometry.update(
                    {
                        "kind": "dual_x_slide_z_replacement",
                        "x_slide_band_sha256": canonical_sha(slide),
                        "replacement_curve_ref": slide["replacement_curve_ref"],
                        "replacement_orientation": orientation,
                        "stored_slide_forward_orientation": stored_forward_orientation,
                        "component_traversal_orientation_factor": -1,
                        "component_orientation": "reverse stored dual-disk boundary",
                        "relative_twist": int(slide["relative_twist"]),
                    }
                )
            else:
                label = original_label
            events.append(
                {
                    "owner": owner,
                    "source_id": source_id,
                    "source_order": len(events),
                    "label": label,
                    "orientation": orientation,
                    "source_geometry": geometry,
                }
            )
    return freely_reduce_events(events)


def cyclic_polyline_between(
    original: list[list[str]], start_vertex: int, end_vertex: int
) -> list[list[str]]:
    """Follow the reversed boundary traversal from start to end."""

    closed_length = len(original) - 1
    if original[0] != original[-1]:
        raise AssertionError("dual-cell boundary is not closed")
    result = [original[start_vertex]]
    index = start_vertex
    while index != end_vertex:
        index = (index - 1) % closed_length
        result.append(original[index])
        if len(result) > len(original) + 1:
            raise AssertionError("dual connector traversal did not terminate")
    return result


def connector_for_pair(
    owner: str,
    y_event: dict[str, Any],
    z_event: dict[str, Any],
    link: dict[str, Any],
    spine: dict[str, Any],
    t_slides: dict[tuple[str, str], dict[str, Any]],
    reductions: list[dict[str, Any]],
) -> dict[str, Any]:
    if owner in ("m_2", "m_3"):
        y_source = y_event["source_id"]
        z_source = z_event["source_id"]
        y_index = (
            int(y_source.rsplit(":", 1)[1]) if ":letter:" in y_source else None
        )
        z_index = (
            int(z_source.rsplit(":", 1)[1]) if ":letter:" in z_source else None
        )
        if y_source.endswith(":C_i") or (z_index == 0 and bool(reductions)):
            return {
                "kind": "cyclic_bottom_top_connector_after_t_cancellation",
                "component": owner,
                "bottom_arc_ref": f"geometry/t73_actual_ar_link.json#/components/{owner}/C_i",
                "top_start_source_id": z_source,
                "t_slide_band_sha256": [
                    canonical_sha(t_slides[(owner, "lambda_i")]),
                    canonical_sha(t_slides[(owner, "mu_i")]),
                ],
                "free_reduction_pairs_crossed": reductions,
            }
        if y_index is None or z_index is None:
            raise AssertionError(f"{owner}: noncyclic pair has no Johnson letter indices")
        if z_index != y_index + 1:
            raise AssertionError(f"{owner}: noncyclic y/z pair skips a surviving source arc")
        connector_id = f"c{1 if owner == 'm_2' else 2}:between:{y_index}"
        connectors = {item["connector_id"]: item for item in spine["central_connectors"]}
        connector = connectors[connector_id]
        return {
            "kind": "johnson_central_connector",
            "connector_id": connector_id,
            "connector_sha256": canonical_sha(connector),
            "polyline": connector["polyline"],
        }

    start = int(y_event["source_id"].rsplit(":", 1)[1])
    end = int(z_event["source_id"].rsplit(":", 1)[1])
    original = link["components"][owner]["polyline"]
    return {
        "kind": "oriented_dual_cell_boundary_interval",
        "component": owner,
        "from_vertex": start,
        "to_vertex": end,
        "traversal": "reverse stored boundary",
        "polyline": cyclic_polyline_between(original, start, end),
    }


def pair_and_leftovers(
    owner: str,
    events: list[dict[str, Any]],
    reductions: list[dict[str, Any]],
    link: dict[str, Any],
    spine: dict[str, Any],
    t_slides: dict[tuple[str, str], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pairs: list[dict[str, Any]] = []
    paired_z: set[int] = set()
    for index, event in enumerate(events):
        if event["label"] != "y":
            continue
        if not events:
            raise AssertionError(f"{owner}: empty event list contains y")
        z_index = (index + 1) % len(events)
        z_event = events[z_index]
        if z_event["label"] != "z":
            raise AssertionError(f"{owner}: y event {index} is not followed by z")
        if z_index in paired_z:
            raise AssertionError(f"{owner}: z event {z_index} is paired twice")
        paired_z.add(z_index)
        pairs.append(
            {
                "primitive_id": f"{owner}:yz:{len(pairs)}",
                "owner": owner,
                "y_event_index": index,
                "z_event_index": z_index,
                "y_source_id": event["source_id"],
                "z_source_id": z_event["source_id"],
                "y_orientation": int(event["orientation"]),
                "z_orientation": int(z_event["orientation"]),
                "y_side": event["source_geometry"],
                "z_side": z_event["source_geometry"],
                "connector": connector_for_pair(
                    owner, event, z_event, link, spine, t_slides, reductions
                ),
                "product_framing": {
                    "normal_width": link["framing"]["spine_ribbon_transport"]["width"],
                    "relative_twist": 0,
                    "source": "transported AR product annulus and registered zero-twist cancellations",
                },
            }
        )
    leftovers = [
        {
            "primitive_id": f"{owner}:leftover_z:{number}",
            "owner": owner,
            "z_event_index": index,
            "z_source_id": event["source_id"],
            "z_orientation": int(event["orientation"]),
            "source_geometry": event["source_geometry"],
        }
        for number, (index, event) in enumerate(
            (item for item in enumerate(events) if item[1]["label"] == "z" and item[0] not in paired_z)
        )
    ]
    return pairs, leftovers


def standardize_leftover_circles(
    leftovers_by_owner: dict[str, list[dict[str, Any]]], width: str
) -> None:
    owner_sector = {"m_2": 3, "m_3": 5, "r_xy": 7, "r_yz": 9, "r_zx": 11}
    radius = Fraction(1, 100000)
    for owner in OWNERS:
        for index, leftover in enumerate(leftovers_by_owner[owner]):
            center = Fraction(owner_sector[owner]) + Fraction(index + 1, 10000)
            leftover["standard_meridian"] = [
                [str(center), str(radius), "0"],
                [str(center), "0", str(radius)],
                [str(center), str(-radius), "0"],
                [str(center), "0", str(-radius)],
                [str(center), str(radius), "0"],
            ]
            leftover["conditional_transport"] = {
                "chart": "normalized Johnson product-collar complement chart",
                "source_normal_width": width,
                "private_level": str(Fraction(index + 1, len(leftovers_by_owner[owner]) + 1)),
                "ambient_scope": "conditional on the P0 collar inclusion; not asserted in actual partial W2",
            }


def expected_words(compact: Any) -> dict[str, list[str]]:
    return {
        "m_2": compact.after_x_cancellation(1),
        "m_3": compact.after_x_cancellation(2),
        "r_xy": [
            "z" if value == "x" else "Z" if value == "X" else value
            for value in compact.commutator("x", "y")
        ],
        "r_yz": compact.commutator("y", "z"),
        "r_zx": compact.free_reduce(
            [
                "z" if value == "x" else "Z" if value == "X" else value
                for value in compact.commutator("z", "x")
            ]
        ),
    }


def verify_payload(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "t73_all_owner_product_primitives/v1":
        raise AssertionError("unexpected all-owner product schema")
    owners = payload["owners"]
    if tuple(owners) != OWNERS:
        raise AssertionError("owner order changed")
    counts = payload["counts"]
    if tuple(counts["n_y"]) != EXPECTED_N_Y or tuple(counts["n_z"]) != EXPECTED_N_Z:
        raise AssertionError("all-owner y/z counts changed")
    live_spine = json.loads(SPINE.read_text(encoding="utf-8"))
    live_link = json.loads(LINK.read_text(encoding="utf-8"))
    live_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    live_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    expected_dependencies = {
        "johnson_spine_embedding_sha256": live_spine["sha256"],
        "actual_ar_link_sha256": live_link["sha256"],
        "t_cancellation_sha256": live_t["sha256"],
        "x_cancellation_sha256": live_x["sha256"],
    }
    if payload["dependencies"] != expected_dependencies:
        raise AssertionError("all-owner artifact is stale relative to its geometry")
    live_spine_arcs = {arc["arc_id"]: arc for arc in live_spine["handle_arcs"]}
    live_x_slides = {slide["source_id"]: slide for slide in live_x["slide_bands"]}
    live_connectors = {
        connector["connector_id"]: connector
        for connector in live_spine["central_connectors"]
    }
    compact = load_script("generate_t73_compact_kirby_ledger")
    compact_words = expected_words(compact)

    all_sources: set[str] = set()
    x_bound_sources: set[str] = set()
    meridians: set[str] = set()
    for owner, expected_y, expected_z in zip(OWNERS, EXPECTED_N_Y, EXPECTED_N_Z):
        record = payload["primitive_geometry"][owner]
        events = record["reduced_events"]
        pairs = record["product_rectangles"]
        leftovers = record["leftover_z_circles"]
        word = [oriented_letter(event) for event in events]
        if record["reduced_word"] != word or record["reduced_word_sha256"] != canonical_sha(word):
            raise AssertionError(f"{owner}: reduced word is not its event word")
        if owner == "m_3":
            if len(word) != len(compact_words[owner]) or Counter(word) != Counter(compact_words[owner]):
                raise AssertionError("m_3: signed compact incidence changed")
        elif word != compact_words[owner]:
            raise AssertionError(f"{owner}: compact word binding changed")
        if owner == "m_3":
            reductions = record["free_reduction_pairs"]
            if len(reductions) != 1 or {
                reductions[0]["left_source_id"], reductions[0]["right_source_id"]
            } != {"c2:letter:1460", "m_3:C_i"}:
                raise AssertionError("m_3 terminal/bottom free reduction changed")
        if owner == "r_zx" and len(record["free_reduction_pairs"]) != 2:
            raise AssertionError("r_zx does not record its two product bigons")
        if sum(event["label"] == "y" for event in events) != expected_y:
            raise AssertionError(f"{owner}: wrong y incidence")
        if sum(event["label"] == "z" for event in events) != expected_z:
            raise AssertionError(f"{owner}: wrong z incidence")
        if len(pairs) != expected_y or len(leftovers) != expected_z - expected_y:
            raise AssertionError(f"{owner}: product/leftover partition changed")
        event_source = {event["source_id"] for event in events}
        if len(event_source) != len(events):
            raise AssertionError(f"{owner}: a surviving source ID occurs twice")
        if all_sources & event_source:
            raise AssertionError("source ID is shared by two owners")
        all_sources |= event_source
        for event in events:
            source_id = event["source_id"]
            geometry = event["source_geometry"]
            if geometry["kind"] in ("johnson_handle_lane", "x_slide_z_replacement"):
                if source_id not in live_spine_arcs:
                    raise AssertionError(f"{owner}: Johnson source arc is absent")
                if geometry["spine_arc_sha256"] != canonical_sha(live_spine_arcs[source_id]):
                    raise AssertionError(f"{owner}: Johnson source arc hash changed")
            if geometry["kind"] in ("x_slide_z_replacement", "dual_x_slide_z_replacement"):
                if source_id not in live_x_slides:
                    raise AssertionError(f"{owner}: x-slide source is absent")
                if geometry["x_slide_band_sha256"] != canonical_sha(live_x_slides[source_id]):
                    raise AssertionError(f"{owner}: x-slide hash changed")
        paired_z: set[str] = set()
        for pair in pairs:
            if pair["y_source_id"] not in event_source or pair["z_source_id"] not in event_source:
                raise AssertionError(f"{owner}: rectangle source is absent")
            if pair["z_source_id"] in paired_z:
                raise AssertionError(f"{owner}: z source paired twice")
            paired_z.add(pair["z_source_id"])
            y_index = int(pair["y_event_index"])
            z_index = int(pair["z_event_index"])
            if not events or z_index != (y_index + 1) % len(events):
                raise AssertionError(f"{owner}: pair is not cyclically consecutive")
            if (
                events[y_index]["label"] != "y"
                or events[z_index]["label"] != "z"
                or events[y_index]["source_id"] != pair["y_source_id"]
                or events[z_index]["source_id"] != pair["z_source_id"]
            ):
                raise AssertionError(f"{owner}: pair incidence disagrees with events")
            connector = pair["connector"]
            if connector["kind"] == "johnson_central_connector":
                connector_id = connector["connector_id"]
                if connector_id not in live_connectors:
                    raise AssertionError("Johnson pair connector is absent")
                if connector["connector_sha256"] != canonical_sha(live_connectors[connector_id]):
                    raise AssertionError("Johnson pair connector hash changed")
            for side in (pair["y_side"], pair["z_side"]):
                if side["kind"] in ("x_slide_z_replacement", "dual_x_slide_z_replacement"):
                    if not side.get("x_slide_band_sha256") or side.get("relative_twist") != 0:
                        raise AssertionError("x replacement lost its cancellation-band binding")
                    x_bound_sources.add(
                        pair["y_source_id"] if side is pair["y_side"] else pair["z_source_id"]
                    )
        leftover_sources = {item["z_source_id"] for item in leftovers}
        if paired_z & leftover_sources:
            raise AssertionError(f"{owner}: z source is paired and leftover")
        all_z_sources = {event["source_id"] for event in events if event["label"] == "z"}
        if paired_z | leftover_sources != all_z_sources:
            raise AssertionError(f"{owner}: z incidence is not exhausted")
        for leftover in leftovers:
            side = leftover["source_geometry"]
            if side["kind"] in ("x_slide_z_replacement", "dual_x_slide_z_replacement"):
                if not side.get("x_slide_band_sha256") or side.get("relative_twist") != 0:
                    raise AssertionError("leftover x replacement lost its slide binding")
                x_bound_sources.add(leftover["z_source_id"])
            meridian = leftover["standard_meridian"]
            if meridian[0] != meridian[-1]:
                raise AssertionError("leftover target meridian is not closed")
            meridian_hash = canonical_sha(meridian)
            if meridian_hash in meridians:
                raise AssertionError("two leftovers use the same standard meridian")
            meridians.add(meridian_hash)
            if any(Fraction(point[0]) <= 1 for point in meridian):
                raise AssertionError("leftover standard meridian meets the detector sector")
    expected_x_bound = {
        event["source_id"]
        for owner in OWNERS
        for event in payload["primitive_geometry"][owner]["reduced_events"]
        if event["source_geometry"]["kind"]
        in ("x_slide_z_replacement", "dual_x_slide_z_replacement")
    }
    if x_bound_sources != expected_x_bound:
        raise AssertionError("not every surviving x replacement is slide-bound")
    theorem = payload["parallel_copy_theorem"]
    if theorem["rectangle_count_formula"] != "sum_i r_i*n_y_i":
        raise AssertionError("parallel rectangle formula changed")
    if theorem["leftover_circle_count_formula"] != "sum_i r_i*(n_z_i-n_y_i)":
        raise AssertionError("parallel leftover formula changed")
    if theorem["copy_offset_formula"] != "delta(i,j,r)=width_i*(2*j-r+1)/(2*(r+1))":
        raise AssertionError("parallel-copy offset formula changed")
    if payload["ambient_scope"]["actual_partial_W2_claimed"]:
        raise AssertionError("conditional collar was promoted to actual partial W2")


def build(write: bool = False) -> dict[str, Any]:
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    link = json.loads(LINK.read_text(encoding="utf-8"))
    cancel_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    if link["johnson_spine_sha256"] != spine["sha256"]:
        raise AssertionError("AR link is stale relative to Johnson spine")
    if cancel_t["ar_link_sha256"] != link["sha256"] or cancel_x["ar_link_sha256"] != link["sha256"]:
        raise AssertionError("cancellation data are stale relative to AR link")
    if cancel_x["t_cancellation_sha256"] != cancel_t["sha256"]:
        raise AssertionError("x cancellation is stale relative to t cancellation")
    x_slides = {item["source_id"]: item for item in cancel_x["slide_bands"]}
    t_slides = {
        (item["component"], item["removed_t_arc"]): item
        for item in cancel_t["slide_bands"]
    }

    reduced: dict[str, list[dict[str, Any]]] = {}
    reductions: dict[str, list[dict[str, Any]]] = {}
    reduced["m_2"], reductions["m_2"] = spine_events(
        "m_2", 1, "y", spine, link, x_slides
    )
    reduced["m_3"], reductions["m_3"] = spine_events(
        "m_3", 2, "z", spine, link, x_slides
    )
    for owner in ("r_xy", "r_yz", "r_zx"):
        reduced[owner], reductions[owner] = dual_events(
            owner, link["components"][owner], x_slides
        )

    compact = load_script("generate_t73_compact_kirby_ledger")
    expected = expected_words(compact)
    for owner in OWNERS:
        actual_word = [oriented_letter(event) for event in reduced[owner]]
        if owner == "m_3":
            # The selected Johnson lift was required to match the compact m_2
            # word exactly.  Its m_3 is a different embedded representative
            # with the same post-cancellation incidence data; do not silently
            # replace it by the compact word.
            if len(actual_word) != len(expected[owner]) or Counter(actual_word) != Counter(expected[owner]):
                raise AssertionError("m_3: Johnson representative has the wrong signed incidence")
        elif actual_word != expected[owner]:
            raise AssertionError(f"{owner}: source-bound reduction differs from compact word")

    pairs_by_owner: dict[str, list[dict[str, Any]]] = {}
    leftovers_by_owner: dict[str, list[dict[str, Any]]] = {}
    for owner in OWNERS:
        pairs_by_owner[owner], leftovers_by_owner[owner] = pair_and_leftovers(
            owner,
            reduced[owner],
            reductions[owner],
            link,
            spine,
            t_slides,
        )
    width = link["framing"]["spine_ribbon_transport"]["width"]
    standardize_leftover_circles(leftovers_by_owner, width)

    payload = {
        "schema": "t73_all_owner_product_primitives/v1",
        "dependencies": {
            "johnson_spine_embedding_sha256": spine["sha256"],
            "actual_ar_link_sha256": link["sha256"],
            "t_cancellation_sha256": cancel_t["sha256"],
            "x_cancellation_sha256": cancel_x["sha256"],
        },
        "owners": list(OWNERS),
        "counts": {
            "n_y": list(EXPECTED_N_Y),
            "n_z": list(EXPECTED_N_Z),
            "rectangles_per_balanced_cable_pair": sum(EXPECTED_N_Y),
            "leftover_circles_per_balanced_cable_pair": sum(
                z - y for y, z in zip(EXPECTED_N_Y, EXPECTED_N_Z)
            ),
        },
        "primitive_geometry": {
            owner: {
                "reduced_word": [oriented_letter(event) for event in reduced[owner]],
                "reduced_word_sha256": canonical_sha(
                    [oriented_letter(event) for event in reduced[owner]]
                ),
                "free_reduction_pairs": reductions[owner],
                "reduced_events": reduced[owner],
                "product_rectangles": pairs_by_owner[owner],
                "leftover_z_circles": leftovers_by_owner[owner],
                "compact_word_relation": (
                    "same signed letter multiset and length; distinct Johnson representative"
                    if owner == "m_3"
                    else "exact word equality"
                ),
            }
            for owner in OWNERS
        },
        "parallel_copy_theorem": {
            "hypothesis": (
                "the finite primitive rectangles and leftover-circle transports have pairwise-disjoint "
                "product neighborhoods inside the normalized Johnson collar"
            ),
            "copy_offset_formula": "delta(i,j,r)=width_i*(2*j-r+1)/(2*(r+1))",
            "copy_index_range": "0<=j<r_i",
            "distinct_offsets": True,
            "rectangle_count_formula": "sum_i r_i*n_y_i",
            "leftover_circle_count_formula": "sum_i r_i*(n_z_i-n_y_i)",
            "framing": "each copy uses the transported product normal and has relative twist zero",
            "conclusion": "every finite balanced cable multiplicity is obtained by disjoint parallel copies",
        },
        "ambient_scope": {
            "chart": "normalized post-t/post-x Johnson product collar",
            "actual_partial_W2_claimed": False,
            "conditional_on": "an explicit P0 ambient inclusion of this collar into partial W2",
        },
    }
    verify_payload(payload)
    payload["sha256"] = canonical_sha(payload)
    if write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def mutation_results(payload: dict[str, Any]) -> dict[str, bool]:
    results: dict[str, bool] = {}
    mutations: dict[str, Any] = {}

    wrong_count = copy.deepcopy(payload)
    wrong_count["counts"]["n_y"][1] -= 1
    mutations["m3_y_count"] = wrong_count

    wrong_pair = copy.deepcopy(payload)
    wrong_pair["primitive_geometry"]["m_3"]["product_rectangles"][0]["z_source_id"] = (
        "missing:m3:z"
    )
    mutations["m3_pair_source"] = wrong_pair

    missing_slide = copy.deepcopy(payload)
    for event in missing_slide["primitive_geometry"]["m_3"]["reduced_events"]:
        if event["source_geometry"]["kind"] == "x_slide_z_replacement":
            event["source_geometry"].pop("x_slide_band_sha256")
            break
    mutations["m3_x_slide_binding"] = missing_slide

    wrong_slide = copy.deepcopy(payload)
    for event in wrong_slide["primitive_geometry"]["m_3"]["reduced_events"]:
        if event["source_geometry"]["kind"] == "x_slide_z_replacement":
            event["source_geometry"]["x_slide_band_sha256"] = "0" * 64
            break
    mutations["m3_wrong_x_slide_hash"] = wrong_slide

    wrong_reduction = copy.deepcopy(payload)
    wrong_reduction["primitive_geometry"]["m_3"]["reduced_events"].append(
        copy.deepcopy(wrong_reduction["primitive_geometry"]["m_3"]["reduced_events"][-1])
    )
    mutations["m3_free_reduction"] = wrong_reduction

    promoted_scope = copy.deepcopy(payload)
    promoted_scope["ambient_scope"]["actual_partial_W2_claimed"] = True
    mutations["ambient_scope_promotion"] = promoted_scope

    for name, mutant in mutations.items():
        try:
            verify_payload(mutant)
        except (AssertionError, KeyError, ValueError):
            results[name] = True
        else:
            results[name] = False
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(write=args.write)
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != payload:
            raise AssertionError("committed all-owner product primitives differ from rebuild")
    mutations = mutation_results(payload)
    if not all(mutations.values()):
        raise AssertionError(f"an all-owner mutation survived: {mutations}")
    print("T73_ALL_OWNER_PRODUCT_PRIMITIVES=PASS")
    print("N_Y=" + json.dumps(payload["counts"]["n_y"], separators=(",", ":")))
    print("N_Z=" + json.dumps(payload["counts"]["n_z"], separators=(",", ":")))
    print(f"RECTANGLES={payload['counts']['rectangles_per_balanced_cable_pair']}")
    print(f"LEFTOVER_CIRCLES={payload['counts']['leftover_circles_per_balanced_cable_pair']}")
    print("MUTATIONS=" + json.dumps(mutations, sort_keys=True, separators=(",", ":")))
    print(f"SHA256={payload['sha256']}")


if __name__ == "__main__":
    main()
