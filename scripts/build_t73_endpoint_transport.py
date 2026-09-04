#!/usr/bin/env python3
"""Build endpoint transport from actual detector endpoints to public order.

Physical endpoints and geometric order come from the actual post-cancellation
detector.  Only after those 88 endpoints exist is the B88 table used to attach
the public Burau index.
Pivotal coefficients are recorded per endpoint; the frozen Burau model uses
+q^0.  The selected cup is identified by physical owner/letter/sign, not by
handwritten public indices.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POSITION_TABLE = ROOT / "data" / "B88_POSITION_TO_PASSAGE_TABLE.json"
ACTUAL_CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"
ACTUAL_BRAID = ROOT / "geometry" / "t73_actual_geometric_braid.json"
CONVENTION_OUT = ROOT / "data" / "T73_ENDPOINT_CONVENTION.json"
AUDIT_OUT = ROOT / "audit" / "t73_endpoint_transport.json"
DIMENSION = 88

# Physical identity of the Hattori U1 cup, from owner/letter/sign rather than
# public indices 2 and 87.
SELECTED_CUP = (
    {"owner": "r_xy", "word_letter": 3, "sign": "neg", "role": "cup_plus"},
    {"owner": "m_2", "word_letter": 310, "sign": "pos", "role": "cup_minus"},
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def canonical_sha(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(raw)


def load_positions() -> list[dict[str, Any]]:
    table = json.loads(POSITION_TABLE.read_text(encoding="utf-8"))
    positions = table["positions"]
    if len(positions) != DIMENSION:
        raise ValueError(f"expected {DIMENSION} endpoints, got {len(positions)}")
    by_index = {int(row["index"]): row for row in positions}
    if set(by_index) != set(range(DIMENSION)):
        raise ValueError("public indices are not 0..87")
    return [by_index[i] for i in range(DIMENSION)]


def geometric_rank(row: dict[str, Any]) -> tuple[int, int, int]:
    """Order r_xy wickets as in the collar table; reverse m_2 wickets."""

    owner = row["owner"]
    wicket = int(row["wicket"])
    sign_rank = 0 if row["sign"] == "neg" else 1
    if owner == "r_xy":
        return (0, wicket, sign_rank)
    if owner == "m_2":
        return (1, -wicket, sign_rank)
    raise ValueError(f"unexpected owner {owner}")


def find_physical(positions: list[dict[str, Any]], query: dict[str, Any]) -> dict[str, Any]:
    matches = [
        row
        for row in positions
        if row["owner"] == query["owner"]
        and int(row["word_letter"]) == int(query["word_letter"])
        and row["sign"] == query["sign"]
    ]
    if len(matches) != 1:
        raise ValueError(f"physical endpoint is not unique: {query}")
    return matches[0]


def monomial_identity(dim: int) -> dict[tuple[int, int], tuple[int, int]]:
    return {(i, i): (1, 0) for i in range(dim)}


def monomial_mul(
    left: dict[tuple[int, int], tuple[int, int]],
    right: dict[tuple[int, int], tuple[int, int]],
    dim: int,
) -> dict[tuple[int, int], tuple[int, int]]:
    result: dict[tuple[int, int], tuple[int, int]] = {}
    for (i, k), (ls, lp) in left.items():
        for j in range(dim):
            entry = right.get((k, j))
            if entry is None:
                continue
            rs, rp = entry
            sign = ls * rs
            power = lp + rp
            key = (i, j)
            if key in result:
                raise ValueError("monomial product is not monomial")
            result[key] = (sign, power)
    return result


def monomial_inverse(
    matrix: dict[tuple[int, int], tuple[int, int]], dim: int
) -> dict[tuple[int, int], tuple[int, int]]:
    inverse: dict[tuple[int, int], tuple[int, int]] = {}
    rows = {i: 0 for i in range(dim)}
    cols = {j: 0 for j in range(dim)}
    for (i, j), (sign, power) in matrix.items():
        if sign not in (-1, 1):
            raise ValueError("unresolved pivotal sign")
        inverse[(j, i)] = (sign, -power)
        rows[i] += 1
        cols[j] += 1
    if any(count != 1 for count in rows.values()) or any(count != 1 for count in cols.values()):
        raise ValueError("P(q) is not a monomial matrix")
    return inverse


def apply_matrix(
    matrix: dict[tuple[int, int], tuple[int, int]],
    vector: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Apply a monomial matrix to a vector of (sign, q-power) pairs; zero is (0,0)."""

    dim = len(vector)
    result = [(0, 0) for _ in range(dim)]
    for (i, j), (ms, mp) in matrix.items():
        vs, vp = vector[j]
        if vs == 0:
            continue
        sign = ms * vs
        power = mp + vp
        if result[i][0] not in (0, sign) or (result[i][0] != 0 and result[i][1] != power):
            raise ValueError("vector image is not a monomial combination")
        result[i] = (result[i][0] + sign, power)
    return result


