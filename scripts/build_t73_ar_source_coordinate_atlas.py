#!/usr/bin/env python3
"""Inventory the actual AR/cancellation coordinate charts without gluing them.

The output is a stage-0 atlas: it records what coordinates really exist,
which transitions are forced by the builders, and which transition choices
are absent.  It intentionally does not pretend that the attaching boundary
#^g(S1 x S2) embeds in S3; a dotted-circle target is a surgery presentation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AR_PATH = ROOT / "geometry" / "t73_actual_ar_link.json"
BELT_PATH = ROOT / "geometry" / "t73_belt_spheres.json"
T_CANCEL_PATH = ROOT / "geometry" / "t73_cancel_t_hcs.json"
X_CANCEL_PATH = ROOT / "geometry" / "t73_cancel_x_m1.json"
PAIR_PATH = ROOT / "audit" / "t73_p0a_handlebody_pair.json"
OUTPUT = ROOT / "geometry" / "t73_ar_source_coordinate_atlas.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def dimensions(polyline: Any) -> list[int]:
    if not isinstance(polyline, list):
        return []
    return sorted({len(point) for point in polyline if isinstance(point, list)})


def closed_literal(polyline: Any) -> bool:
    return isinstance(polyline, list) and len(polyline) >= 2 and polyline[0] == polyline[-1]


def component_inventory(ar: dict[str, Any]) -> dict[str, Any]:
    records = {}
    for name in ("m_1", "m_2", "m_3"):
        component = ar["components"][name]
        core = component["core_polyline_T3xI"]
        framing = component["full_framing_annulus"]
        records[name] = {
            "chart": "mapping_torus_T3xI",
            "source_pointer": f"/components/{name}/core_polyline_T3xI",
            "coordinate_dimension": dimensions(core),
            "vertex_count": len(core),
            "closed_mode": "literal_polyline",
            "closed_verified": closed_literal(core),
            "core_sha256": canonical_sha(core),
            "framing": {
                "status": "PROCEDURAL_SOURCE_DATA",
                "source_pointer": f"/components/{name}/full_framing_annulus",
                "outer_core_rule": framing["outer_core_rule"],
                "relative_twist": framing["relative_twist"],
                "quadrilateral_count": framing["quadrilateral_count"],
                "framing_sha256": canonical_sha(framing),
            },
        }
    hcs = ar["components"]["h_CS"]
    records["h_CS"] = {
        "chart": "mapping_torus_T3xI",
        "source_pointer": "/components/h_CS/core_polyline_T3xI",
        "coordinate_dimension": dimensions(hcs["core_polyline_T3xI"]),
        "vertex_count": len(hcs["core_polyline_T3xI"]),
        "closed_mode": "mapping_torus_seam",
        "closed_verified": (
            hcs["core_polyline_T3xI"][0][:-1]
            == hcs["core_polyline_T3xI"][-1][:-1]
            and hcs["core_polyline_T3xI"][0][-1] == "0"
            and hcs["core_polyline_T3xI"][-1][-1] == "1"
            and hcs["closed_by_mapping_torus_seam"]
        ),
        "core_sha256": canonical_sha(hcs["core_polyline_T3xI"]),
        "framing": {
            "status": "PROCEDURAL_SOURCE_DATA",
            "source_pointer": "/components/h_CS/framing_annulus",
            "relative_twist": hcs["framing_annulus"]["relative_twist"],
            "framing_sha256": canonical_sha(hcs["framing_annulus"]),
        },
    }
    for name in ("r_xy", "r_yz", "r_zx"):
        component = ar["components"][name]
        core = component["polyline"]
        records[name] = {
            "chart": "fiber_dual_H2_T3",
            "source_pointer": f"/components/{name}/polyline",
            "coordinate_dimension": dimensions(core),
            "vertex_count": len(core),
            "closed_mode": "literal_polyline",
            "closed_verified": closed_literal(core) and component["disk"]["closed"],
            "core_sha256": canonical_sha(core),
            "framing": {
                "status": "OPEN",
                "reason": (
                    "the dual disk and product-framing name are present, but no closed "
                    "push-off polyline or ribbon vertex/triangle list is stored"
                ),
            },
        }
    return records


def build(write: bool = False) -> dict[str, Any]:
    ar = json.loads(AR_PATH.read_text(encoding="utf-8"))
    belts = json.loads(BELT_PATH.read_text(encoding="utf-8"))
    cancel_t = json.loads(T_CANCEL_PATH.read_text(encoding="utf-8"))
    cancel_x = json.loads(X_CANCEL_PATH.read_text(encoding="utf-8"))
    pair = json.loads(PAIR_PATH.read_text(encoding="utf-8"))
    if belts["ar_link_sha256"] != ar["sha256"]:
        raise AssertionError("belt atlas is stale relative to the AR link")
    if cancel_t["ar_link_sha256"] != ar["sha256"]:
        raise AssertionError("t cancellation is stale relative to the AR link")
    if cancel_x["ar_link_sha256"] != ar["sha256"]:
        raise AssertionError("x cancellation is stale relative to the AR link")
    if cancel_x["t_cancellation_sha256"] != cancel_t["sha256"]:
        raise AssertionError("x cancellation is stale relative to t cancellation")

    cores = component_inventory(ar)
    t_bands = cancel_t["slide_bands"]
    x_bands = cancel_x["slide_bands"]
    t_dimensions = sorted(
        {
            len(point)
            for band in t_bands
            for point in band["band_core_on_belt_sphere"]
        }
    )
    x_dimensions = sorted(
        {
            len(point)
            for band in x_bands
            for point in band["band_core_on_positive_belt_face"]
        }
    )
    result = {
        "schema": "t73_ar_source_coordinate_atlas/v1",
        "source_bindings": {
            "actual_ar_link_sha256": ar["sha256"],
            "belt_spheres_sha256": belts["sha256"],
            "t_cancellation_sha256": cancel_t["sha256"],
            "x_cancellation_sha256": cancel_x["sha256"],
            "p0a_handlebody_pair_sha256": pair["pair_sha256"],
        },
        "source_charts": {
            "mapping_torus_T3xI": {
                "dimension": 4,
                "coordinate_names": ["x", "y", "z", "u"],
                "u_interval": ["0", "1"],
                "seam": "(p,1)~(psi_A(p),0); identity only on the protected section ball",
                "objects": ["m_1", "m_2", "m_3", "h_CS"],
            },
            "fiber_dual_H2_T3": {
                "dimension": 3,
                "coordinate_names": ["x", "y", "z"],
                "objects": ["r_xy", "r_yz", "r_zx"],
                "missing_embedding_field": "fiber level/side u and transition into mapping_torus_T3xI",
            },
            "t_belt_slice": {
                "dimension": 3,
                "coordinate_names": ["x", "y", "z"],
                "ambient_lift": ["x", "y", "z", "1/2"],
                "belt_vertex_dimension": dimensions(belts["t_handle"]["belt_sphere"]["vertices"]),
                "band_center_dimension": t_dimensions,
                "band_count": len(t_bands),
            },
            "x_belt_local": {
                "dimension": 3,
                "coordinate_names": ["y", "z", "nu"],
                "ambient_local_coordinates": ["2", "y", "z", "nu"],
                "belt_vertex_dimension": dimensions(belts["x_handle"]["belt_sphere"]["vertices"]),
                "band_center_dimension": x_dimensions,
                "band_count": len(x_bands),
                "warning": "nu is the x-handle normal coordinate, not the mapping-torus coordinate u",
            },
            "johnson_ar_fiber_pair": {
                "dimension": 3,
                "pair_vertex_count": len(pair["ar"]["vertices"]),
                "handlebody_B_tetrahedra": len(pair["ar"]["handlebody_B"]),
                "handlebody_D_tetrahedra": len(pair["ar"]["handlebody_D"]),
                "scope": "one T3 fiber Heegaard pair; not a mapping-torus or Kirby-presentation chart",
            },
        },
        "pre_cancellation_cores": cores,
        "known_transitions": [
            {
                "id": "t_belt_to_mapping_torus_slice",
                "status": "PASS",
                "formula": "(x,y,z)->(x,y,z,1/2)",
                "scope": "t belt sphere and six stored band-center paths only",
            },
            {
                "id": "johnson_to_ar_fiber_similarity",
                "status": "PASS",
                "formula": "S(v)=v-(1,1,1) on the period-4 scaled mesh",
                "scope": "single-fiber Heegaard pair only",
            },
        ],
        "missing_transitions_in_order": [
            {
                "id": "fiber_dual_H2_to_mapping_torus",
                "status": "OPEN",
                "required_choice": "the u level/side and compatible seam collar for each dual-cell core and ribbon",
            },
            {
                "id": "x_belt_local_to_mapping_torus_or_cut_handlebody",
                "status": "OPEN",
                "required_choice": "a collar map u=u0+epsilon*nu (including seam-side choice and epsilon), not nu=u",
            },
            {
                "id": "cut_handlebody_to_dotted_S3_presentation",
                "status": "OPEN",
                "required_choice": (
                    "four pre-cancellation 1-handle foot pairs, orientation-reversing disk identifications, "
                    "lane endpoint maps, and ribbon normal trivializations"
                ),
            },
            {
                "id": "full_band_rectangles_and_surgery_splices",
                "status": "OPEN",
                "required_choice": (
                    "both edges and attachment parameters of 6 t-bands and 1513 x-bands, "
                    "plus embedded parallel replacement arcs"
                ),
            },
        ],
        "presentation_snapshots": {
            "pre_cancellation": {
                "one_handle_names": ["x", "y", "z", "t"],
                "required_dotted_meridians": 4,
                "two_handle_names": ["m_1", "m_2", "m_3", "h_CS", "r_xy", "r_yz", "r_zx"],
                "required_two_handle_cores": 7,
            },
            "post_cancellation": {
                "one_handle_names": ["y", "z"],
                "required_dotted_meridians": 2,
                "two_handle_names": ["m_2", "m_3", "r_xy", "r_yz", "r_zx"],
                "required_two_handle_cores": 5,
            },
        },
        "global_embedding_obstruction": {
            "claim": "neither #4(S1xS2) nor #2(S1xS2) embeds as a closed 3-submanifold of S3",
            "proof": (
                "invariance of domain makes the image of a closed connected 3-manifold open and closed in S3; "
                "surjectivity would force a homeomorphism, contradicted by H1=Z^g versus H1(S3)=0"
            ),
            "consequence": "the missing map must be a cut/surgery presentation or a triangulated-manifold isomorphism",
        },
        "status": {
            "source_chart_inventory": "PASS",
            "all_seven_pre_cancellation_cores_referenced": "PASS",
            "upstream_actual_framed_ar_link_claim": ar["status"]["actual_framed_ar_link"],
            "complete_pre_cancellation_framing_ribbons": "OPEN",
            "explicit_dual_cell_ribbon_count": 0,
            "explicit_pre_cancellation_dotted_meridian_count": 0,
            "data_completeness_conflict": (
                "upstream PASS names the product framings, but r_xy/r_yz/r_zx have no "
                "stored ribbon/push-off coordinates and x,y,z,t dotted cores are absent"
            ),
            "common_kirby_presentation": "OPEN",
            "reason": "the first two missing transition choices precede any honest dotted-circle PD export",
        },
    }
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check:
        if not OUTPUT.is_file() or json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
            raise AssertionError("committed AR source atlas differs from live rebuild")
    print("T73_AR_SOURCE_ATLAS=PASS")
    print(f"PRE_CANCEL_CORES={len(result['pre_cancellation_cores'])}")
    print(f"T_BANDS={result['source_charts']['t_belt_slice']['band_count']}")
    print(f"X_BANDS={result['source_charts']['x_belt_local']['band_count']}")
    print(f"COMMON_KIRBY={result['status']['common_kirby_presentation']}")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
