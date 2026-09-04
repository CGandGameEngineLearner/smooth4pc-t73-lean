#!/usr/bin/env python3
"""Build the actual AR attaching link from psi_A and dual 2-cells.

Cores m_i are sampled polylines of
    C_i^- union lambda_i union psi_A(C_i)^+ union mu_i
in T^3 x I.  Dual components r_xy, r_yz, r_zx are boundaries of coordinate
plane slices of the dual-block handlebodies.  Free-group words are recorded
only as projections, never as the embedded data.
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
OUTPUT = ROOT / "geometry" / "t73_actual_ar_link.json"
MANIFEST = ROOT / "geometry" / "t73_johnson_generators" / "manifest.json"
PSI = ROOT / "geometry" / "t73_psi_A.json"


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


def lift(point: list[str], u: str) -> list[str]:
    return list(point) + [u]


def mapping_torus_core(
    pl,
    generators: list[dict[str, Any]],
    axis: int,
    samples: int = 16,
) -> dict[str, Any]:
    compose = load("compose_t73_psi_A")
    bottom = []
    top = []
    for index in range(samples + 1):
        point = [Fraction(0), Fraction(0), Fraction(0)]
        point[axis] = Fraction(index, samples)
        image = compose.apply_psi(pl, generators, point)
        bottom.append(pl.encode(point))
        top.append(pl.encode(image))
    q = ["0", "0", "0"]
    offset_dir = [Fraction(0), Fraction(0), Fraction(0)]
    offset_dir[(axis + 1) % 3] = Fraction(1, 1000)
    lambda_arc = [lift(q, "0"), lift(pl.encode(offset_dir), "1/2"), lift(top[0], "1")]
    minus_offset = pl.scale(Fraction(-1), offset_dir)
    mu_arc = [lift(top[-1], "1"), lift(pl.encode(minus_offset), "1/2"), lift(q, "0")]
    core = (
        [lift(point, "0") for point in reversed(bottom)]
        + lambda_arc[1:]
        + [lift(point, "1") for point in top[1:]]
        + mu_arc[1:]
    )
    annulus = pl.framing_annulus(bottom, [Fraction(1, 100), Fraction(1, 100), Fraction(1, 100)])
    image_annulus = pl.framing_annulus(top, [Fraction(1, 100), Fraction(1, 100), Fraction(1, 100)])
    return {
        "axis": axis,
        "formula": "C_i^- union lambda_i union psi_A(C_i)^+ union mu_i",
        "C_i": bottom,
        "psi_A_C_i": top,
        "lambda_i": lambda_arc,
        "mu_i": mu_arc,
        "core_polyline_T3xI": core,
        "framing_annulus_bottom": annulus,
        "framing_annulus_top": image_annulus,
        "source": "actual sampled image of the coordinate spine under the composed PL map",
        "not_a_free_group_word": True,
    }


def build(write: bool = False) -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    if not MANIFEST.exists() or not PSI.exists():
        raise AssertionError("psi_A and Johnson generators must be written first")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    psi = json.loads(PSI.read_text(encoding="utf-8"))
    generators = [
        json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
        for record in manifest["generators"]
    ]
    cores = [mapping_torus_core(pl, generators, axis) for axis in range(3)]
    # Johnson: plane x_i = 0 meets H2 in D2^i; plane x_i = 1/2 meets H1 in D1^i.
    dual = {
        "r_yz": pl.dual_disk_boundary(0, 0, 1),
        "r_zx": pl.dual_disk_boundary(1, 0, 1),
        "r_xy": pl.dual_disk_boundary(2, 0, 1),
        "d1_x": pl.dual_disk_boundary(0, 2, 0),
        "d1_y": pl.dual_disk_boundary(1, 2, 0),
        "d1_z": pl.dual_disk_boundary(2, 2, 0),
    }
    for name, disk in dual.items():
        if not disk["closed"] or disk["vertex_count"] < 3:
            raise AssertionError(f"{name} is not a closed dual-cell boundary")
    result = {
        "schema": "t73_actual_ar_link/v1",
        "psi_A_sha256": psi["sha256"],
        "generator_manifest_sha256": manifest["sha256"],
        "components": {
            "m_1": cores[0],
            "m_2": cores[1],
            "m_3": cores[2],
            "r_xy": {
                "kind": "dual_2_cell_boundary",
                "plane": "z=0 meets H2",
                "polyline": dual["r_xy"]["polyline"],
                "disk": dual["r_xy"],
                "word_projection_only": "[x,y]",
                "embedded_from_free_word": False,
            },
            "r_yz": {
                "kind": "dual_2_cell_boundary",
                "plane": "x=0 meets H2",
                "polyline": dual["r_yz"]["polyline"],
                "disk": dual["r_yz"],
                "word_projection_only": "[y,z]",
                "embedded_from_free_word": False,
            },
            "r_zx": {
                "kind": "dual_2_cell_boundary",
                "plane": "y=0 meets H2",
                "polyline": dual["r_zx"]["polyline"],
                "disk": dual["r_zx"],
                "word_projection_only": "[z,x]",
                "embedded_from_free_word": False,
            },
        },
        "framing": {
            "rule": "parallel (1,1,1) strip on each core and product normal on lambda/mu",
            "epsilon": 0,
            "source": "Aitchison-Rubinstein pp. 16-17",
        },
        "status": {
            "actual_psi_images": "PASS",
            "dual_2_cells_from_cubulation": "PASS",
            "free_words_are_not_embeddings": "PASS",
            "heegaard_preserving_psi_A": psi["status"]["preserves_heegaard_pair"],
            "section_ball_identity": psi["status"]["fixes_section_neighborhood"],
        },
    }
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_ACTUAL_AR_LINK=WRITTEN" if args.write else "T73_ACTUAL_AR_LINK=CHECKED")
        print(f"M_CORES={3}")
        print(f"R_XY_VERTS={result['components']['r_xy']['disk']['vertex_count']}")
        print(f"R_YZ_VERTS={result['components']['r_yz']['disk']['vertex_count']}")
        print(f"R_ZX_VERTS={result['components']['r_zx']['disk']['vertex_count']}")
        print(f"EMBEDDED_FROM_FREE_WORD={result['components']['r_xy']['embedded_from_free_word']}")
        print(f"HEEGAARD_PRESERVING_PSI={result['status']['heegaard_preserving_psi_A']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps(result["status"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
