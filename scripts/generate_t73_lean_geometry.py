#!/usr/bin/env python3
"""Emit Lean index data for the E12/E13 certificates and Johnson transvections.

Regenerate with --write.  The generated modules record SHA-256 digests,
integer counts, and the compressed Johnson row-add factorization of A.
They do not inhabit ExternalGeometry, CSExternalGeometry, or CSTopologyData.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX_OUT = ROOT / "Smooth4PC" / "T73CertificateIndex.lean"
TRANSVECTION_OUT = ROOT / "Smooth4PC" / "T73JohnsonTransvections.lean"
E12 = ROOT / "audit" / "t73_e12_s4_reduction.json"
E13_CLOSE = ROOT / "audit" / "t73_e13_close.json"
E13_ID = ROOT / "audit" / "t73_e13_identification.json"
PD = ROOT / "audit" / "t73_reduced_link_pd.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_index(e12: dict[str, Any], close: dict[str, Any], ident: dict[str, Any], pd: dict[str, Any]) -> str:
    linking = close["attaching_link"]["linking_m2_ryz"]
    channels = close["selected_y_channels"]
    wickets = channels.get("wicket_count", len(channels.get("wickets", [])))
    crossings = close["attaching_link"]["pd_crossing_count"]
    if len(pd["crossings"]) != crossings:
        raise AssertionError("railroad PD crossing count disagrees with the E13 close certificate")
    psi_moves = close["psi"]["move_count"]
    return f"""-- Generated from the committed E12/E13 certificates.
-- Regenerate with scripts/generate_t73_lean_geometry.py --write; do not edit.

import Smooth4PC.T73Finite

namespace Smooth4PC.T73

/-!
Index data for the E12 empty-link reduction and the E13 Johnson CS handle
picture.  These definitions record certificate digests and integer counts.
They do not inhabit `ExternalGeometry`, `CSExternalGeometry`, or
`CSTopologyData`.
-/

def e12S4ReductionSha256 : String :=
  "{e12["certificate_sha256"]}"

def e13CloseSha256 : String :=
  "{close["certificate_sha256"]}"

def e13IdentificationSha256 : String :=
  "{ident["certificate_sha256"]}"

def e13RailroadPdSha256 : String :=
  "{close["attaching_link"]["pd_sha256"]}"

def e13AlphaMovieSha256 : String :=
  "{close["alpha_movie_sha256"]}"

def p3FourHandleSha256 : String :=
  "{close["p3_certificate_sha256"]}"

def linkingM2Ryz : Int := {linking}

def selectedWicketCount : Nat := {wickets}

def johnsonPsiSupportCount : Nat := {psi_moves}

def railroadPdCrossingCount : Nat := {crossings}

theorem linkingM2Ryz_eq_zero : linkingM2Ryz = 0 := rfl

theorem selectedWicketCount_eq_44 : selectedWicketCount = 44 := rfl

theorem johnsonPsiSupportCount_eq_93 : johnsonPsiSupportCount = 93 := rfl

theorem railroadPdCrossingCount_eq_1958 :
    railroadPdCrossingCount = 1958 :=
  rfl

end Smooth4PC.T73
"""


def render_transvections(ops: list[dict[str, Any]], unit_count: int) -> str:
    items = ",\n  ".join(
        f"⟨{op['target']}, {op['source']}, {op['coefficient']}⟩" for op in ops
    )
    return f"""-- Generated from scripts/factor_t73_matrix_johnson.py.
-- Regenerate with scripts/generate_t73_lean_geometry.py --write; do not edit.

import Smooth4PC.T73Finite

namespace Smooth4PC.T73

/-!
Compressed Johnson `alpha_ij` row additions whose product is `matrixA`.
This is the linear monodromy of the E13 PL automorphism `psi`, not a
4-manifold triangulation and not an inhabitant of `ExternalGeometry`.
-/

/-- Add `coefficient` times the source row to the target row. -/
structure RowAdd where
  target : Fin 3
  source : Fin 3
  coefficient : Int
  deriving DecidableEq, Repr

def applyRowAdd (m : Matrix3) (op : RowAdd) : Matrix3 :=
  fun row col =>
    if row = op.target then m row col + op.coefficient * m op.source col
    else m row col

def applyRowAdds (ops : List RowAdd) (m : Matrix3) : Matrix3 :=
  ops.foldl applyRowAdd m

def identity3 : Matrix3 := identityEntry

/-- Construction transvections: start from the identity and recover `A`. -/
def johnsonConstructionTransvections : List RowAdd :=
  [{items}]

def johnsonCompressedMoveCount : Nat :=
  johnsonConstructionTransvections.length

def johnsonUnitAlphaMoveCount : Nat :=
  (johnsonConstructionTransvections.map fun op => op.coefficient.natAbs).sum

theorem johnsonCompressedMoveCount_eq_45 :
    johnsonCompressedMoveCount = 45 :=
  rfl

theorem johnsonUnitAlphaMoveCount_eq_93 :
    johnsonUnitAlphaMoveCount = {unit_count} :=
  rfl

theorem johnsonConstruction_eq_matrixA :
    applyRowAdds johnsonConstructionTransvections identity3 = matrixA := by
  ext row col
  fin_cases row <;> fin_cases col <;> decide

end Smooth4PC.T73
"""


def generate_index() -> str:
    e12 = json_load(E12)
    close = json_load(E13_CLOSE)
    ident = json_load(E13_ID)
    pd = json_load(PD)
    if close["attaching_link"]["linking_m2_ryz"] != 0:
        raise AssertionError("Lean index refuses a nonzero railroad linking number")
    if ident["e13_close_sha256"] != close["certificate_sha256"]:
        raise AssertionError("E13 identification is not bound to the close digest")
    return render_index(e12, close, ident, pd)


def generate_transvections() -> str:
    factor = load("factor_t73_matrix_johnson").generate()
    ops = factor["construction_transvections"]
    if factor["unit_alpha_move_count"] != 93:
        raise AssertionError("Johnson unit alpha-move count is not 93")
    if factor["compressed_move_count"] != 45:
        raise AssertionError("Johnson compressed transvection count is not 45")
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    rebuilt = load("factor_t73_matrix_johnson").apply_all(identity, ops)
    if rebuilt != load("factor_t73_matrix_johnson").A:
        raise AssertionError("Johnson construction transvections do not recover A")
    for op in ops:
        if op["target"] == op["source"]:
            raise AssertionError("Johnson transvection has equal target and source")
        if op["kind"] != "add":
            raise AssertionError("Johnson factorization is not a row-add list")
    return render_transvections(ops, factor["unit_alpha_move_count"])


def generate() -> dict[str, str]:
    return {
        "index": generate_index(),
        "transvections": generate_transvections(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = generate()
    if args.write:
        INDEX_OUT.write_text(generated["index"], encoding="utf-8")
        TRANSVECTION_OUT.write_text(generated["transvections"], encoding="utf-8")
        print(f"WROTE={INDEX_OUT}")
        print(f"WROTE={TRANSVECTION_OUT}")
    if args.check:
        if INDEX_OUT.read_text(encoding="utf-8") != generated["index"]:
            raise AssertionError("T73CertificateIndex.lean is stale")
        if TRANSVECTION_OUT.read_text(encoding="utf-8") != generated["transvections"]:
            raise AssertionError("T73JohnsonTransvections.lean is stale")
        print("T73_LEAN_GEOMETRY_DATA=PASS")
    if not args.write and not args.check:
        print(generated["index"])


if __name__ == "__main__":
    main()
