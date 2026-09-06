#!/usr/bin/env python3
"""Independent full replay of all complete nine-piece framed x-m1 cycles."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_receipt.json"
CORES = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v3_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_lane_push_paths_receipt.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
TRANSLATION = (Fraction(20_000), Fraction(2_000), Fraction(0))
PIECE_ORDER = (
    "source_stub_before",
    "negative_band_lane",
    "target_complement_first",
    "negative_middle_transition_first",
    "translated_m1_parallel_middle",
    "negative_middle_transition_last",
    "target_complement_last",
    "positive_band_lane",
    "source_stub_after",
)


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


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


def records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def translated(values):
    return [
        tuple(
            coordinate + shift for coordinate, shift in zip(point(value), TRANSLATION)
        )
        for value in values
    ]


def expected_triangles(size):
    return [
        triangle
        for index in range(size - 1)
        for triangle in (
            [index, index + 1, size + index + 1],
            [index, size + index + 1, size + index],
        )
    ]


def orient(core, push, expected):
    if core == expected:
        return core, push
    if list(reversed(core)) == expected:
        return list(reversed(core)), list(reversed(push))
    raise AssertionError("framed source piece misses complete core")


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha(payload):
        raise AssertionError("complete framed receipt payload hash changed")
    source_receipts = {
        name: json.loads(path.read_text())
        for name, path in {
            "cores": CORES,
            "stubs": STUBS,
            "bands": BANDS,
            "transitions": TRANSITIONS,
            "middles": MIDDLES,
        }.items()
    }
    source = {name: records(receipt) for name, receipt in source_receipts.items()}
    cache_path = resolve(data["cache_path"])
    if (
        cache_path.stat().st_size != data["cache_size"]
        or file_sha(cache_path) != data["cache_sha256"]
    ):
        raise AssertionError("complete framed cache bytes changed")
    digest = hashlib.sha256()
    counts = {
        "records": 0,
        "segments": 0,
        "triangles": 0,
        "joins": 0,
        "source_points": 0,
    }
    extrema = {name: [None, None] for name in ("stub", "band", "transition", "middle")}

    def update(system, core, push):
        values = [vertex[0] for vertex in core + push]
        low, high = min(values), max(values)
        extrema[system][0] = (
            low if extrema[system][0] is None else min(extrema[system][0], low)
        )
        extrema[system][1] = (
            high if extrema[system][1] is None else max(extrema[system][1], high)
        )

    with gzip.open(cache_path, "rt", encoding="utf-8") as framed:
        header_line = framed.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if (
            header["schema"]
            != "t73_x_m1_complete_global_r3_framed_replacement_cycles/v1"
        ):
            raise AssertionError("complete framed cache schema changed")
        for band_index, line in enumerate(framed):
            digest.update(line.encode())
            record = json.loads(line)
            core_record = source["cores"][band_index]
            stub_record = source["stubs"][band_index]
            band_record = source["bands"][band_index]
            first_transition, last_transition = source["transitions"][
                2 * band_index : 2 * band_index + 2
            ]
            middle = source["middles"][band_index]
            complete_core = [point(value) for value in record["core_vertices"]]
            complete_push = [point(value) for value in record["push_vertices"]]
            if (
                record["band_index"] != band_index
                or record["core_vertices"] != core_record["vertices"]
            ):
                raise AssertionError("complete framed core order/content changed")
            if tuple(piece["piece"] for piece in record["piece_ranges"]) != PIECE_ORDER:
                raise AssertionError("complete framed semantic piece order changed")
            stubs = stub_record["stubs"]
            lanes = {lane["lane"]: lane for lane in band_record["lanes"]}

            def cp(value):
                return [point(vertex) for vertex in value["core_vertices"]], [
                    point(vertex) for vertex in value["push_vertices"]
                ]

            pieces = {
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
                    translated(middle["core_vertices_r3"]),
                    translated(middle["push_vertices_r3"]),
                    "middle",
                ),
                "negative_middle_transition_last": (*cp(last_transition), "transition"),
                "target_complement_last": (
                    *cp(stubs["target_complement_last"]),
                    "stub",
                ),
                "positive_band_lane": (*cp(lanes["positive"]), "band"),
                "source_stub_after": (*cp(stubs["source_stub_after"]), "stub"),
            }
            previous_push = None
            for piece in record["piece_ranges"]:
                low, high = piece["segment_range"]
                expected_core = complete_core[low : high + 1]
                piece_core, piece_push, system = pieces[piece["piece"]]
                piece_core, piece_push = orient(piece_core, piece_push, expected_core)
                if complete_push[low : high + 1] != piece_push:
                    raise AssertionError("complete framed push piece changed")
                if previous_push is not None and previous_push != piece_push[0]:
                    raise AssertionError(
                        "complete framed push boundary is discontinuous"
                    )
                previous_push = piece_push[-1]
                update(system, piece_core, piece_push)
                counts["source_points"] += len(piece_core) + len(piece_push)
            size = len(complete_core)
            if record["ribbon_triangles"] != expected_triangles(size):
                raise AssertionError("complete framed ribbon triangulation changed")
            if record["relative_twist"] != 0:
                raise AssertionError("complete framed relative twist changed")
            counts["records"] += 1
            counts["segments"] += size - 1
            counts["triangles"] += len(record["ribbon_triangles"])
            counts["joins"] += 8
        if framed.readline():
            raise AssertionError("extra complete framed records")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("complete framed decompressed stream changed")
    expected = {"records": 1513, "segments": 92284, "triangles": 184568, "joins": 12104}
    if any(counts[key] != value for key, value in expected.items()):
        raise AssertionError(f"complete framed totals changed: {counts}")
    encoded_extrema = {
        name: [str(value) for value in bounds] for name, bounds in extrema.items()
    }
    if encoded_extrema != data["subsystem_x_extrema"]:
        raise AssertionError("complete framed subsystem x extrema changed")
    if not (
        extrema["stub"][1] < extrema["middle"][0]
        and extrema["band"][1] < extrema["middle"][0]
    ):
        raise AssertionError("middle framing x interval is not separate")
    if len(data["subsystem_pair_clearance"]) != 10 or any(
        item["status"] != "PASS" for item in data["subsystem_pair_clearance"]
    ):
        raise AssertionError("complete framed pair evidence is incomplete")
    return {
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_FRAMED_REPLACEMENT_CYCLES_FULL",
        "cache_sha_checked": True,
        "records_reconstructed": counts["records"],
        "core_push_segments_each": counts["segments"],
        "ribbon_triangles_reconstructed": counts["triangles"],
        "piece_boundary_core_push_matches": counts["joins"],
        "source_piece_point_occurrences_checked": counts["source_points"],
        "subsystem_pair_clearance_count": 10,
        "globally_embedded_complete_framing": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
