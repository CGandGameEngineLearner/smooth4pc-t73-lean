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
ACTUAL_AR = ROOT / "geometry" / "t73_actual_ar_link.json"
ACTUAL_CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"
ACTUAL_RECTANGLES = ROOT / "geometry" / "t73_actual_product_rectangles.json"
ACTUAL_LEFTOVERS = ROOT / "geometry" / "t73_actual_leftover_z_circles.json"
ACTUAL_BRAID = ROOT / "geometry" / "t73_actual_geometric_braid.json"
DUAL_DISKS = ROOT / "geometry" / "t73_johnson_dual_disk_movie.json"
SURFACE_TRANSPORT = ROOT / "geometry" / "t73_three_handle_surface_transport.json"
ACTUAL_SPHERES = ROOT / "geometry" / "t73_actual_sphere_system.json"
HEMISPHERES = ROOT / "geometry" / "t73_actual_hemisphere_movies.json"


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


def render_index(e12: dict[str, Any], close: dict[str, Any], ident: dict[str, Any], pd: dict[str, Any], actual: dict[str, Any]) -> str:
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

def actualArLinkSha256 : String := "{actual["ar"]["sha256"]}"
def actualCutTangleSha256 : String := "{actual["cut"]["sha256"]}"
def actualProductRectanglesSha256 : String := "{actual["rectangles"]["sha256"]}"
def actualLeftoverCirclesSha256 : String := "{actual["leftovers"]["sha256"]}"
def actualGeometricBraidSha256 : String := "{actual["braid"]["witness_sha256"]}"
def actualDualDiskMovieSha256 : String := "{actual["dual"]["sha256"]}"
def actualThreeHandleSurfacesSha256 : String := "{actual["surfaces"]["sha256"]}"
def actualSphereSystemSha256 : String := "{actual["spheres"]["sha256"]}"
def actualHemisphereMoviesSha256 : String := "{actual["hemispheres"]["sha256"]}"

def linkingM2Ryz : Int := {linking}

def selectedWicketCount : Nat := {wickets}

def johnsonPsiSupportCount : Nat := {psi_moves}

def railroadPdCrossingCount : Nat := {crossings}

def actualProductRectangleCount : Nat := {actual["rectangles"]["rectangle_count"]}
def actualLeftoverCircleCount : Nat := {actual["leftovers"]["circle_count"]}
def actualDualDiskFactorCount : Nat := {actual["dual"]["factor_count"]}
def actualThreeHandleCoreCounts : List Nat := {actual["surfaces"]["core_disk_counts"]}
def actualTCancellationBandCount : Nat := {len(actual["surfaces"]["surfaces"][0]["t_cancellation_band_hashes"])}
def actualXCancellationBandCount : Nat := {len(actual["surfaces"]["surfaces"][0]["x_cancellation_band_hashes"])}
def actualW2LasagnaMapVerified : Bool := {str(actual["hemispheres"]["actual_w2_lasagna_map"]).lower()}

theorem linkingM2Ryz_eq_zero : linkingM2Ryz = 0 := rfl

theorem selectedWicketCount_eq_44 : selectedWicketCount = 44 := rfl

theorem johnsonPsiSupportCount_eq_93 : johnsonPsiSupportCount = 93 := rfl

theorem railroadPdCrossingCount_eq_1958 :
    railroadPdCrossingCount = 1958 :=
  rfl

theorem actualProductRectangleCount_eq_44 : actualProductRectangleCount = 44 := rfl
theorem actualLeftoverCircleCount_eq_227 : actualLeftoverCircleCount = 227 := rfl
theorem actualDualDiskFactorCount_eq_93 : actualDualDiskFactorCount = 93 := rfl
theorem actualThreeHandleCoreCounts_eq :
    actualThreeHandleCoreCounts = [12578, 1824, 409] := rfl
theorem actualTCancellationBandCount_eq_6 : actualTCancellationBandCount = 6 := rfl
theorem actualXCancellationBandCount_eq_1513 : actualXCancellationBandCount = 1513 := rfl
theorem actualW2LasagnaMapVerified_eq_true : actualW2LasagnaMapVerified = true := rfl

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
    actual = {
        "ar": json_load(ACTUAL_AR),
        "cut": json_load(ACTUAL_CUT),
        "rectangles": json_load(ACTUAL_RECTANGLES),
        "leftovers": json_load(ACTUAL_LEFTOVERS),
        "braid": json_load(ACTUAL_BRAID),
        "dual": json_load(DUAL_DISKS),
        "surfaces": json_load(SURFACE_TRANSPORT),
        "spheres": json_load(ACTUAL_SPHERES),
        "hemispheres": json_load(HEMISPHERES),
    }
    if close["attaching_link"]["linking_m2_ryz"] != 0:
        raise AssertionError("Lean index refuses a nonzero railroad linking number")
    if ident["e13_close_sha256"] != close["certificate_sha256"]:
        raise AssertionError("E13 identification is not bound to the close digest")
    if actual["rectangles"]["cut_tangle_sha256"] != actual["cut"]["sha256"]:
        raise AssertionError("actual rectangle certificate is stale")
    if actual["surfaces"]["dual_disk_movie_sha256"] != actual["dual"]["sha256"]:
        raise AssertionError("actual surface transport is stale")
    if actual["hemispheres"]["sphere_system_sha256"] != actual["spheres"]["sha256"]:
        raise AssertionError("actual hemisphere certificate is stale")
    return render_index(e12, close, ident, pd, actual)


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
