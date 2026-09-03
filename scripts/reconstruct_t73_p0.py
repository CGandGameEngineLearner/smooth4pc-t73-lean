#!/usr/bin/env python3
"""Strict, reproducible gate for the geometric P0 reconstruction.

This program deliberately does not turn a word ledger into geometry.  A
passing input must contain actual rational PL data for a 3-ball, 44 braid
strands, normal fields, the two cancellation movies, and an AR provenance
map.  The public six-sweep word is an output to be compared, never an input
from which the AR collar is inferred.

The verifier checks the finite combinatorial conditions that can be checked
without a computer-assisted 3-manifold theorem.  The input format leaves
room for independent certificates for PL embeddedness and local Kirby moves;
their receipts are mandatory.  In particular, a symbolic/string-only input
is rejected before any braid comparison.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "audit" / "t73_p0_reconstruction_schema.json"
PUBLIC_INPUT = ROOT / "data" / "T73_DELTA3_PUBLIC_INPUT.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def fail(message: str) -> None:
    raise AssertionError(message)


def rational(value: Any, where: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        fail(f"{where} is not an exact rational")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        fail(f"{where} is not an exact rational: {exc}")
    raise AssertionError("unreachable")


def point(value: Any, where: str) -> tuple[Fraction, Fraction, Fraction]:
    if not isinstance(value, list) or len(value) != 3:
        fail(f"{where} must be a 3-vector")
    return tuple(rational(x, f"{where}[{i}]") for i, x in enumerate(value))  # type: ignore[return-value]


def require_object(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{where} must be an object")
    return value


def verify_source(source: dict[str, Any]) -> None:
    path_text = source.get("local_path")
    if not isinstance(path_text, str):
        fail("source.local_path must identify available source bytes")
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        fail("source.local_path escapes the repository")
    if not path.is_file():
        fail(f"source bytes are unavailable: {path_text}")
    expected = source.get("sha256")
    if not isinstance(expected, str) or file_sha(path) != expected.upper():
        fail("source SHA-256 does not match the supplied bytes")


def verify_ball(ball: dict[str, Any]) -> None:
    vertices = ball.get("vertices")
    if not isinstance(vertices, list) or not vertices:
        fail("ambient_ball.vertices must contain explicit PL vertices")
    for i, value in enumerate(vertices):
        point(value, f"ambient_ball.vertices[{i}]")
    triangles = ball.get("boundary_triangles")
    if not isinstance(triangles, list) or not triangles:
        fail("ambient_ball.boundary_triangles must be explicit")
    for i, tri in enumerate(triangles):
        if not isinstance(tri, list) or len(tri) != 3 or not all(isinstance(x, int) for x in tri):
            fail(f"ambient_ball.boundary_triangles[{i}] is not an index triple")
        if any(x < 0 or x >= len(vertices) for x in tri):
            fail(f"ambient_ball.boundary_triangles[{i}] has an out-of-range vertex")
    if ball.get("certified_topological_type") != "3-ball":
        fail("ambient_ball.certified_topological_type must be 3-ball")


def verify_strands(collar: dict[str, Any]) -> dict[int, dict[str, Any]]:
    strands = collar.get("strands")
    if not isinstance(strands, list) or len(strands) != 44:
        fail("detector_collar.strands must contain exactly 44 explicit strands")
    by_id: dict[int, dict[str, Any]] = {}
    for index, raw in enumerate(strands):
        strand = require_object(raw, f"detector_collar.strands[{index}]")
        strand_id = strand.get("id")
        if not isinstance(strand_id, int) or not 1 <= strand_id <= 44 or strand_id in by_id:
            fail("strand ids must be a permutation of 1,...,44")
        vertices = strand.get("vertices")
        normals = strand.get("normal_vectors")
        if not isinstance(vertices, list) or len(vertices) < 2:
            fail(f"strand {strand_id} has no explicit polyline")
        if not isinstance(normals, list) or len(normals) != len(vertices):
            fail(f"strand {strand_id} needs one normal vector at every vertex")
        points = [point(v, f"strand {strand_id}.vertices[{i}]") for i, v in enumerate(vertices)]
        zs = [v[2] for v in points]
        if any(a >= b for a, b in zip(zs, zs[1:])):
            fail(f"strand {strand_id} is not monotone in collar height")
        for i, normal in enumerate(normals):
            n = point(normal, f"strand {strand_id}.normal_vectors[{i}]")
            if n == (0, 0, 0):
                fail(f"strand {strand_id} has a zero normal vector")
        by_id[strand_id] = strand
    if sorted(by_id) != list(range(1, 45)):
        fail("strand ids are not exactly 1,...,44")
    if collar.get("pairwise_disjointness_certificate", {}).get("status") != "PASS":
        fail("pairwise disjointness certificate is not PASS")
    if collar.get("normal_field_certificate", {}).get("status") != "PASS":
        fail("normal_field_certificate is not PASS")
    return by_id


def verify_ar_binding(collar: dict[str, Any]) -> None:
    binding = require_object(collar.get("ar_passage_binding"), "detector_collar.ar_passage_binding")
    if binding.get("status") != "PASS":
        fail("AR passage binding is not PASS")
    for key in ("component_parametrization_sha256", "segment_map", "endpoint_map", "normal_transport_map"):
        if key not in binding:
            fail(f"AR passage binding missing {key}")
    if binding.get("derived_from") in {"T73_DELTA3_PUBLIC_INPUT.json", "public crossing rows", "abstract braid"}:
        fail("AR passage binding is circularly derived from the public braid")
    if not isinstance(binding["segment_map"], list) or len(binding["segment_map"]) != 44:
        fail("AR segment_map must bind every one of the 44 strands")


def verify_cancellation(movie: dict[str, Any]) -> None:
    moves = movie.get("moves")
    if not isinstance(moves, list) or len(moves) != 2:
        fail("cancellation_movie.moves must contain the two registered cancellations")
    pairs = []
    for i, raw in enumerate(moves):
        move = require_object(raw, f"cancellation_movie.moves[{i}]")
        pair = move.get("cancelled_pair")
        if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, str) for x in pair):
            fail(f"cancellation move {i} has no cancelled pair")
        pairs.append(tuple(pair))
        for key in ("local_movie", "owner_transport", "normal_field_transport"):
            if move.get(key, {}).get("status") != "PASS":
                fail(f"cancellation move {i} missing PASS {key}")
    if pairs != [("t", "h_CS"), ("x", "m_1")]:
        fail(f"unexpected cancellation order/pairs: {pairs}")


def expected_public_word() -> list[int]:
    data = json.loads(PUBLIC_INPUT.read_text(encoding="utf-8"))
    chronology = data["point_push"]["oriented_source_indices"]
    rows = {row[0]: row for row in data["point_push"]["crossing_rows"]}
    # Importing the checked public conversion is intentional only here: it is
    # the target word, never the source of AR geometry.
    import importlib.util

    path = ROOT / "scripts" / "verify_t73_compact_point_push.py"
    spec = importlib.util.spec_from_file_location("t73_public_target", path)
    if spec is None or spec.loader is None:
        fail("cannot load public target braid converter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [letter for index in chronology for letter in module.row_word(rows[index])]


def pure_factor(moving: int, other: int, sign: int, geometry: str) -> list[int]:
    """Expand one physical point-push crossing into its pure Artin factor."""
    i, j = sorted((moving, other))
    if geometry == "L":
        return list(range(j - 1, i, -1)) + [sign * i, sign * i] + [
            -k for k in range(i + 1, j)
        ]
    if geometry == "R":
        return list(range(i, j - 1)) + [sign * (j - 1), sign * (j - 1)] + [
            -k for k in range(j - 2, i - 1, -1)
        ]
    fail(f"unknown point-push geometry {geometry!r}")
    raise AssertionError("unreachable")


def point_on_segment(
    points: list[tuple[Fraction, Fraction, Fraction]],
    segment: int,
    height: Fraction,
    where: str,
) -> tuple[Fraction, Fraction, Fraction]:
    if not isinstance(segment, int) or not 0 <= segment < len(points) - 1:
        fail(f"{where} is not a valid strand segment")
    a, b = points[segment], points[segment + 1]
    if not a[2] <= height <= b[2] or a[2] == b[2]:
        fail(f"{where} does not contain the event height")
    t = (height - a[2]) / (b[2] - a[2])
    return tuple(a[k] + t * (b[k] - a[k]) for k in range(3))  # type: ignore[return-value]


def segment_at_height(
    points: list[tuple[Fraction, Fraction, Fraction]],
    height: Fraction,
    where: str,
    heights: list[Fraction] | None = None,
) -> tuple[int, tuple[Fraction, Fraction, Fraction]]:
    if heights is None:
        heights = [p[2] for p in points]
    segment = bisect.bisect_right(heights, height) - 1
    if segment < 0:
        fail(f"{where} is below the strand")
    if segment >= len(points) - 1:
        segment = len(points) - 2
    return segment, point_on_segment(points, segment, height, where)


def verify_event_geometry(
    event: dict[str, Any],
    index: int,
    parsed: dict[int, list[tuple[Fraction, Fraction, Fraction]]],
    heights: dict[int, list[Fraction]] | None = None,
) -> None:
    height = rational(event["z_time"], f"crossing event {index}.z_time")
    moving = event["moving_strand"]
    other = event["other_strand"]
    moving_points = parsed[moving]
    other_points = parsed[other]
    pm = point_on_segment(
        moving_points, event["moving_segment"], height, f"event {index}.moving_segment"
    )
    po = point_on_segment(
        other_points, event["other_segment"], height, f"event {index}.other_segment"
    )
    if pm[0] != po[0]:
        fail(f"event {index} is not an x-projection crossing")
    if pm[1] == po[1]:
        fail(f"event {index} is a non-transverse projected crossing")
    expected_over = moving if pm[1] > po[1] else other
    if event["over_strand"] != expected_over:
        fail(f"event {index} over_strand disagrees with the y-over convention")

    x_values: list[tuple[Fraction, int]] = []
    for strand_id, vertices in parsed.items():
        _, at_height = segment_at_height(
            vertices, height, f"strand {strand_id}", None if heights is None else heights[strand_id]
        )
        x_values.append((at_height[0], strand_id))
    if len(x_values) != 44:
        fail(f"event {index} does not meet all 44 strands at its height")
    x_values.sort()
    equal = [strand_id for x, strand_id in x_values if x == pm[0]]
    if set(equal) != {moving, other}:
        fail(f"event {index} has an unrecorded simultaneous x-crossing")
    positions = [strand_id for _, strand_id in x_values]
    if abs(positions.index(moving) - positions.index(other)) != 1:
        fail(f"event {index} is not an adjacent braid crossing")

    if event["sign"] not in (-1, 1):
        fail(f"event {index} has an invalid braid sign")


def derive_elementary_events(collar: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive projected crossings from explicit rational strand polylines."""
    strand_records = verify_strands(collar)
    parsed = {
        strand_id: [
            point(v, f"strand {strand_id}.vertices[{j}]")
            for j, v in enumerate(raw["vertices"])
        ]
        for strand_id, raw in strand_records.items()
    }
    heights = {strand_id: [p[2] for p in vertices] for strand_id, vertices in parsed.items()}
    candidates: list[tuple[Fraction, int, int, int, int]] = []
    grids = [[p[2] for p in parsed[strand_id]] for strand_id in range(1, 45)]
    common_grid = all(grid == grids[0] for grid in grids[1:])
    if common_grid:
        # In a layered movie, only adjacent strands can cross without a third
        # strand at the same projection point.  This is O(43 * events).
        grid = grids[0]
        for step in range(len(grid) - 1):
            lo, hi = grid[step], grid[step + 1]
            mid = (lo + hi) / 2
            order = sorted(
                range(1, 45),
                key=lambda strand_id: point_on_segment(parsed[strand_id], step, mid, f"strand {strand_id}")[0],
            )
            for position in range(43):
                left, right = order[position], order[position + 1]
                a0, a1 = parsed[left][step], parsed[left][step + 1]
                b0, b1 = parsed[right][step], parsed[right][step + 1]
                av = (a1[0] - a0[0]) / (a1[2] - a0[2])
                bv = (b1[0] - b0[0]) / (b1[2] - b0[2])
                velocity = av - bv
                if velocity == 0:
                    continue
                z = (b0[0] - a0[0] + av * a0[2] - bv * b0[2]) / velocity
                if lo < z < hi:
                    candidates.append((z, left, right, step, step))
    else:
        for left in range(1, 45):
            for right in range(left + 1, 45):
                a_points, b_points = parsed[left], parsed[right]
                a_seg = b_seg = 0
                while a_seg < len(a_points) - 1 and b_seg < len(b_points) - 1:
                    a0, a1 = a_points[a_seg], a_points[a_seg + 1]
                    b0, b1 = b_points[b_seg], b_points[b_seg + 1]
                    av = (a1[0] - a0[0]) / (a1[2] - a0[2])
                    bv = (b1[0] - b0[0]) / (b1[2] - b0[2])
                    lo, hi = max(a0[2], b0[2]), min(a1[2], b1[2])
                    velocity = av - bv
                    if lo < hi and velocity != 0:
                        z = (b0[0] - a0[0] + av * a0[2] - bv * b0[2]) / velocity
                        if lo < z < hi:
                            candidates.append((z, left, right, a_seg, b_seg))
                    if a1[2] < b1[2]:
                        a_seg += 1
                    else:
                        b_seg += 1
    candidates.sort()
    if any(a[0] == b[0] for a, b in zip(candidates, candidates[1:])):
        fail("derived crossing movie has simultaneous projected events")

    events: list[dict[str, Any]] = []
    previous_height = Fraction(0)
    for index, (height, left, right, left_seg, right_seg) in enumerate(candidates):
        # At the crossing height the two x-coordinates are equal.  Recover
        # the braid order from a rational sample immediately before it.
        sample_height = (previous_height + height) / 2
        x_values: list[tuple[Fraction, int]] = []
        for strand_id, vertices in parsed.items():
            _, at_height = segment_at_height(vertices, sample_height, f"strand {strand_id}", heights[strand_id])
            x_values.append((at_height[0], strand_id))
        x_values.sort()
        # Use the exact pair's x-coordinate, avoiding any floating comparison.
        pair_x = point_on_segment(parsed[left], left_seg, height, f"derived {index}")[0]
        exact_x_values: list[tuple[Fraction, int]] = []
        for strand_id, vertices in parsed.items():
            _, at_height = segment_at_height(vertices, height, f"strand {strand_id}", heights[strand_id])
            exact_x_values.append((at_height[0], strand_id))
        equal = [strand_id for x, strand_id in exact_x_values if x == pair_x]
        if set(equal) != {left, right}:
            fail(f"derived event {index} has a third simultaneous projected crossing")
        positions = [strand_id for _, strand_id in x_values]
        if abs(positions.index(left) - positions.index(right)) != 1:
            fail(f"derived event {index} is not an adjacent braid crossing")
        lp = point_on_segment(parsed[left], left_seg, height, f"derived {index}.left")
        rp = point_on_segment(parsed[right], right_seg, height, f"derived {index}.right")
        over = left if lp[1] > rp[1] else right
        left_pos, right_pos = positions.index(left), positions.index(right)
        current_left, current_right = (
            (left, right) if left_pos < right_pos else (right, left)
        )
        left_seg_for_sign = left_seg if current_left == left else right_seg
        right_seg_for_sign = right_seg if current_right == right else left_seg
        left_points = parsed[current_left]
        right_points = parsed[current_right]
        sign = 1 if over == current_right else -1
        moving, other = current_left, current_right
        letter = sign * (min(left_pos, right_pos) + 1)
        events.append({
            "z_time": str(height),
            "moving_strand": moving,
            "other_strand": other,
            "sign": sign,
            "artin_letter": letter,
            "over_strand": over,
            "source_segment": [left_seg, right_seg],
            "moving_segment": left_seg,
            "other_segment": right_seg,
        })
        previous_height = height
    return events


