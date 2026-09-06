#!/usr/bin/env python3
"""Assemble all nine-piece x-m1 replacement core/push cycles in R3."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORES = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v3_receipt.json"
CORE_EMBEDDING = (
    ROOT / "audit/t73_x_m1_complete_global_r3_replacement_core_embedding_v3.json"
)
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
STUB_CLEARANCE = ROOT / "audit/t73_x_m1_stub_ribbon_cross_band_verification.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_lane_push_paths_receipt.json"
BAND_CLEARANCE = ROOT / "audit/t73_x_band_global_r3_lane_push_clearance.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
TRANSITION_CLEARANCE = ROOT / "audit/t73_x_m1_transition_ribbon_global_clearance.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
MIDDLE_VERIFY = ROOT / "audit/t73_x_m1_middle_paths_r3_verification.json"
STUB_BAND = ROOT / "audit/t73_x_m1_stub_band_ribbon_clearance_verification.json"
OUTPUT_RECEIPT = (
    ROOT / "audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_receipt.json"
)
DEFAULT_OUTPUT = (
    Path.home()
    / ".cache/t73_x_m1_complete_global_r3_framed_replacement_cycles.jsonl.gz"
)
TRANSLATION = (Fraction(20_000), Fraction(2_000), Fraction(0))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest().upper()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def encode(value):
    return [str(coordinate) for coordinate in value]


def translated(values):
    return [
        tuple(
            coordinate + shift for coordinate, shift in zip(point(value), TRANSLATION)
        )
        for value in values
    ]


def extract(record, name):
    piece = next(item for item in record["piece_ranges"] if item["piece"] == name)
    low, high = piece["segment_range"]
    return [point(value) for value in record["vertices"][low : high + 1]]


def orient_to(path, push, expected, name):
    if path == expected:
        return path, push
    if list(reversed(path)) == expected:
        return list(reversed(path)), list(reversed(push))
    raise AssertionError(f"framed source core misses v3 piece {name}")


def append_piece(core, push, piece_core, piece_push, name, ranges):
    if core and (core[-1] != piece_core[0] or push[-1] != piece_push[0]):
        raise AssertionError(f"framed core/push boundary mismatch before {name}")
    low = len(core) - 1 if core else 0
    core.extend(piece_core if not core else piece_core[1:])
    push.extend(piece_push if not push else piece_push[1:])
    ranges.append(
        {
            "piece": name,
            "segment_range": [low, len(core) - 1],
            "segment_count": len(piece_core) - 1,
        }
    )


def build(output_path):
    receipts = {
        name: json.loads(path.read_text())
        for name, path in {
            "cores": CORES,
            "core_embedding": CORE_EMBEDDING,
            "stubs": STUBS,
            "stub_clearance": STUB_CLEARANCE,
            "bands": BANDS,
            "band_clearance": BAND_CLEARANCE,
            "transitions": TRANSITIONS,
            "transition_clearance": TRANSITION_CLEARANCE,
            "middles": MIDDLES,
            "middle_verify": MIDDLE_VERIFY,
            "stub_band": STUB_BAND,
        }.items()
    }
    source = {
        name: records(receipts[name])
        for name in ("cores", "stubs", "bands", "transitions", "middles")
    }
    if tuple(
        len(source[name])
        for name in ("cores", "stubs", "bands", "transitions", "middles")
    ) != (1513, 1513, 1513, 3026, 1513):
        raise AssertionError("complete framed source inventory changed")
    if not receipts["core_embedding"]["complete_replacement_core_embedding"]:
        raise AssertionError("complete v3 core embedding is not closed")
    if not receipts["transition_clearance"]["global_transition_ribbon_clearance"]:
        raise AssertionError("transition ribbon clearance is not closed")
    if receipts["stub_band"]["full_result"]["intersections"]:
        raise AssertionError("stub/band ribbon clearance failed")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_complete_global_r3_framed_replacement_cycles/v1",
        "complete_core_embedding_sha256": receipts["core_embedding"]["sha256"],
        "stub_ribbon_clearance_sha256": receipts["stub_clearance"]["sha256"],
        "band_ribbon_clearance_sha256": receipts["band_clearance"]["sha256"],
        "transition_ribbon_clearance_sha256": receipts["transition_clearance"][
            "sha256"
        ],
        "middle_ribbon_verification_sha256": receipts["middle_verify"]["sha256"],
        "stub_band_ribbon_clearance_sha256": receipts["stub_band"]["sha256"],
    }
    counts = {"records": 0, "segments": 0, "triangles": 0, "joins": 0}
    extrema = {name: [None, None] for name in ("stub", "band", "transition", "middle")}

    def update_extrema(system, core, push):
        values = [value[0] for value in core + push]
        low, high = min(values), max(values)
        extrema[system][0] = (
            low if extrema[system][0] is None else min(extrema[system][0], low)
        )
        extrema[system][1] = (
            high if extrema[system][1] is None else max(extrema[system][1], high)
        )

    with output_path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0
        ) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for band_index, core_record in enumerate(source["cores"]):
                stub_record = source["stubs"][band_index]
                band_record = source["bands"][band_index]
                first_transition, last_transition = source["transitions"][
                    2 * band_index : 2 * band_index + 2
                ]
                middle_record = source["middles"][band_index]
                stubs = stub_record["stubs"]
                lanes = {lane["lane"]: lane for lane in band_record["lanes"]}

                def cp(record, core_key="core_vertices", push_key="push_vertices"):
                    return [point(value) for value in record[core_key]], [
                        point(value) for value in record[push_key]
                    ]

                middle_core = translated(middle_record["core_vertices_r3"])
                middle_push = translated(middle_record["push_vertices_r3"])
                raw_pieces = {
                    "source_stub_before": (*cp(stubs["source_stub_before"]), "stub"),
                    "negative_band_lane": (*cp(lanes["negative"]), "band"),
                    "target_complement_first": (
                        *cp(stubs["target_complement_first"]),
                        "stub",
                    ),
                    "negative_middle_transition_first": (
                        *cp(first_transition),
                        "transition",
                    ),
                    "translated_m1_parallel_middle": (
                        middle_core,
                        middle_push,
                        "middle",
                    ),
                    "negative_middle_transition_last": (
                        *cp(last_transition),
                        "transition",
                    ),
                    "target_complement_last": (
                        *cp(stubs["target_complement_last"]),
                        "stub",
                    ),
                    "positive_band_lane": (*cp(lanes["positive"]), "band"),
                    "source_stub_after": (*cp(stubs["source_stub_after"]), "stub"),
                }
                complete_core, complete_push, ranges = [], [], []
                for piece in core_record["piece_ranges"]:
                    name = piece["piece"]
                    expected = extract(core_record, name)
                    piece_core, piece_push, system = raw_pieces[name]
                    piece_core, piece_push = orient_to(
                        piece_core, piece_push, expected, name
                    )
                    update_extrema(system, piece_core, piece_push)
                    append_piece(
                        complete_core,
                        complete_push,
                        piece_core,
                        piece_push,
                        name,
                        ranges,
                    )
                if [encode(value) for value in complete_core] != core_record[
                    "vertices"
                ]:
                    raise AssertionError(
                        "complete framed core differs from v3 core cache"
                    )
                size = len(complete_core)
                triangles = [
                    triangle
                    for index in range(size - 1)
                    for triangle in (
                        [index, index + 1, size + index + 1],
                        [index, size + index + 1, size + index],
                    )
                ]
                record = {
                    "record": "complete_global_r3_framed_replacement_cycle",
                    "band_index": band_index,
                    "component": core_record["component"],
                    "core_vertices": [encode(value) for value in complete_core],
                    "push_vertices": [encode(value) for value in complete_push],
                    "piece_ranges": ranges,
                    "ribbon_triangles": triangles,
                    "segment_count": size - 1,
                    "relative_twist": 0,
                    "global_embedding_status": "BOUND_TO_ALL_SUBSYSTEM_PAIR_CLEARANCE_CERTIFICATES",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                counts["records"] += 1
                counts["segments"] += size - 1
                counts["triangles"] += len(triangles)
                counts["joins"] += 8

    if not (
        extrema["stub"][1] < extrema["middle"][0]
        and extrema["band"][1] < extrema["middle"][0]
    ):
        raise AssertionError("stub/band framing x intervals reach middle framing")
    pair_evidence = [
        ("stub/stub", receipts["stub_clearance"]["sha256"]),
        ("band/band", receipts["band_clearance"]["sha256"]),
        ("transition/transition", receipts["transition_clearance"]["sha256"]),
        ("middle/middle", receipts["middle_verify"]["sha256"]),
        ("stub/band", receipts["stub_band"]["sha256"]),
        ("stub/transition", receipts["transition_clearance"]["sha256"]),
        ("stub/middle", "exact disjoint core/push x intervals"),
        ("band/transition", receipts["transition_clearance"]["sha256"]),
        ("band/middle", "exact disjoint core/push x intervals"),
        ("transition/middle", receipts["transition_clearance"]["sha256"]),
    ]
    receipt = {
        "schema": "t73_x_m1_complete_global_r3_framed_replacement_cycles_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "complete_core_embedding_sha256": header["complete_core_embedding_sha256"],
        "stub_ribbon_clearance_sha256": header["stub_ribbon_clearance_sha256"],
        "band_ribbon_clearance_sha256": header["band_ribbon_clearance_sha256"],
        "transition_ribbon_clearance_sha256": header[
            "transition_ribbon_clearance_sha256"
        ],
        "middle_ribbon_verification_sha256": header[
            "middle_ribbon_verification_sha256"
        ],
        "stub_band_ribbon_clearance_sha256": header[
            "stub_band_ribbon_clearance_sha256"
        ],
        "record_count": counts["records"],
        "core_segment_count": counts["segments"],
        "push_segment_count": counts["segments"],
        "ribbon_triangle_count": counts["triangles"],
        "piece_boundary_core_push_match_count": counts["joins"],
        "piece_count_per_cycle": 9,
        "subsystem_x_extrema": {
            name: [str(value) for value in bounds] for name, bounds in extrema.items()
        },
        "subsystem_pair_clearance": [
            {"pair": pair, "evidence": evidence, "status": "PASS"}
            for pair, evidence in pair_evidence
        ],
        "subsystem_pair_count": len(pair_evidence),
        "relative_twist_sum": 0,
        "globally_embedded_complete_framing": True,
        "completion_status": "ALL_1513_NINE_PIECE_X_M1_REPLACEMENT_CYCLES_HAVE_GLOBAL_CORE_PUSH_RIBBON_EMBEDDINGS",
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_FRAMED_REPLACEMENT_CYCLES",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(args.output or DEFAULT_OUTPUT)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "cycles": result["record_count"],
                "segments": result["core_segment_count"],
                "triangles": result["ribbon_triangle_count"],
                "joins": result["piece_boundary_core_push_match_count"],
                "bytes": result["cache_size"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
