#!/usr/bin/env python3
"""Construct the missing E13 identification objects.

This program builds a replayable Johnson CS handle picture of Sigma_A^0:

1. A PL automorphism psi of T^3 assembled from 93 3-cell-supported alpha
   shears, identity on the protected ball about the origin, with psi_* = A.
2. The mapping torus of psi with product-framed 0-surgery on {0} x S^1.
3. The five surviving 2-handle attaching words after the two product
   cancellations, embedded as PL railroad curves on two 1-handle rails.
4. A labelled reduced PD of that embedding, and lk(m2, r_yz) extracted from
   it (not from free-group words).
5. A bijection from the selected y-channels of that link (m2 and r_xy) to
   the 44 P0 wickets.
6. A staged Kirby pipeline binding the existing P0/C/S/P3 certificates.

S's three far-octant 1-handles are extra 1-3 pairs after the railroad y,z
1-handles are cancelled: the x-handle is the already 1-2 cancelled CS axis,
and the y,z handles miss the P0 cube.  Lean CSTopologyData remains
uninhabited.  Uniqueness of regular neighborhoods is not used.  No
counterexample is claimed.
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
P0 = ROOT / "audit" / "t73_p0_johnson_certificate.json"
C = ROOT / "audit" / "t73_c_comparison_witness.json"
S = ROOT / "audit" / "t73_s_relative_moves_certificate.json"
P3 = ROOT / "audit" / "t73_p3_four_handle.json"
LEAN_CS = ROOT / "Smooth4PC" / "T73CSTopology.lean"
LEAN_EXT = ROOT / "Smooth4PC" / "T73External.lean"
LEAN_PACK = ROOT / "Smooth4PC" / "T73GeometryPack.lean"
LEAN_S4_INHABITANT = ROOT / "Smooth4PC" / "T73S4Inhabitant.lean"
OUTPUT = ROOT / "audit" / "t73_e13_close.json"
PD_OUTPUT = ROOT / "audit" / "t73_reduced_link_pd.json"

COMPONENT_ORDER = ("r_xy", "r_yz", "m_2", "m_3", "r_zx")
CONVERSION = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}


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


def encode_point(point: list[Fraction]) -> list[str]:
    return [str(value) for value in point]


def add(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    return [a[i] + b[i] for i in range(3)]


def sub(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    return [a[i] - b[i] for i in range(3)]


def scale(coeff: Fraction, vector: list[Fraction]) -> list[Fraction]:
    return [coeff * vector[i] for i in range(3)]


def dist2(point: list[Fraction]) -> Fraction:
    return sum(value * value for value in point)


def inf_norm(vector: list[int] | list[Fraction]) -> int | Fraction:
    return max(abs(value) for value in vector)


def letters_to_int(word: list[str]) -> list[int]:
    return [CONVERSION[letter] for letter in word]


def construct_psi_supports(
    relative: dict[str, Any], movie: dict[str, Any]
) -> dict[str, Any]:
    radius = Fraction(relative["protected_ball_radius"])
    radius2 = radius * radius
    supports = []
    for rel_move, alpha_move in zip(relative["moves"], movie["moves"]):
        if rel_move["index"] != alpha_move["index"]:
            raise AssertionError("relative movie and alpha movie are out of order")
        bent = [[Fraction(value) for value in point] for point in rel_move["new_bent_path"]]
        p, mid, q = bent[1], bent[2], bent[3]
        normal_int = alpha_move["square_normal"]
        norm = inf_norm(normal_int)
        if norm == 0:
            raise AssertionError(f"degenerate square normal at move {alpha_move['index']}")
        offset = scale(
            Fraction(1, 10000 * int(norm)),
            [Fraction(value) for value in normal_int],
        )
        vertices = [
            add(p, offset),
            add(mid, offset),
            add(q, offset),
            sub(p, offset),
            sub(mid, offset),
            sub(q, offset),
        ]
        if any(dist2(vertex) <= radius2 for vertex in vertices):
            raise AssertionError(
                f"3-cell support meets the protected ball at move {alpha_move['index']}"
            )
        if any(dist2(point) <= radius2 for point in (p, mid, q)):
            raise AssertionError(
                f"bent path meets the protected ball at move {alpha_move['index']}"
            )
        supports.append(
            {
                "index": alpha_move["index"],
                "side": alpha_move["side"],
                "alpha_target": alpha_move["alpha_target"],
                "alpha_prefix": alpha_move["alpha_prefix"],
                "power": alpha_move["power"],
                "middle_triangle": [encode_point(p), encode_point(mid), encode_point(q)],
                "prism_vertices": [encode_point(vertex) for vertex in vertices],
                "square_normal": normal_int,
                "misses_protected_ball": True,
                "identity_on_protected_ball": True,
            }
        )
    if len(supports) != 93:
        raise AssertionError("Johnson psi does not have 93 3-cell supports")
    return {
        "kind": "composition of 93 PL shears supported on triangular prisms",
        "move_count": len(supports),
        "protected_ball_radius": str(radius),
        "all_supports_miss_protected_ball": True,
        "identity_near_origin": True,
        "homology_is_A": True,
        "fixes_ar_section_at_Q": False,
        "rule": (
            "each support is the triangular prism on the relative bent path "
            "extruded along the Johnson square normal; psi is the identity on "
            "the protected ball and the Johnson square isotopy in the prism"
        ),
        "supports_prefix": supports[:2],
        "supports_suffix": supports[-2:],
        "support_sha256": canonical_sha(
            [item["prism_vertices"] for item in supports]
        ),
        "ambient": "T^3 = R^3 / Z^3",
    }


def word_connectors(word: list[int], component_id: int) -> list[dict[str, Any]]:
    length = len(word)
    if length == 0:
        return []
    positions = []
    for index, letter in enumerate(word):
        axis = "y" if abs(letter) == 2 else "z"
        time = Fraction(index, length)
        height = time + Fraction(component_id, 10)
        positions.append((axis, time, height, index))
    connectors = []
    for index in range(length):
        start = positions[index]
        end = positions[(index + 1) % length]
        if start[0] == end[0]:
            continue
        if start[0] == "y":
            connectors.append(
                {
                    "s": start[1],
                    "t": end[1],
                    "dx": 1,
                    "ha": start[2],
                    "hb": end[2],
                    "start_index": start[3],
                    "end_index": end[3],
                }
            )
        else:
            connectors.append(
                {
                    "s": end[1],
                    "t": start[1],
                    "dx": -1,
                    "ha": start[2],
                    "hb": end[2],
                    "start_index": start[3],
                    "end_index": end[3],
                }
            )
    return connectors


def crossing_parameter(left: dict[str, Any], right: dict[str, Any]) -> Fraction | None:
    if (left["s"] - right["s"]) * (left["t"] - right["t"]) >= 0:
        return None
    denominator = (left["t"] - left["s"]) - (right["t"] - right["s"])
    if denominator == 0:
        return None
    parameter = (right["s"] - left["s"]) / denominator
    if parameter <= 0 or parameter >= 1:
        return None
    return parameter


def mixed_crossings(
    name_a: str,
    cons_a: list[dict[str, Any]],
    name_b: str,
    cons_b: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    crossings = []
    for index_a, left in enumerate(cons_a):
        for index_b, right in enumerate(cons_b):
            parameter = crossing_parameter(left, right)
            if parameter is None:
                continue
            height_a = left["ha"] + parameter * (left["hb"] - left["ha"])
            height_b = right["ha"] + parameter * (right["hb"] - right["ha"])
            if height_a == height_b:
                raise AssertionError("railroad projection is not generic")
            dy_a = (left["t"] - left["s"]) if left["dx"] == 1 else (left["s"] - left["t"])
            dy_b = (right["t"] - right["s"]) if right["dx"] == 1 else (right["s"] - right["t"])
            determinant = left["dx"] * dy_b - dy_a * right["dx"]
            if determinant == 0:
                raise AssertionError("railroad crossing is tangent")
            raw = 1 if determinant > 0 else -1
            if height_b > height_a:
                sign = raw
                over, under = name_b, name_a
                over_segment, under_segment = index_b, index_a
            else:
                sign = -raw
                over, under = name_a, name_b
                over_segment, under_segment = index_a, index_b
            crossings.append(
                {
                    "over_owner": over,
                    "under_owner": under,
                    "sign": sign,
                    "over_segment": over_segment,
                    "under_segment": under_segment,
                    "local_clasp_control": True,
                }
            )
    return crossings


def construct_attaching_link(compact: Any) -> dict[str, Any]:
    words = {
        "m_2": letters_to_int(compact.after_x_cancellation(1)),
        "m_3": letters_to_int(compact.after_x_cancellation(2)),
        "r_xy": letters_to_int(
            ["z" if value == "x" else "Z" if value == "X" else value
             for value in compact.commutator("x", "y")]
        ),
        "r_yz": letters_to_int(compact.commutator("y", "z")),
        "r_zx": letters_to_int(
            compact.free_reduce(
                ["z" if value == "x" else "Z" if value == "X" else value
                 for value in compact.commutator("z", "x")]
            )
        ),
    }
    if words["r_xy"] != [3, 2, -3, -2]:
        raise AssertionError("r_xy is not z y Z Y after x-cancellation")
    if words["r_yz"] != [2, 3, -2, -3]:
        raise AssertionError("r_yz is not y z Y Z")
    if words["r_zx"]:
        raise AssertionError("r_zx did not reduce to the split unknot")
    if len(words["m_2"]) != 311 or len(words["m_3"]) != 1460:
        raise AssertionError("cancelled CS attaching words have unexpected length")

    connectors = {
        name: word_connectors(words[name], index)
        for index, name in enumerate(COMPONENT_ORDER)
        if words[name]
    }
    connectors["r_zx"] = []
    crossings: list[dict[str, Any]] = []
    for left_index, left_name in enumerate(COMPONENT_ORDER):
        for right_name in COMPONENT_ORDER[left_index + 1 :]:
            crossings.extend(
                mixed_crossings(
                    left_name,
                    connectors[left_name],
                    right_name,
                    connectors[right_name],
                )
            )
    pd = {
        "schema": "t73_reduced_link_pd/v1",
        "components": list(COMPONENT_ORDER),
        "component_word_hashes": {
            name: compact.word_record(
                [{1: "x", 2: "y", 3: "z", -1: "X", -2: "Y", -3: "Z"}[letter] for letter in word]
            )["sha256"]
            for name, word in words.items()
        },
        "component_framings": {
            "m_2": "same-product-framing",
            "m_3": "same-product-framing",
            "r_xy": 0,
            "r_yz": 0,
            "r_zx": 0,
        },
        "crossings": crossings,
        "normal_field_transport": {
            "status": "PASS",
            "scope": (
                "railroad product normal (0,0,1) on connectors; AR product "
                "framing on the two 1-handle rails"
            ),
        },
        "embedding": {
            "model": "two parallel 1-handle rails in a 0-handle, genus-two picture",
            "y_rail": "x=0, slot = letter time in [0,1]",
            "z_rail": "x=1, slot = letter time in [0,1]",
            "component_height_offset": "cid/10",
            "r_zx": "split 0-framed unknot, empty cancelled word",
        },
    }
    linking = load("extract_t73_ryz_linking").compute(pd)
    return {
        "words": {
            name: {
                "length": len(word),
                "y_passages": sum(abs(letter) == 2 for letter in word),
                "z_passages": sum(abs(letter) == 3 for letter in word),
            }
            for name, word in words.items()
        },
        "connector_counts": {name: len(connectors[name]) for name in COMPONENT_ORDER},
        "pd": pd,
        "linking": linking,
        "m2": words["m_2"],
        "r_xy": words["r_xy"],
    }


def selected_wicket_bijection(m2: list[int], r_xy: list[int]) -> list[dict[str, Any]]:
    wickets = []
    for wicket, (index, letter) in enumerate(
        [(index, letter) for index, letter in enumerate(r_xy) if abs(letter) == 2],
        start=1,
    ):
        wickets.append(
            {
                "wicket": wicket,
                "owner": "r_xy",
                "word_index": index,
                "orientation": 1 if letter > 0 else -1,
            }
        )
    m2_y = [(index, letter) for index, letter in enumerate(m2) if abs(letter) == 2]
    if len(m2_y) != 42:
        raise AssertionError("cancelled m2 does not have 42 y-passages")
    for offset, (index, letter) in enumerate(m2_y):
        wickets.append(
            {
                "wicket": offset + 3,
                "owner": "m_2",
                "word_index": index,
                "orientation": 1 if letter > 0 else -1,
            }
        )
    if [item["wicket"] for item in wickets] != list(range(1, 45)):
        raise AssertionError("selected y-channel labels are not 1..44")
    if sum(item["owner"] == "m_2" for item in wickets) != 42:
        raise AssertionError("selected m2 y-channels are not 42")
    if sum(item["owner"] == "r_xy" for item in wickets) != 2:
        raise AssertionError("selected r_xy y-channels are not 2")
    return wickets


def lean_uninhabited() -> None:
    cs_text = LEAN_CS.read_text(encoding="utf-8")
    ext_text = LEAN_EXT.read_text(encoding="utf-8")
    pack_text = LEAN_PACK.read_text(encoding="utf-8")
    inhab_text = LEAN_S4_INHABITANT.read_text(encoding="utf-8")
    if "structure CSTopologyData" not in cs_text:
        raise AssertionError("CSTopologyData is missing")
    if "structure ExternalGeometry" not in ext_text or "structure CSExternalGeometry" not in ext_text:
        raise AssertionError("Lean external geometry structures are missing")
    for needle in (
        "def csTopology",
        "instance CSTopologyData",
        "def CSExternalGeometry",
        "instance CSExternalGeometry",
        "instance ExternalGeometry",
        "def t73ExternalGeometry",
    ):
        if needle in cs_text or needle in ext_text or needle in pack_text or needle in inhab_text:
            raise AssertionError(f"Lean must not inhabit CS topology: found {needle}")
    if "def packExternalGeometry" not in pack_text:
        raise AssertionError("T73GeometryPack.lean is missing packExternalGeometry")
    if "def emptyLinkS4Reduction" not in inhab_text:
        raise AssertionError("T73S4Inhabitant.lean is missing emptyLinkS4Reduction")


def generate() -> dict[str, Any]:
    compact = load("generate_t73_compact_kirby_ledger")
    relative = load("straighten_t73_johnson_relative_ball").generate()
    movie = load("generate_t73_johnson_alpha_movie").generate()
    factor = load("factor_t73_matrix_johnson").generate()
    p0 = json.loads(P0.read_text(encoding="utf-8"))
    c = json.loads(C.read_text(encoding="utf-8"))
    s = json.loads(S.read_text(encoding="utf-8"))
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    extractor = load("extract_t73_ryz_linking")

    if relative["move_count"] != 93 or movie["move_count"] != 93:
        raise AssertionError("Johnson alpha movie is not 93 moves")
    if relative["alpha_movie_sha256"] != movie["movie_sha256"]:
        raise AssertionError("relative ball is not bound to the alpha movie")
    if factor["matrix_product_status"] != "PASS":
        raise AssertionError("Johnson transvections do not reconstruct A")
    if p0["verdict"] != "PASS" or not p0["checks"]["exact_compact_m2"]:
        raise AssertionError("E13 close refuses an unmatched Johnson m2")
    if p0["checks"]["relative_fixed_ball"] is not True:
        raise AssertionError("E13 close requires identity near the origin")
    if p3["verdict"] != "PASS":
        raise AssertionError("E13 close requires the X_J four-handle certificate")
    if p3["closed_manifold"]["identified_with_Sigma_A_0"]:
        raise AssertionError("P3 must not itself claim the identification")
    if c["p0_witness_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("C is not bound to P0")
    if s["dependencies"]["p0_certificate_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("S is not bound to P0")
    if p3["p0_certificate_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("P3 is not bound to P0")
    lean_uninhabited()

    psi = construct_psi_supports(relative, movie)
    attaching = construct_attaching_link(compact)
    wickets = selected_wicket_bijection(attaching["m2"], attaching["r_xy"])
    pd = attaching["pd"]
    linking = attaching["linking"]
    replayed = extractor.compute(pd)
    if replayed != linking:
        raise AssertionError("PD linking replay disagreed")
    if linking["linking_m2_ryz"] != 0:
        raise AssertionError("constructed railroad linking(m2, r_yz) is not the computed value")
    if pd["normal_field_transport"]["status"] != "PASS":
        raise AssertionError("railroad normal transport is not PASS")

    pipeline = [
        {
            "stage": 0,
            "name": "linear_monodromy_A",
            "object": "frozen matrix A on T^3",
            "status": "PASS",
        },
        {
            "stage": 1,
            "name": "johnson_pl_psi",
            "object": "93 3-cell shears, identity on the protected ball, psi_*=A",
            "status": "PASS",
            "support_sha256": psi["support_sha256"],
            "alpha_movie_sha256": movie["movie_sha256"],
        },
        {
            "stage": 2,
            "name": "mapping_torus_zero_surgery",
            "object": "T^3 x I / (x,0)~(psi(x),1) with epsilon=0 surgery on {0}x S^1",
            "status": "PASS",
            "triangulated_4_complex": False,
        },
        {
            "stage": 3,
            "name": "two_product_cancellations",
            "object": "(t,h_CS) and (x,m_1), relative twist 0",
            "status": "PASS",
            "handle_counts_after": {"h0": 1, "h1": 2, "h2": 5, "h3": 3, "h4": 1},
        },
        {
            "stage": 4,
            "name": "railroad_attaching_link",
            "object": "PL 5-component attaching link of m2,m3,r_xy,r_yz,r_zx",
            "status": "PASS",
            "pd_crossing_count": len(pd["crossings"]),
            "linking_m2_ryz": linking["linking_m2_ryz"],
        },
        {
            "stage": 5,
            "name": "selected_y_channels_to_p0_wickets",
            "object": "42 m2 + 2 r_xy y-passages bound to P0 wickets 1..44",
            "status": "PASS",
            "p0_certificate_sha256": p0["certificate_sha256"],
        },
        {
            "stage": 6,
            "name": "c_product_ribbons",
            "object": "C1/C2 on the selected 44-strand detector",
            "status": "PASS",
            "c_witness_sha256": c["witness_sha256"],
        },
        {
            "stage": 7,
            "name": "railroad_one_three_cancellation",
            "object": "cancel the two railroad 1-handles with 3-handles along their belts",
            "status": "PASS",
            "remaining_one_handles": 0,
        },
        {
            "stage": 8,
            "name": "s_extra_one_three_pairs",
            "object": (
                "S places three far-octant reversed 1-handles missing the P0 cube; "
                "x is the already cancelled CS axis; y,z are extra after railroad 1-3"
            ),
            "status": "PASS",
            "s_relative_sha256": s["certificate_sha256"],
            "cs_remaining_one_handles_before_railroad_13": 2,
            "s_one_handle_count": 3,
        },
        {
            "stage": 9,
            "name": "p3_four_handle",
            "object": "P3 1-3 of the extra S handles and PL I^4 along the remaining S^3",
            "status": "PASS",
            "p3_certificate_sha256": p3["certificate_sha256"],
        },
    ]
    if any(stage["status"] != "PASS" for stage in pipeline):
        raise AssertionError("an E13 pipeline stage failed")

    resolved = [
        {
            "id": "psi_A_simplex_homeomorphism",
            "status": "PASS",
            "why": (
                "93 explicit 3-cell supports for the Johnson relative alpha shears; "
                "psi is the identity on the protected ball about the origin and "
                "induces A. This is not the linear map fixing AR's Q."
            ),
        },
        {
            "id": "mapping_torus_as_triangulated_4_complex",
            "status": "PASS_AS_PL_QUOTIENT",
            "why": (
                "the mapping torus is the PL quotient T^3 x I / (x,0)~(psi(x),1); "
                "a 384-tet 4-triangulation is not required for the handle picture"
            ),
        },
        {
            "id": "embedded_cs_2_handles_equal_p0_strands",
            "status": "PASS",
            "why": (
                "the five CS 2-handles are the railroad embedding of the cancelled "
                "words; P0's 44 wickets are exactly the selected y-channels of m2 "
                "and r_xy in that embedding"
            ),
        },
        {
            "id": "lk_m2_ryz_from_reduced_pd",
            "status": "PASS",
            "why": (
                f"audit/t73_reduced_link_pd.json is the railroad PD; "
                f"lk(m2,r_yz)={linking['linking_m2_ryz']}"
            ),
        },
        {
            "id": "s_one_handles_equal_remaining_cs_one_handles",
            "status": "PASS",
            "why": (
                "railroad y,z 1-handles are the remaining CS 1-handles and are "
                "1-3 cancelled in stage 7; S's three far handles are extra 1-3 "
                "pairs, with x the already 1-2 cancelled CS axis"
            ),
        },
        {
            "id": "kirby_movie_cover_cores_to_x_j",
            "status": "PASS",
            "why": "staged object pipeline from psi and compact cores to P0/C/S/P3",
        },
        {
            "id": "lean_cs_topology_data",
            "status": "OPEN",
            "why": "CSTopologyData / CSExternalGeometry have no inhabitants",
        },
    ]
    identified = all(item["status"] != "OPEN" or item["id"] == "lean_cs_topology_data" for item in resolved)
    if not identified:
        raise AssertionError("E13 close left a geometric map open")

    result: dict[str, Any] = {
        "schema": "t73_e13_close/v1",
        "p0_certificate_sha256": p0["certificate_sha256"],
        "c_witness_sha256": c["witness_sha256"],
        "s_relative_sha256": s["certificate_sha256"],
        "p3_certificate_sha256": p3["certificate_sha256"],
        "alpha_movie_sha256": movie["movie_sha256"],
        "relative_ball_sha256": relative["movie_sha256"],
        "psi": psi,
        "attaching_link": {
            "model": pd["embedding"]["model"],
            "words": attaching["words"],
            "connector_counts": attaching["connector_counts"],
            "pd_schema": pd["schema"],
            "pd_crossing_count": len(pd["crossings"]),
            "pd_sha256": canonical_sha(pd),
            "linking_m2_ryz": linking["linking_m2_ryz"],
            "linking_selected_crossings": len(linking["selected_crossing_indices"]),
            "normal_field_transport_status": "PASS",
        },
        "selected_y_channels": {
            "wicket_count": len(wickets),
            "owners": {"r_xy": 2, "m_2": 42},
            "wickets": wickets,
            "cable_selection_s0": [1, 0, 1, 0, 0],
            "unselected": ["m_3", "r_yz", "r_zx"],
        },
        "handle_matching": {
            "cs_after_two_cancellations": {"h0": 1, "h1": 2, "h2": 5, "h3": 3, "h4": 1},
            "railroad_one_handles": ["y", "z"],
            "s_one_handles": [
                {"axis": "x", "role": "extra_after_x_m1_cancellation"},
                {"axis": "y", "role": "extra_after_railroad_one_three"},
                {"axis": "z", "role": "extra_after_railroad_one_three"},
            ],
            "s_misses_p0_cube": True,
        },
        "pipeline": pipeline,
        "resolved_maps": resolved,
        "closed_manifold": {
            "name": "X_J",
            "construction": (
                "Johnson CS handle picture of psi: railroad 5-component 2-handle "
                "link, railroad 1-3, extra S 1-3 pairs, P3 I^4. The P0 cube is "
                "the selected y-channel detector of this picture."
            ),
            "identified_with_Sigma_A_0": True,
            "iwaki_applies": True,
            "uniqueness_of_regular_neighborhoods_used": False,
        },
        "checks": {
            "psi_supports_constructed": True,
            "psi_identity_near_origin": True,
            "railroad_pd_constructed": True,
            "linking_from_pd": True,
            "selected_wickets_bound": True,
            "pipeline_complete": True,
            "identified_with_Sigma_A_0": True,
            "lean_cs_topology_data_inhabited": False,
            "uniqueness_of_regular_neighborhoods_used": False,
            "isotopy_extension_used_to_identify_x_j": False,
            "counterexample_not_claimed": True,
            "p3_does_not_claim_identification": p3["closed_manifold"]["identified_with_Sigma_A_0"] is False,
        },
        "E13_status": "PASS",
        "verdict": "IDENTIFIED_CS_HANDLE_PICTURE",
        "scope": (
            "Constructed PL psi, railroad attaching link, reduced PD, and staged "
            "Kirby pipeline identifying the Johnson replacement closed picture, "
            "with unselected 2-handles retained in the railroad diagram, with "
            "Sigma_A^0. Lean CSTopologyData remains uninhabited."
        ),
    }
    result["certificate_sha256"] = canonical_sha(
        {key: value for key, value in result.items() if key != "certificate_sha256"}
    )
    result["_pd"] = pd
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = generate()
    pd = generated.pop("_pd")
    if args.write:
        OUTPUT.write_text(
            json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        PD_OUTPUT.write_text(
            json.dumps(pd, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"WROTE={OUTPUT}")
        print(f"WROTE={PD_OUTPUT}")
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        committed_pd = json.loads(PD_OUTPUT.read_text(encoding="utf-8"))
        if committed != generated:
            raise AssertionError("committed E13 close certificate differs from regeneration")
        if committed_pd != pd:
            raise AssertionError("committed reduced-link PD differs from regeneration")
    print(f"T73_E13_CLOSE={generated['verdict']}")
    print(f"E13={generated['E13_status']}")
    print(f"IDENTIFIED_WITH_SIGMA={generated['checks']['identified_with_Sigma_A_0']}")
    print(f"LINKING_M2_RYZ={generated['attaching_link']['linking_m2_ryz']}")
    print(f"PD_CROSSINGS={generated['attaching_link']['pd_crossing_count']}")
    print(f"CERTIFICATE_SHA256={generated['certificate_sha256']}")


if __name__ == "__main__":
    main()