def verify_movie(candidate: dict[str, Any], expected: list[int]) -> dict[str, Any]:
    collar = require_object(candidate.get("detector_collar"), "detector_collar")
    movie = require_object(collar.get("crossing_movie"), "detector_collar.crossing_movie")
    derivation = require_object(movie.get("derivation"), "crossing_movie.derivation")
    if derivation.get("status") != "PASS":
        fail("crossing_movie.derivation is not PASS")
    geometry_digest = canonical_sha(
        {
            "ambient_ball": candidate.get("ambient_ball"),
            "strands": collar.get("strands"),
            "ar_passage_binding": collar.get("ar_passage_binding"),
        }
    )
    if derivation.get("geometry_sha256") != geometry_digest:
        fail("crossing movie is not bound to the supplied AR geometry")
    strand_records = verify_strands(collar)
    parsed = {
        strand_id: [
            point(v, f"strand {strand_id}.vertices[{j}]")
            for j, v in enumerate(raw["vertices"])
        ]
        for strand_id, raw in strand_records.items()
    }
    heights = {strand_id: [p[2] for p in vertices] for strand_id, vertices in parsed.items()}
    events = movie.get("events")
    if not isinstance(events, list) or len(events) != len(expected):
        fail(f"crossing_movie.events must contain exactly {len(expected)} elementary crossings")
    if not isinstance(events, list):
        fail("crossing_movie.events must be an explicit ordered list")
    letters: list[int] = []
    previous_height: Fraction | None = None
    order = list(range(1, 45))
    for i, raw in enumerate(events):
        event = require_object(raw, f"crossing_movie.events[{i}]")
        moving = event.get("moving_strand")
        other = event.get("other_strand")
        sign = event.get("sign")
        if (
            not isinstance(moving, int)
            or not isinstance(other, int)
            or moving == other
            or not 1 <= moving <= 44
            or not 1 <= other <= 44
        ):
            fail(f"crossing event {i} has invalid strand labels")
        if sign not in (-1, 1):
            fail(f"crossing event {i} has invalid sign")
        letter = event.get("artin_letter")
        if not isinstance(letter, int) or letter == 0 or abs(letter) >= 44:
            fail(f"crossing event {i} has an invalid Artin letter")
        for key in ("z_time", "over_strand", "source_segment", "moving_segment", "other_segment"):
            if key not in event:
                fail(f"crossing event {i} missing {key}")
        height = rational(event["z_time"], f"crossing event {i}.z_time")
        if previous_height is not None and height <= previous_height:
            fail("crossing event heights must be strictly increasing")
        previous_height = height
        if event["over_strand"] not in (moving, other):
            fail(f"crossing event {i}.over_strand is not a participating strand")
        verify_event_geometry(event, i, parsed, heights)
        positions = []
        order_sample = (Fraction(0) if previous_height is None else previous_height + height) / 2
        for strand_id, raw_points in parsed.items():
            _, at_height = segment_at_height(raw_points, order_sample, f"strand {strand_id}", heights[strand_id])
            positions.append((at_height[0], strand_id))
        positions.sort()
        left_position, right_position = positions.index(moving), positions.index(other)
        if right_position != left_position + 1:
            fail(f"crossing event {i} is not in the declared left/right order")
        if order[left_position] != moving or order[right_position] != other:
            fail(f"crossing event {i} strand labels disagree with prior braid events")
        derived_sign = 1 if event["over_strand"] == other else -1
        if sign != derived_sign:
            fail(f"crossing event {i} sign disagrees with the over-strand convention")
        derived_letter = derived_sign * (left_position + 1)
        if letter != derived_letter:
            fail(f"crossing event {i} has an inconsistent derived Artin letter")
        letters.append(letter)
        order[left_position], order[right_position] = order[right_position], order[left_position]
    if letters != expected:
        fail("AR-derived elementary crossing movie does not equal the public 11340-letter word")
    return {
        "elementary_crossing_count": len(events),
        "length": len(letters),
        "sha256": canonical_sha(letters),
        "letters": letters,
    }


