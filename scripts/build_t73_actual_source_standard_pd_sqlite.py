#!/usr/bin/env python3
"""Stream the full source-native seven-component PD into a SQLite certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from fractions import Fraction
from pathlib import Path

import ijson

from build_t73_actual_source_connector_projection_receipt import (
    check_receipt as check_projection_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
PROJECTION_RECEIPT = ROOT / "audit/t73_actual_source_connector_projection_receipt.json"
PROVENANCE = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
SLOTS = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_actual_source_standard_pd_sqlite_receipt.json"
DEFAULT_DB = Path.home() / ".cache/t73_actual_source_standard_pd.sqlite"
COMPONENT_ORDER = ["m_2", "m_3", "r_xy", "r_yz", "r_zx", "dotted_y", "dotted_z"]


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def fraction_parts(value):
    number = Fraction(value)
    return str(number.numerator), str(number.denominator)


def create_schema(connection):
    connection.executescript(
        """
        CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE crossings(
            id INTEGER PRIMARY KEY,
            kind TEXT NOT NULL,
            over_owner TEXT NOT NULL,
            under_owner TEXT NOT NULL,
            over_segment INTEGER NOT NULL,
            under_segment INTEGER NOT NULL,
            over_num TEXT NOT NULL,
            over_den TEXT NOT NULL,
            under_num TEXT NOT NULL,
            under_den TEXT NOT NULL,
            sign INTEGER NOT NULL,
            source_id TEXT
        );
        CREATE TABLE occurrences(
            crossing_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            owner TEXT NOT NULL,
            segment INTEGER NOT NULL,
            param_num TEXT NOT NULL,
            param_den TEXT NOT NULL,
            sign INTEGER NOT NULL,
            incoming_arc INTEGER,
            outgoing_arc INTEGER,
            PRIMARY KEY(crossing_id, role)
        );
        CREATE TABLE pd_rows(
            crossing_id INTEGER PRIMARY KEY,
            a INTEGER NOT NULL,
            b INTEGER NOT NULL,
            c INTEGER NOT NULL,
            d INTEGER NOT NULL
        );
        CREATE TABLE component_summary(
            component TEXT PRIMARY KEY,
            event_count INTEGER NOT NULL,
            first_arc INTEGER NOT NULL,
            last_arc INTEGER NOT NULL
        );
        """
    )


def central_segment_map(provenance):
    result = {}
    for component in provenance["components"]:
        for edge_index, edge in enumerate(component["reduced_edges"]):
            for cell in edge["raw_connector_cells"]:
                if cell["kind"] == "actual_johnson_central_connector":
                    result[cell["raw_cell_id"]] = (
                        component["component"],
                        edge_index,
                    )
    return result


def insert_crossing_batch(connection, crossings, occurrences):
    connection.executemany(
        "INSERT INTO crossings VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", crossings
    )
    connection.executemany(
        "INSERT INTO occurrences VALUES(?,?,?,?,?,?,?,NULL,NULL)", occurrences
    )


def add_source_crossings(connection, full_projection, connector_map):
    crossing_rows = []
    occurrence_rows = []
    count = 0
    with full_projection.open("rb") as source:
        for crossing in ijson.items(source, "crossings.item"):
            over_curve = crossing["over_curve_id"]
            under_curve = crossing["under_curve_id"]
            if over_curve not in connector_map or under_curve not in connector_map:
                raise AssertionError(
                    "full projection contains a dual crossing requiring an explicit dual segment map"
                )
            over_owner, over_edge = connector_map[over_curve]
            under_owner, under_edge = connector_map[under_curve]
            if over_owner != crossing["over_owner"] or under_owner != crossing[
                "under_owner"
            ]:
                raise AssertionError("source projection connector owner changed")
            over_segment = 5 * over_edge + 1 + crossing["over_segment"]
            under_segment = 5 * under_edge + 1 + crossing["under_segment"]
            over_num, over_den = fraction_parts(crossing["over_parameter"])
            under_num, under_den = fraction_parts(crossing["under_parameter"])
            crossing_rows.append((
                count,
                "actual_source_connector",
                over_owner,
                under_owner,
                over_segment,
                under_segment,
                over_num,
                over_den,
                under_num,
                under_den,
                crossing["sign"],
                crossing["id"],
            ))
            occurrence_rows.extend([
                (
                    count,
                    "over",
                    over_owner,
                    over_segment,
                    over_num,
                    over_den,
                    crossing["sign"],
                ),
                (
                    count,
                    "under",
                    under_owner,
                    under_segment,
                    under_num,
                    under_den,
                    crossing["sign"],
                ),
            ])
            count += 1
            if len(crossing_rows) >= 10000:
                insert_crossing_batch(connection, crossing_rows, occurrence_rows)
                crossing_rows.clear()
                occurrence_rows.clear()
    if crossing_rows:
        insert_crossing_batch(connection, crossing_rows, occurrence_rows)
    return count


def add_dotted_crossings(connection, start_id, cycles, slots):
    slot_by_passage = {
        entry["passage_id"]: (handle["handle"], entry["dotted_segment_pair"])
        for handle in slots["handles"]
        for entry in handle["entries"]
    }
    crossing_rows = []
    occurrence_rows = []
    current_id = start_id
    for component in cycles["components"]:
        owner = component["component"]
        for passage_index, passage in enumerate(component["passages"]):
            passage_id = passage["passage_id"]
            handle, dotted_segments = slot_by_passage[passage_id]
            dotted_owner = f"dotted_{handle}"
            sign = passage["orientation"]
            owner_segment = 5 * passage_index
            for local_index, (over_owner, under_owner, owner_parameter) in enumerate(
                (
                    (owner, dotted_owner, Fraction(1, 3)),
                    (dotted_owner, owner, Fraction(2, 3)),
                )
            ):
                dotted_segment = dotted_segments[local_index]
                if over_owner == owner:
                    over_segment, under_segment = owner_segment, dotted_segment
                    over_parameter, under_parameter = owner_parameter, Fraction(1, 2)
                else:
                    over_segment, under_segment = dotted_segment, owner_segment
                    over_parameter, under_parameter = Fraction(1, 2), owner_parameter
                over_num, over_den = fraction_parts(over_parameter)
                under_num, under_den = fraction_parts(under_parameter)
                crossing_rows.append((
                    current_id,
                    "actual_foot_dotted_hopf",
                    over_owner,
                    under_owner,
                    over_segment,
                    under_segment,
                    over_num,
                    over_den,
                    under_num,
                    under_den,
                    sign,
                    passage_id,
                ))
                occurrence_rows.extend([
                    (
                        current_id,
                        "over",
                        over_owner,
                        over_segment,
                        over_num,
                        over_den,
                        sign,
                    ),
                    (
                        current_id,
                        "under",
                        under_owner,
                        under_segment,
                        under_num,
                        under_den,
                        sign,
                    ),
                ])
                current_id += 1
    insert_crossing_batch(connection, crossing_rows, occurrence_rows)
    return current_id - start_id


def assign_arc_labels(connection):
    next_arc = 0
    updates = []
    for component in COMPONENT_ORDER:
        segments = [
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT segment FROM occurrences WHERE owner=? ORDER BY segment",
                (component,),
            )
        ]
        ordered_events = []
        for segment in segments:
            events = list(
                connection.execute(
                    "SELECT crossing_id,role,param_num,param_den FROM occurrences "
                    "WHERE owner=? AND segment=?",
                    (component, segment),
                )
            )
            events.sort(
                key=lambda row: (
                    Fraction(int(row[2]), int(row[3])),
                    row[1],
                    row[0],
                )
            )
            ordered_events.extend(events)
        count = len(ordered_events)
        labels = list(range(next_arc, next_arc + count))
        for index, event in enumerate(ordered_events):
            incoming = labels[(index - 1) % count]
            outgoing = labels[index]
            updates.append((incoming, outgoing, event[0], event[1]))
            if len(updates) >= 20000:
                connection.executemany(
                    "UPDATE occurrences SET incoming_arc=?,outgoing_arc=? "
                    "WHERE crossing_id=? AND role=?",
                    updates,
                )
                updates.clear()
        connection.execute(
            "INSERT INTO component_summary VALUES(?,?,?,?)",
            (component, count, labels[0], labels[-1]),
        )
        next_arc += count
    if updates:
        connection.executemany(
            "UPDATE occurrences SET incoming_arc=?,outgoing_arc=? "
            "WHERE crossing_id=? AND role=?",
            updates,
        )
    return next_arc


def build_pd_rows(connection, crossing_count):
    connection.execute(
        """
        INSERT INTO pd_rows
        SELECT c.id,
               u.incoming_arc,
               CASE WHEN c.sign=1 THEN o.outgoing_arc ELSE o.incoming_arc END,
               u.outgoing_arc,
               CASE WHEN c.sign=1 THEN o.incoming_arc ELSE o.outgoing_arc END
        FROM crossings c
        JOIN occurrences u ON u.crossing_id=c.id AND u.role='under'
        JOIN occurrences o ON o.crossing_id=c.id AND o.role='over'
        ORDER BY c.id
        """
    )
    if connection.execute("SELECT COUNT(*) FROM pd_rows").fetchone()[0] != crossing_count:
        raise AssertionError("SQLite PD row insertion count changed")


def pairwise_linking(connection):
    matrix = [[0 for _ in COMPONENT_ORDER] for _ in COMPONENT_ORDER]
    for first_index, first in enumerate(COMPONENT_ORDER):
        for second_index in range(first_index + 1, len(COMPONENT_ORDER)):
            second = COMPONENT_ORDER[second_index]
            signed_sum = connection.execute(
                "SELECT COALESCE(SUM(sign),0) FROM crossings WHERE "
                "(over_owner=? AND under_owner=?) OR (over_owner=? AND under_owner=?)",
                (first, second, second, first),
            ).fetchone()[0]
            if signed_sum % 2:
                raise AssertionError(f"odd mixed crossing sum for {first}/{second}")
            matrix[first_index][second_index] = signed_sum // 2
            matrix[second_index][first_index] = signed_sum // 2
    return matrix


def build(database_path):
    projection_receipt = json.loads(PROJECTION_RECEIPT.read_text(encoding="utf-8"))
    if check_projection_receipt(check_full=True)["verdict"] != "PASS_SOURCE_CONNECTOR_PROJECTION_RECEIPT":
        raise AssertionError("source projection receipt did not verify")
    full_projection = Path(projection_receipt["full_cache_path"])
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))
    if database_path.exists():
        database_path.unlink()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA journal_mode=OFF")
    connection.execute("PRAGMA synchronous=OFF")
    connection.execute("PRAGMA temp_store=MEMORY")
    create_schema(connection)
    source_count = add_source_crossings(
        connection, full_projection, central_segment_map(provenance)
    )
    dotted_count = add_dotted_crossings(connection, source_count, cycles, slots)
    crossing_count = source_count + dotted_count
    if (source_count, dotted_count, crossing_count) != (1758060, 3570, 1761630):
        raise AssertionError("actual source PD crossing counts changed")
    connection.execute(
        "CREATE INDEX occurrence_owner_segment ON occurrences(owner,segment)"
    )
    arc_count = assign_arc_labels(connection)
    if arc_count != 2 * crossing_count:
        raise AssertionError("actual source PD arc count changed")
    build_pd_rows(connection, crossing_count)
    linking = pairwise_linking(connection)
    metadata = {
        "schema": "t73_actual_source_standard_pd_sqlite/v1",
        "source_projection_full_sha256": projection_receipt["full_file_sha256"],
        "source_projection_receipt_sha256": projection_receipt["sha256"],
        "connector_provenance_sha256": provenance["sha256"],
        "component_cycles_sha256": cycles["sha256"],
        "dotted_slot_map_sha256": slots["sha256"],
        "component_order": COMPONENT_ORDER,
        "source_crossings": source_count,
        "dotted_crossings": dotted_count,
        "crossing_count": crossing_count,
        "arc_label_count": arc_count,
        "pairwise_linking_matrix": linking,
        "framing_status": "OPEN_SOURCE_PRODUCT_PUSH_OFFS_REQUIRED",
        "verdict": "PASS_ACTUAL_SOURCE_STANDARD_PD_CORE_ONLY",
    }
    for key, value in metadata.items():
        connection.execute(
            "INSERT INTO metadata VALUES(?,?)", (key, json.dumps(value, sort_keys=True))
        )
    connection.commit()
    connection.close()
    receipt = {
        **metadata,
        "database_path": str(database_path),
        "database_size": database_path.stat().st_size,
        "database_sha256": file_sha(database_path),
        "builder_sha256": file_sha(Path(__file__)),
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    result = build(args.database)
    print(
        f"T73_ACTUAL_SOURCE_PD={result['verdict']} crossings={result['crossing_count']}"
    )


if __name__ == "__main__":
    main()
