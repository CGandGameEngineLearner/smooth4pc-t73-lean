#!/usr/bin/env python3
"""Verify the public T73 geometry evidence bundle.

This checks immutable identities and independently reruns the linear-time
global-descending calculation.  It deliberately does not turn stored geometry
certificate fields into proofs of their own semantics.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "public_geometry"


def load_descending_verifier():
    path = ROOT / "scripts" / "verify_t73_global_descending.py"
    spec = importlib.util.spec_from_file_location("t73_global_descending", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def load_json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def determinant3(columns: list[list[int]]) -> int:
    a, b, c = columns
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - b[0] * (a[1] * c[2] - a[2] * c[1])
        + c[0] * (a[1] * b[2] - a[2] * b[1])
    )


def main() -> None:
    sums = {}
    for line in (EVIDENCE / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected, name = line.split(maxsplit=1)
        sums[name] = expected
    for name, expected in sums.items():
        actual = sha256(EVIDENCE / name)
        if actual != expected:
            raise ValueError(f"{name}: {actual} != {expected}")

    cable = load_json("ACTUAL_PD_CABLE_UNIT_CERT.json")
    if cable["schema"] != "actual_pd_streaming_blackboard_2parallel_unit/v1":
        raise ValueError("unexpected cable-certificate schema")
    if cable["verdict"] != "PASS_ACTUAL_PD_GAUSS_RIBBON_UNIT_AND_227_SPLIT_DISKS":
        raise ValueError("cable certificate does not carry the frozen verdict")

    th1 = load_json("TH1_EXHAUSTIVE_ALL_ROW_GEOMETRY.json")
    th2 = load_json("TH2_EXHAUSTIVE_ALL_ROW_GEOMETRY.json")
    thxy = load_json("THXY_FULL_MACRO_P3FREE_HJ_CERT.json")
    if th1["schema"] != "t73_th1_exhaustive_all_row_geometry/v1":
        raise ValueError("unexpected TH1 schema")
    if th2["schema"] != "t73_th2_exhaustive_all_row_geometry/v1":
        raise ValueError("unexpected TH2 schema")
    if thxy["schema"] != "thxy_full_coordinate_macro_p3free_hj_basis/v1":
        raise ValueError("unexpected THXY schema")

    columns = thxy["HJ_basis"]["class_columns"]
    if determinant3(columns) != 1:
        raise ValueError("chosen-sphere column determinant is not one")
    for name, cert in (("TH1", th1), ("TH2", th2)):
        if any(value != "PASS" and not str(value).startswith("PASS_")
               for value in cert["verdict"].values()):
            raise ValueError(f"{name}: non-PASS frozen verdict field")
    if set(thxy["actual_cap_scalars"].values()) != {0}:
        raise ValueError("THXY scalar pair differs")

    actual = load_descending_verifier()(
        EVIDENCE / "t73_reduced_billiard.pd.json"
    )
    frozen = json.loads(
        (ROOT / "docs" / "proofs" / "T73_EVIDENCE_GLOBAL_DESCENDING.json")
        .read_text(encoding="utf-8")
    )
    actual.pop("pd_path", None)
    frozen.pop("pd_path", None)
    if actual != frozen:
        raise ValueError("fresh global-descending result differs from frozen receipt")

    print(f"FILES={len(sums)}")
    print("SHA256=PASS")
    print(f"SPHERE_DET={determinant3(columns)}")
    print("TH1_SCHEMA=PASS")
    print("TH2_SCHEMA=PASS")
    print("THXY_SCHEMA=PASS")
    print(f"PD_CROSSINGS={actual['pd_crossings']}")
    print("GLOBAL_DESCENDING=PASS")
    print("VERIFY=PASS")


if __name__ == "__main__":
    main()