def verify(candidate: dict[str, Any]) -> dict[str, Any]:
    if candidate.get("schema") != "t73_p0_reconstruction_input/v1":
        fail("wrong P0 reconstruction schema")
    verify_source(require_object(candidate.get("source"), "source"))
    verify_ball(require_object(candidate.get("ambient_ball"), "ambient_ball"))
    collar = require_object(candidate.get("detector_collar"), "detector_collar")
    verify_strands(collar)
    verify_ar_binding(collar)
    verify_cancellation(require_object(candidate.get("cancellation_movie"), "cancellation_movie"))
    result = verify_movie(candidate, expected_public_word())
    checks = candidate.get("independent_checks")
    if (
        not isinstance(checks, list)
        or not checks
        or any(not isinstance(c, dict) or c.get("status") != "PASS" for c in checks)
    ):
        fail("independent_checks must contain only structured PASS receipts")
    return {
        "schema": "t73_p0_reconstruction_result/v1",
        "verdict": "PASS",
        "B44_length": result["length"],
        "B44_sha256": result["sha256"],
        "public_target_source": str(PUBLIC_INPUT.relative_to(ROOT)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--derive-events", action="store_true")
    args = parser.parse_args()
    try:
        candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
        if args.derive_events:
            collar = require_object(candidate.get("detector_collar"), "detector_collar")
            print(json.dumps(derive_elementary_events(collar), indent=2))
            return
        result = verify(candidate)
    except (OSError, json.JSONDecodeError, AssertionError) as exc:
        print("P0_RECONSTRUCTION=OPEN")
        print(f"REASON={exc}")
        raise SystemExit(2)
    print("P0_RECONSTRUCTION=PASS")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
