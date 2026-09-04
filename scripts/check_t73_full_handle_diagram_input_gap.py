#!/usr/bin/env python3
"""Locate the first missing coordinate map before the T73 PD exporter input.

This is a structural audit of live AR and cancellation artifacts.  It never
upgrades event/band ledgers into a geometric map merely because their status
field says PASS.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AR = ROOT / "geometry" / "t73_actual_ar_link.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
COMPLETE_INPUT = ROOT / "geometry" / "t73_full_handle_diagram_input.json"


def point_arities(polyline: Any) -> list[int]:
    if not isinstance(polyline, list):
        return []
    return sorted({len(point) for point in polyline if isinstance(point, list)})


def inspect() -> dict[str, Any]:
    ar = json.loads(AR.read_text(encoding="utf-8"))
    cancel_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    components = ar.get("components", {})
    mapping_torus_arities = {
        name: point_arities(components.get(name, {}).get("core_polyline_T3xI"))
        for name in ("m_1", "m_2", "m_3", "h_CS")
    }
    dual_arities = {
        name: point_arities(components.get(name, {}).get("polyline"))
        for name in ("r_xy", "r_yz", "r_zx")
    }
    t_post_has_core = {
        name: isinstance(record, dict) and "closed_core_polyline" in record
        for name, record in cancel_t.get("post_cancel_components", {}).items()
    }
    x_post_has_core = {
        name: isinstance(record, dict) and "closed_core_polyline" in record
        for name, record in cancel_x.get("post_cancel_components", {}).items()
    }
    dotted_present = {
        name: name in components
        for name in ("dotted_y", "dotted_z")
    }
    complete_validation: dict[str, Any]
    ready = False
    if COMPLETE_INPUT.is_file():
        try:
            candidate = json.loads(COMPLETE_INPUT.read_text(encoding="utf-8"))
            provenance = candidate.get("provenance", {})
            expected_provenance = {
                "actual_ar_link_sha256": ar.get("sha256"),
                "t_cancellation_sha256": cancel_t.get("sha256"),
                "x_cancellation_sha256": cancel_x.get("sha256"),
            }
            if provenance != expected_provenance:
                raise ValueError(
                    f"provenance {provenance!r} does not equal {expected_provenance!r}"
                )
            exporter_path = ROOT / "scripts" / "export_t73_full_handle_diagram.py"
            spec = importlib.util.spec_from_file_location("t73_full_exporter", exporter_path)
            if spec is None or spec.loader is None:
                raise ValueError("cannot import full handle exporter")
            exporter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(exporter)
            exported = exporter.export(candidate)
            complete_validation = {
                "status": "PASS",
                "export_sha256": exported["sha256"],
            }
            ready = True
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            complete_validation = {"status": "OPEN", "reason": str(exc)}
    else:
        complete_validation = {"status": "OPEN", "reason": "candidate file is absent"}
    first_map = {
        "name": "kappa_AR_to_common_Kirby_presentation",
        "map_type": "cut-and-surgery presentation map, not an ambient embedding",
        "domain": (
            "the #4(S1xS2) pre-cancellation attaching boundary, represented by "
            "the seam-identified T^3 x I AR charts together with the octahedral "
            "t-belt chart, cubical x-belt chart, and dual-cell H2 chart"
        ),
        "codomain": (
            "either a four-dotted-circle rational link presentation in S^3, or "
            "an explicit triangulation of #4(S1xS2); after the two cancellations, "
            "respectively a two-dotted-circle S^3 presentation or #2(S1xS2) triangulation"
        ),
        "must_map": [
            "all seven pre-cancellation attaching cores and four pre-cancellation dotted meridians",
            "both cancellation belt spheres and both edges of every slide band",
            "all AR product framing ribbons",
            "the five post-cancellation cores and eventual dotted y and dotted z meridians",
        ],
        "boundary_conditions": [
            "respect the mapping-torus seam",
            "agree on all overlapping source charts",
            "embed each cut-open core/ribbon/belt/band piece and record every surgery quotient pairing",
            "record an ambient orientation and one exact generic projection",
        ],
        "ambient_embedding_obstruction": (
            "a global embedding #g(S1xS2)->S3 for g=4 or g=2 is impossible: "
            "invariance of domain would make the image open and closed, hence all of S3, "
            "contradicting H1(#g(S1xS2))=Z^g while H1(S3)=0"
        ),
        "why_first": (
            "m_2/m_3 are stored as four-coordinate T^3 x I seam polylines, "
            "whereas r_xy/r_yz/r_zx and belt-band centers are stored in several "
            "three-coordinate local charts; no transition plus cut/surgery quotient "
            "presentation is present, so band surgery cannot yet output one final core"
        ),
    }
    blockers = [
        {
            "stage": 0,
            "missing": first_map["name"],
            "evidence": {
                "mapping_torus_point_arities": mapping_torus_arities,
                "dual_cell_point_arities": dual_arities,
                "common_chart_field_in_ar": "common_kirby_chart" in ar,
            },
        },
        {
            "stage": 1,
            "missing": "ordered band-surgery trace producing post-(t,h_CS) closed cores",
            "evidence": {
                "post_cancel_closed_core_polyline_present": t_post_has_core,
                "stored_band_data": (
                    "center paths and target points only; no two boundary edges, "
                    "attachment parameters, or spliced cyclic successor"
                ),
            },
        },
        {
            "stage": 2,
            "missing": "ordered band-surgery trace producing post-(x,m_1) closed cores",
            "evidence": {
                "post_cancel_closed_core_polyline_present": x_post_has_core,
                "stored_band_data": (
                    "belt-face center paths and a replacement-curve reference only; "
                    "no embedded parallel replacement arc or final splice"
                ),
            },
        },
        {
            "stage": 3,
            "missing": "dotted_y/dotted_z closed cores and five transported closed push-offs",
            "evidence": {"dotted_components_present_in_ar": dotted_present},
        },
    ]
    return {
        "schema": "t73_full_handle_diagram_input_gap/v1",
        "sources": {
            "actual_ar_link": str(AR.relative_to(ROOT)),
            "t_cancellation": str(CANCEL_T.relative_to(ROOT)),
            "x_cancellation": str(CANCEL_X.relative_to(ROOT)),
        },
        "complete_exporter_input_present": COMPLETE_INPUT.is_file(),
        "complete_exporter_input_validation": complete_validation,
        "first_missing_coordinate_map": first_map,
        "ordered_downstream_blockers": blockers,
        "exporter_readiness": "PASS" if ready else "OPEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect-open", action="store_true")
    args = parser.parse_args()
    result = inspect()
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.expect_open and result["exporter_readiness"] != "OPEN":
        raise SystemExit("current T73 input unexpectedly became complete; update this audit")


if __name__ == "__main__":
    main()
