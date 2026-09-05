#!/usr/bin/env python3
"""Assemble the six t-cancellation bands into a replayable candidate movie."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECTANGLES = ROOT / "geometry/t73_candidate_band_rectangles.json"
SPLICES = ROOT / "geometry/t73_candidate_band_splice_descriptors.json"
SOURCE = ROOT / "geometry/t73_cancel_t_hcs.json"
OUTPUT = ROOT / "geometry/t73_candidate_t_band_movie.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def build() -> dict[str, Any]:
    rectangles = json.loads(RECTANGLES.read_text(encoding="utf-8"))
    splices = json.loads(SPLICES.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    by_band: dict[int, list[dict[str, Any]]] = {}
    for segment in rectangles["bands"]:
        if segment["kind"] == "t":
            by_band.setdefault(segment["index"], []).append(segment)
    splice = {(item["kind"], item["index"]): item for item in splices["bands"]}
    movie = []
    for band in source["slide_bands"]:
        index = band["index"]
        segments = sorted(by_band[index], key=lambda item: item["segment_index"])
        descriptor = splice[("t", index)]
        if len(segments) != descriptor["segment_count"]:
            raise AssertionError("t-band rectangle/splice segment count disagrees")
        movie.append({
            "index": index,
            "component": band["component"],
            "movie_time_order": band["movie_time_order"],
            "current_link_before": f"candidate_t_state_{index}",
            "source_attachment": descriptor["source_attachment"],
            "target_attachment": descriptor["target_attachment"],
            "rectangle_segments": segments,
            "splice": descriptor,
            "updated_link_after": f"candidate_t_state_{index + 1}",
            "status": "CANDIDATE_UNVERIFIED",
        })
    if len(movie) != 6 or [item["movie_time_order"] for item in movie] != list(range(6)):
        raise AssertionError("t-band order is not the six-step cancellation order")
    result = {
        "schema": "t73_candidate_t_band_movie/v1",
        "t_cancellation_sha256": source["sha256"],
        "rectangles_sha256": rectangles["sha256"],
        "splices_sha256": splices["sha256"],
        "bands": movie,
        "completion_status": "CANDIDATE_UNVERIFIED",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("candidate t-band movie is stale")
    print("T73_CANDIDATE_T_BAND_MOVIE=CANDIDATE_UNVERIFIED")


if __name__ == "__main__":
    main()