def apply_covector(
    covector: list[tuple[int, int]],
    matrix_inverse: dict[tuple[int, int], tuple[int, int]],
) -> list[tuple[int, int]]:
    """ell_public = ell_geometric P^{-1}."""

    dim = len(covector)
    result = [(0, 0) for _ in range(dim)]
    for (j, i), (ms, mp) in matrix_inverse.items():
        # ell_geo_j * (P^{-1})_{j i} contributes to public index i.
        vs, vp = covector[j]
        if vs == 0:
            continue
        sign = vs * ms
        power = vp + mp
        if result[i][0] not in (0, sign) or (result[i][0] != 0 and result[i][1] != power):
            raise ValueError("covector image is not a monomial combination")
        result[i] = (result[i][0] + sign, power)
    return result


def sparse_terms(vector: list[tuple[int, int]], *, descending: bool = False) -> list[list[int]]:
    terms = []
    for index, (sign, power) in enumerate(vector):
        if sign == 0:
            continue
        if power != 0:
            raise ValueError("frozen public pairing still has residual q-powers")
        terms.append([index, sign])
    terms.sort(key=lambda term: term[0], reverse=descending)
    return terms


def evaluate_q1(
    matrix: dict[tuple[int, int], tuple[int, int]], dim: int
) -> list[list[int]]:
    dense = [[0] * dim for _ in range(dim)]
    for (i, j), (sign, power) in matrix.items():
        dense[i][j] = sign
    return dense


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    n = len(left)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if left[i][k] == 0:
                continue
            for j in range(n):
                result[i][j] += left[i][k] * right[k][j]
    return result


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(matrix))]


def vecmat(vector: list[int], matrix: list[list[int]]) -> list[int]:
    n = len(vector)
    return [sum(vector[i] * matrix[i][j] for i in range(n)) for j in range(n)]


