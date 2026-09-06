#!/usr/bin/env python3
"""Build complete nonincident stub/band common-displacement candidates."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
from probe_t73_x_m1_transition_ribbon_global_clearance import (
    BANDS,
    STUBS,
    band_triangles,
    exact_bounds,
    float_bounds,
    overlap,
    screen_bounds,
    stub_triangles,
)
from rtree import index as rtree_index

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit/t73_x_m1_stub_band_ribbon_exact_candidates.json"
DEFAULT_CACHE = Path.home() / ".cache/t73_x_m1_stub_band_rectangle_candidates.csv.gz"


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def owner_pair_allowed(stub_owner, band_owner):
    if stub_owner[0] != band_owner[0]:
        return False
    return (stub_owner[1], band_owner[1]) in {
        ("source_stub_before", "negative"),
        ("target_complement_first", "negative"),
        ("target_complement_last", "positive"),
        ("source_stub_after", "positive"),
    }


def rectangle_metadata(triangles):
    answer = []
    for index in range(0, len(triangles), 2):
        first, second = triangles[index], triangles[index + 1]
        if first[:2] != second[:2]:
            raise AssertionError("two-triangle ribbon rectangle ownership changed")
        answer.append((first[1], first[2] // 2))
    return answer


def permitted_rectangle(stub_meta, band_meta, stub_counts, band_counts):
    stub_owner, stub_segment = stub_meta
    band_owner, band_segment = band_meta
    if not owner_pair_allowed(stub_owner, band_owner):
        return False
    stub_name, lane = stub_owner[1], band_owner[1]
    expected = {
        ("source_stub_before", "negative"): (stub_counts[stub_owner] - 1, 0),
        ("target_complement_first", "negative"): (0, band_counts[band_owner] - 1),
        ("target_complement_last", "positive"): (stub_counts[stub_owner] - 1, 0),
        ("source_stub_after", "positive"): (0, band_counts[band_owner] - 1),
    }[(stub_name, lane)]
    return (stub_segment, band_segment) == expected


def build(cache_path=DEFAULT_CACHE):
    stub_receipt = json.loads(STUBS.read_text())
    band_receipt = json.loads(BANDS.read_text())
    stubs = stub_triangles(stub_receipt)
    bands = band_triangles(band_receipt)
    stub_meta, band_meta = rectangle_metadata(stubs), rectangle_metadata(bands)
    stub_counts = {owner: max(segment + 1, 0) for owner, segment in stub_meta}
    band_counts = {owner: max(segment + 1, 0) for owner, segment in band_meta}
    band_bounds = [exact_bounds(item[3]) for item in bands]
    band_screens = [screen_bounds(item[3]) for item in bands]
    band_low = np.asarray([value[0] for value in band_screens])
    band_high = np.asarray([value[1] for value in band_screens])
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(bounds), None)
            for index, bounds in enumerate(band_bounds)
        ),
        properties=properties,
    )
    broad = screen_rejects = exact_bounds_rejects = shared_incidences = (
        rectangle_incidences
    ) = 0
    pairs = set()
    for stub_index, stub in enumerate(stubs):
        stub_bound = exact_bounds(stub[3])
        candidates = np.fromiter(
            tree.intersection(float_bounds(stub_bound)), dtype=np.int64
        )
        broad += len(candidates)
        low, high = screen_bounds(stub[3])
        mask = np.all(band_high[candidates] >= low, axis=1) & np.all(
            band_low[candidates] <= high, axis=1
        )
        screen_rejects += int(np.count_nonzero(~mask))
        for raw_band_index in candidates[mask]:
            band_index = int(raw_band_index)
            band = bands[band_index]
            if not overlap(stub_bound, band_bounds[band_index]):
                exact_bounds_rejects += 1
                continue
            shared = set(stub[3]) & set(band[3])
            if shared:
                if not owner_pair_allowed(stub[1], band[1]):
                    raise AssertionError(
                        f"unexpected stub/band shared vertex: {stub[:3]} / {band[:3]}"
                    )
                shared_incidences += 1
                continue
            stub_rectangle, band_rectangle = stub_index // 2, band_index // 2
            if permitted_rectangle(
                stub_meta[stub_rectangle],
                band_meta[band_rectangle],
                stub_counts,
                band_counts,
            ):
                rectangle_incidences += 1
                continue
            pairs.add((stub_rectangle << 32) | band_rectangle)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with (
        cache_path.open("wb") as raw,
        gzip.GzipFile(
            filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0
        ) as output,
    ):
        output.write(b"stub_band_rectangle_pairs/v1\n")
        for packed in sorted(pairs):
            output.write(f"{packed >> 32},{packed & 0xFFFFFFFF}\n".encode())
    result = {
        "schema": "t73_x_m1_stub_band_ribbon_exact_candidates/v1",
        "stub_push_receipt_sha256": stub_receipt["sha256"],
        "band_push_receipt_sha256": band_receipt["sha256"],
        "stub_triangle_count": len(stubs),
        "band_triangle_count": len(bands),
        "expanded_3d_aabb_candidate_count": broad,
        "exact_integer_functional_interval_reject_count": screen_rejects,
        "exact_3d_bounds_reject_count": exact_bounds_rejects,
        "shared_vertex_triangle_incidence_count": shared_incidences,
        "adjacent_rectangle_triangle_incidence_count": rectangle_incidences,
        "exact_rectangle_pair_count": len(pairs),
        "candidate_path": str(cache_path),
        "candidate_size": cache_path.stat().st_size,
        "candidate_sha256": file_sha(cache_path),
        "status": "CANDIDATES_ONLY_NO_CLEARANCE_CLAIM",
    }
    result["sha256"] = canonical_sha(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_CACHE)
    args = parser.parse_args()
    result = build(args.output)
    print(
        json.dumps(
            {
                "broad": result["expanded_3d_aabb_candidate_count"],
                "rectangles": result["exact_rectangle_pair_count"],
                "incidences": result["shared_vertex_triangle_incidence_count"]
                + result["adjacent_rectangle_triangle_incidence_count"],
                "status": result["status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
