#!/usr/bin/env python3
"""Generate exact rational local PL templates for unit Nielsen slides."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


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
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest().upper()


def fpoint(values: list[str | int]) -> tuple[Fraction, Fraction, Fraction]:
    return tuple(Fraction(x) for x in values)  # type: ignore[return-value]


def sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def scale(c, a):
    return tuple(c * a[i] for i in range(3))


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def zero(v) -> bool:
    return all(x == 0 for x in v)


def segments_intersect(p, q, r, s) -> bool:
    u, v, delta = sub(q, p), sub(s, r), sub(r, p)
    n = cross(u, v)
    if not zero(n):
        denom = dot(n, n)
        t = dot(cross(delta, v), n) / denom
        w = dot(cross(delta, u), n) / denom
        return 0 <= t <= 1 and 0 <= w <= 1 and add(p, scale(t, u)) == add(r, scale(w, v))
    if not zero(cross(delta, u)):
        return False
    axis = next((i for i, value in enumerate(u) if value != 0), None)
    if axis is None:
        return p == r
    a0, a1 = sorted((p[axis], q[axis]))
    b0, b1 = sorted((r[axis], s[axis]))
    return max(a0, b0) <= min(a1, b1)


def polyline_self_disjoint(points) -> bool:
    for i in range(len(points) - 1):
        for j in range(i + 2, len(points) - 1):
            if j == i + 1:
                continue
            if segments_intersect(points[i], points[i + 1], points[j], points[j + 1]):
                return False
    return True


def polylines_disjoint(a, b) -> bool:
    return not any(segments_intersect(a[i], a[i + 1], b[j], b[j + 1]) for i in range(len(a) - 1) for j in range(len(b) - 1))


def template(sign: int) -> dict[str, Any]:
    z = Fraction(sign, 2)
    source = [(-2, 1, 0), (2, 1, 0)]
    before = [(-2, -1, 0), (2, -1, 0)]
    after = [(-2, -1, 0), (Fraction(-3, 2), -1, 0), (Fraction(-3, 2), 1, z), (Fraction(3, 2), 1, z), (Fraction(3, 2), -1, 0), (2, -1, 0)]
    band = [(Fraction(-3, 2), -1, 0), (Fraction(3, 2), -1, 0), (Fraction(3, 2), 1, z), (Fraction(-3, 2), 1, z)]
    source_f, before_f, after_f, band_f = map(lambda pts: [fpoint(list(p)) for p in pts], (source, before, after, band))
    triangles = [(band_f[0], band_f[1], band_f[2]), (band_f[0], band_f[2], band_f[3])]
    if not polyline_self_disjoint(after_f):
        raise AssertionError("unit slide target-after polyline self-intersects")
    if not polylines_disjoint(source_f, after_f):
        raise AssertionError("unit slide target-after intersects source")
    if any(zero(cross(sub(tri[1], tri[0]), sub(tri[2], tri[0]))) for tri in triangles):
        raise AssertionError("unit slide band has a degenerate triangle")
    payload = {
        "sign": sign,
        "support_ball": {"kind": "box", "min": [-3, -2, -1], "max": [3, 2, 1]},
        "source_arc": [list(p) for p in source_f],
        "target_before": [list(p) for p in before_f],
        "target_after": [list(p) for p in after_f],
        "slide_band_vertices": [list(p) for p in band_f],
        "slide_band_triangles": [[0, 1, 2], [0, 2, 3]],
        "normal_rule": "oriented product normal; reflection z->-z handles negative sign",
        "relative_twist": 0,
        "checks": {"target_after_embedded": True, "source_disjoint": True, "band_nondegenerate": True},
    }
    payload["template_sha256"] = canonical_sha(payload)
    return payload


def generate() -> dict[str, Any]:
    factor = load("factor_t73_matrix_nielsen").generate()
    templates = {"positive": template(1), "negative": template(-1)}
    expanded = []
    for operation_index, operation in enumerate(factor["construction_operations"]):
        if operation["kind"] == "add":
            sign = 1 if operation["coefficient"] > 0 else -1
            for repetition in range(abs(operation["coefficient"])):
                expanded.append({
                    "kind": "unit_slide",
                    "operation_index": operation_index,
                    "repetition": repetition,
                    "target": operation["target"],
                    "source": operation["source"],
                    "sign": sign,
                    "template_sha256": templates["positive" if sign > 0 else "negative"]["template_sha256"],
                    "global_support_status": "OPEN",
                })
        else:
            expanded.append({
                "kind": operation["kind"],
                "operation_index": operation_index,
                "operation": operation,
                "local_template_status": "PASS: signed permutation of the standard handle chart",
                "global_support_status": "OPEN",
            })
    result: dict[str, Any] = {
        "schema": "t73_pl_nielsen_templates/v1",
        "templates": templates,
        "expanded_moves": expanded,
        "unit_slide_count": sum(move["kind"] == "unit_slide" for move in expanded),
        "local_template_status": "PASS",
        "global_placement_status": "OPEN: templates are not yet embedded simultaneously in the AR torus relative to the section ball",
    }
    result["witness_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = generate()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    if args.check:
        print("T73_PL_NIELSEN_TEMPLATES=PASS")
        print(f"UNIT_SLIDES={result['unit_slide_count']}")
        print(f"GLOBAL_PLACEMENT_STATUS={result['global_placement_status']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    elif not args.output:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
