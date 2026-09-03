#!/usr/bin/env python3
"""Build an exact rational triangulated coordinate model for the AR 3-torus.

Coordinates are multiplied by two.  Thus the fundamental cube is [-2,2]^3,
the period is 4, and the AR spine vertices Q and Qbar are (-1,-1,-1) and
(1,1,1).  This stage constructs only the torus and coordinate networks; it
does not claim that an explicit handlebody-preserving psi_A has been built.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def add(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(a[i] + b[i] for i in range(3))  # type: ignore[return-value]


def det3(rows: list[list[int]]) -> int:
    return (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )


def tet_volume6(tet: list[tuple[int, int, int]]) -> int:
    base = tet[0]
    rows = [[tet[i][j] - base[j] for j in range(3)] for i in range(1, 4)]
    return det3(rows)


def quotient_vertex(v: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((x + 2) % 4 for x in v)  # type: ignore[return-value]


def generate() -> dict[str, Any]:
    axes = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    tetrahedra: list[list[tuple[int, int, int]]] = []
    for origin in itertools.product(range(-2, 2), repeat=3):
        o = tuple(origin)
        for permutation in itertools.permutations(range(3)):
            v0 = o
            v1 = add(v0, axes[permutation[0]])
            v2 = add(v1, axes[permutation[1]])
            v3 = add(v2, axes[permutation[2]])
            tetrahedra.append([v0, v1, v2, v3])
    if len(tetrahedra) != 4**3 * 6:
        raise AssertionError("unexpected Freudenthal tetrahedron count")
    if any(tet_volume6(tet) == 0 for tet in tetrahedra):
        raise AssertionError("degenerate cover tetrahedron")

    faces: Counter[tuple[tuple[int, int, int], ...]] = Counter()
    for tet in tetrahedra:
        for omitted in range(4):
            face = tuple(sorted(tet[:omitted] + tet[omitted + 1 :]))
            faces[face] += 1
    boundary = [face for face, count in faces.items() if count == 1]
    pairings = []
    seen: set[tuple[tuple[int, int, int], ...]] = set()
    boundary_set = set(boundary)
    for face in boundary:
        if face in seen:
            continue
        axis = next(
            (i for i in range(3) if all(v[i] == -2 for v in face) or all(v[i] == 2 for v in face)),
            None,
        )
        if axis is None:
            raise AssertionError("cover boundary face is not on a fundamental-cube face")
        direction = 4 if all(v[axis] == -2 for v in face) else -4
        partner = tuple(sorted(tuple(x + (direction if i == axis else 0) for i, x in enumerate(v)) for v in face))
        if partner not in boundary_set:
            raise AssertionError("opposite boundary triangulation does not match")
        seen.add(face)
        seen.add(partner)
        pairings.append({"axis": axis, "source": [list(v) for v in face], "target": [list(v) for v in partner]})
    if len(seen) != len(boundary):
        raise AssertionError("not every boundary triangle is paired")

    q = (-1, -1, -1)
    qbar = (1, 1, 1)
    networks: dict[str, list[dict[str, Any]]] = {"L_B": [], "L_D": []}
    for name, base in (("L_B", q), ("L_D", qbar)):
        for axis in range(3):
            points = []
            for offset in range(5):
                value = list(base)
                value[axis] = base[axis] + offset
                points.append(value)
            networks[name].append({"axis": axis, "cover_polyline": points, "closed_mod_period": 4})

    model: dict[str, Any] = {
        "schema": "t73_ar_torus_model/v1",
        "coordinate_scale": 2,
        "period_scaled": 4,
        "fundamental_cube_scaled": [[-2, -2, -2], [2, 2, 2]],
        "quotient_vertex_count": len({quotient_vertex(v) for tet in tetrahedra for v in tet}),
        "cover_tetrahedra": [[list(v) for v in tet] for tet in tetrahedra],
        "boundary_face_pairings": pairings,
        "heegaard_spine_networks": networks,
        "section_arc_scaled": [list(q), list(qbar)],
        "section_ball_status": "OPEN: regular-neighborhood triangulation not yet certified",
        "psi_A_status": "OPEN: no handlebody-preserving PL map supplied at this stage",
        "checks": {
            "cover_tetrahedra": len(tetrahedra),
            "boundary_triangles": len(boundary),
            "boundary_pairs": len(pairings),
            "all_cover_tetrahedra_nondegenerate": True,
            "all_boundary_faces_paired_by_period_translation": True,
        },
    }
    model["model_sha256"] = canonical_sha(model)
    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    generated = generate()
    if args.output:
        args.output.write_text(json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        print("T73_AR_TORUS_MODEL=PASS")
        print(f"MODEL_SHA256={generated['model_sha256']}")
        return
    if not args.output:
        print(json.dumps(generated, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