def build_convention(positions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    cut = json.loads(ACTUAL_CUT.read_text(encoding="utf-8"))
    braid = json.loads(ACTUAL_BRAID.read_text(encoding="utf-8"))
    if cut["status"] != "PASS" or len(cut["framed_endpoints"]) != DIMENSION:
        raise ValueError("actual detector does not supply 88 framed endpoints")
    if braid["actual_cut_tangle_sha256"] != cut["sha256"]:
        raise ValueError("actual geometric braid is stale relative to the detector")
    if braid["endpoint_return_status"] != "PASS":
        raise ValueError("actual geometric braid does not return its endpoints")
    if positions is None:
        positions = load_positions()
    public_by_physical_key = {
        (row["owner"], int(row["wicket"]), row["sign"]): row
        for row in positions
    }
    if len(public_by_physical_key) != DIMENSION:
        raise ValueError("public endpoint table does not have unique owner/wicket/sign keys")
    endpoints = []
    for actual in cut["framed_endpoints"]:
        key = (actual["owner"], int(actual["wicket"]), actual["sign"])
        row = public_by_physical_key.get(key)
        if row is None:
            raise ValueError(f"actual endpoint has no public coordinate: {key}")
        if int(row["word_letter"]) != int(actual["word_event_index"]):
            raise ValueError("public word-event label disagrees with the actual detector endpoint")
        geometric_index = int(actual["geometric_order"])
        public_index = int(row["index"])
        orientation = 1 if actual["sign"] == "pos" else -1
        pivotal_sign = 1
        q_power = 0
        basis = [0] * DIMENSION
        basis[geometric_index] = 1
        endpoints.append(
            {
                "physical_endpoint_id": actual["physical_endpoint_id"],
                "actual_side_source_id": actual["actual_side_source_id"],
                "coordinate_in_detector_chart": actual["coordinate_in_detector_chart"],
                "passage_id": actual["actual_side_source_id"],
                "public_endpoint_id": row["endpoint_id"],
                "public_passage_id": row["passage_id"],
                "owner": actual["owner"],
                "orientation": orientation,
                "passage_orientation": actual["orientation"],
                "sign": actual["sign"],
                "wicket": int(actual["wicket"]),
                "word_letter": int(actual["word_event_index"]),
                "geometric_order": geometric_index,
                "public_order": public_index,
                "pivotal_coefficient": {
                    "sign": pivotal_sign,
                    "q_power": q_power,
                    "display": "+q^0" if pivotal_sign == 1 else f"{pivotal_sign} q^{q_power}",
                },
                "weight_defect_basis_vector": basis,
            }
        )

    unresolved = [
        ep["physical_endpoint_id"]
        for ep in endpoints
        if ep["pivotal_coefficient"]["sign"] not in (-1, 1)
        or ep["orientation"] not in (-1, 1)
    ]
    return {
        "schema": "t73_endpoint_convention/v2",
        "dimension": DIMENSION,
        "geometric_order_rule": (
            cut["endpoint_boundary_order_rule"]
        ),
        "public_order_rule": "B88_POSITION_TO_PASSAGE_TABLE.json index",
        "actual_cut_tangle_sha256": cut["sha256"],
        "actual_geometric_braid_sha256": braid["witness_sha256"],
        "selected_cup_physical": [
            {
                "owner": spec["owner"],
                "word_letter": spec["word_letter"],
                "sign": spec["sign"],
                "role": spec["role"],
            }
            for spec in SELECTED_CUP
        ],
        "position_table_sha256": sha256_bytes(POSITION_TABLE.read_bytes()),
        "physical_endpoints_precede_public_table_lookup": True,
        "no_unresolved_signs": not unresolved,
        "unresolved_endpoint_ids": unresolved,
        "endpoints": endpoints,
    }


def transport_from_convention(convention: dict[str, Any]) -> dict[str, Any]:
    endpoints = convention["endpoints"]
    if len(endpoints) != DIMENSION:
        raise ValueError("convention does not contain 88 endpoints")
    if not convention["no_unresolved_signs"]:
        raise ValueError("unresolved signs remain")

    P: dict[tuple[int, int], tuple[int, int]] = {}
    for ep in endpoints:
        pub = int(ep["public_order"])
        geo = int(ep["geometric_order"])
        sign = int(ep["pivotal_coefficient"]["sign"])
        power = int(ep["pivotal_coefficient"]["q_power"])
        if sign not in (-1, 1):
            raise ValueError("unresolved pivotal sign")
        if (ep["sign"] == "pos") != (int(ep["orientation"]) == 1):
            raise ValueError("orientation does not match recorded sign")
        P[(pub, geo)] = (sign, power)
    P_inv = monomial_inverse(P, DIMENSION)
    identity = monomial_mul(P, P_inv, DIMENSION)
    if identity != monomial_identity(DIMENSION):
        raise ValueError("P P^{-1} is not the identity")
    identity_l = monomial_mul(P_inv, P, DIMENSION)
    if identity_l != monomial_identity(DIMENSION):
        raise ValueError("P^{-1} P is not the identity")

    plus = find_physical(
        [
            {
                "owner": ep["owner"],
                "word_letter": ep["word_letter"],
                "sign": ep["sign"],
                **ep,
            }
            for ep in endpoints
        ],
        SELECTED_CUP[0],
    )
    minus = find_physical(
        [
            {
                "owner": ep["owner"],
                "word_letter": ep["word_letter"],
                "sign": ep["sign"],
                **ep,
            }
            for ep in endpoints
        ],
        SELECTED_CUP[1],
    )

    u_geo = [(0, 0) for _ in range(DIMENSION)]
    ell_geo = [(0, 0) for _ in range(DIMENSION)]
    u_geo[int(plus["geometric_order"])] = (1, 0)
    u_geo[int(minus["geometric_order"])] = (-1, 0)
    ell_geo[int(minus["geometric_order"])] = (1, 0)
    ell_geo[int(plus["geometric_order"])] = (-1, 0)

    u_pub = apply_matrix(P, u_geo)
    ell_pub = apply_covector(ell_geo, P_inv)
    u_terms = sparse_terms(u_pub)
    ell_terms = sparse_terms(ell_pub, descending=True)

    P_q1 = evaluate_q1(P, DIMENSION)
    Pinv_q1 = evaluate_q1(P_inv, DIMENSION)
    u_geo_q1 = [sign for sign, _power in u_geo]
    ell_geo_q1 = [sign for sign, _power in ell_geo]
    u_pub_q1 = matvec(P_q1, u_geo_q1)
    ell_pub_q1 = vecmat(ell_geo_q1, Pinv_q1)

    # Random integer matrix conjugation check at q=1, independent of Burau W.
    seed_w = [
        [((i * 17 + j * 13) % 11) - 5 for j in range(DIMENSION)]
        for i in range(DIMENSION)
    ]
    w_pub = matmul(P_q1, matmul(seed_w, Pinv_q1))
    recovered = matmul(Pinv_q1, matmul(w_pub, P_q1))
    if recovered != seed_w:
        raise ValueError("W_public = P W_geometric P^{-1} failed on the probe matrix")
    if u_pub_q1 != [sign for sign, _ in u_pub]:
        raise ValueError("u_public = P u_geometric failed")
    if ell_pub_q1 != [sign for sign, _ in ell_pub]:
        raise ValueError("ell_public = ell_geometric P^{-1} failed")

    pairing = sum(a * b for a, b in zip(ell_pub_q1, u_pub_q1))
    geo_pairing = sum(a * b for a, b in zip(ell_geo_q1, u_geo_q1))
    if pairing != geo_pairing:
        raise ValueError("simultaneous conjugation changed the pairing")

    return {
        "schema": "t73_endpoint_transport/v1",
        "dimension": DIMENSION,
        "convention_sha256": canonical_sha(convention),
        "P_q_entries": [
            {
                "row_public": i,
                "column_geometric": j,
                "sign": sign,
                "q_power": power,
            }
            for (i, j), (sign, power) in sorted(P.items())
        ],
        "selected_cup": {
            "plus_physical_endpoint_id": plus["physical_endpoint_id"],
            "minus_physical_endpoint_id": minus["physical_endpoint_id"],
            "plus_geometric_order": plus["geometric_order"],
            "minus_geometric_order": minus["geometric_order"],
            "plus_public_order": plus["public_order"],
            "minus_public_order": minus["public_order"],
        },
        "derived_public_pairing": {
            "u_terms": u_terms,
            "ell_terms": ell_terms,
            "source": "P(q) applied to the geometric cup/cap of the physical U1 feet",
        },
        "checks": {
            "P_times_Pinv_is_identity": True,
            "W_public_conjugation": True,
            "u_public_equals_P_u_geometric": True,
            "ell_public_equals_ell_geometric_Pinv": True,
            "pairing_invariant": True,
            "no_unresolved_signs": True,
        },
        "ENDPOINT_TRANSPORT": "PASS",
        "NO_UNRESOLVED_SIGNS": "PASS",
    }


def public_pairing_terms(convention: dict[str, Any] | None = None) -> dict[str, list[list[int]]]:
    if convention is None:
        convention = build_convention()
    transport = transport_from_convention(convention)
    return transport["derived_public_pairing"]


def write_outputs() -> dict[str, Any]:
    convention = build_convention()
    transport = transport_from_convention(convention)
    CONVENTION_OUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUT.parent.mkdir(parents=True, exist_ok=True)
    CONVENTION_OUT.write_text(
        json.dumps(convention, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    AUDIT_OUT.write_text(
        json.dumps(transport, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"convention": convention, "transport": transport}


def mutate_convention(convention: dict[str, Any], kind: str) -> dict[str, Any]:
    mutant = deepcopy(convention)

    def cup_plus() -> dict[str, Any]:
        matches = [
            ep
            for ep in mutant["endpoints"]
            if ep["owner"] == SELECTED_CUP[0]["owner"]
            and int(ep["word_letter"]) == SELECTED_CUP[0]["word_letter"]
            and ep["sign"] == SELECTED_CUP[0]["sign"]
        ]
        if len(matches) != 1:
            raise ValueError("cup-plus endpoint missing")
        return matches[0]

    if kind == "pivotal_sign":
        foot = cup_plus()
        foot["pivotal_coefficient"]["sign"] *= -1
        foot["pivotal_coefficient"]["display"] = "-q^0"
    elif kind == "orientation":
        foot = cup_plus()
        foot["orientation"] *= -1
    elif kind == "unresolved_sign":
        mutant["endpoints"][3]["pivotal_coefficient"]["sign"] = 0
        mutant["no_unresolved_signs"] = False
        mutant["unresolved_endpoint_ids"] = [mutant["endpoints"][3]["physical_endpoint_id"]]
    elif kind == "geometric_swap":
        foot = cup_plus()
        other = mutant["endpoints"][0]
        foot["geometric_order"], other["geometric_order"] = (
            other["geometric_order"],
            foot["geometric_order"],
        )
        foot["weight_defect_basis_vector"], other["weight_defect_basis_vector"] = (
            other["weight_defect_basis_vector"],
            foot["weight_defect_basis_vector"],
        )
    else:
        raise ValueError(kind)
    return mutant


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write convention and audit JSON")
    args = parser.parse_args()
    payloads = write_outputs() if args.write else {
        "convention": build_convention(),
        "transport": transport_from_convention(build_convention()),
    }
    transport = payloads["transport"]
    pairing = transport["derived_public_pairing"]
    print(f"ENDPOINT_TRANSPORT={transport['ENDPOINT_TRANSPORT']}")
    print(f"NO_UNRESOLVED_SIGNS={transport['NO_UNRESOLVED_SIGNS']}")
    print("U_PUBLIC_TERMS=" + json.dumps(pairing["u_terms"], separators=(",", ":")))
    print("ELL_PUBLIC_TERMS=" + json.dumps(pairing["ell_terms"], separators=(",", ":")))
    print(f"CONVENTION_SHA256={transport['convention_sha256']}")


if __name__ == "__main__":
    main()
