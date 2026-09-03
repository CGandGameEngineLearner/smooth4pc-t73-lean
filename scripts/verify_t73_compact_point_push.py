#!/usr/bin/env python3
"""Generate the public T73 point-push rows from a compact sweep schema.

This verifier is independent of the unavailable 2,126,291-crossing PD file.
It proves that the 252 public r_xy/m_2 crossing rows are exactly six explicit
42-crossing sweeps.  It then rebuilds the 44-strand pure-braid word and checks
its pinned identity.  It does *not* identify this collar with the full Kirby
presentation; that marked/framed global join remains a separate obligation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPOSITORY / "data" / "T73_DELTA3_PUBLIC_INPUT.json"

COLUMNS = [
    "source_index",
    "x",
    "y",
    "sign",
    "under_owner",
    "under_segment",
    "over_owner",
    "over_segment",
    "moving_wicket",
    "other_wicket",
    "m2_passage_exponent",
    "geometry",
]

# The 40-step Christoffel schedule between the 41 ordinary wickets.  The same
# schedule controls both the m_2 segment ledger and the long-leg x coordinates.
# Storing this 40-bit choice word is the only non-affine part of the schema.
SEGMENT_DELTAS = (
    32, 28, 32, 28, 32, 28, 32, 32, 28, 32,
    28, 32, 28, 32, 28, 32, 32, 28, 32, 28,
    32, 28, 32, 32, 28, 32, 28, 32, 28, 32,
    28, 32, 32, 28, 32, 28, 32, 28, 32, 28,
)
LONG_X_DELTAS = tuple(112 if value == 32 else 96 for value in SEGMENT_DELTAS)
ORDINARY_WICKETS = range(3, 44)


def canonical_sha(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def prefix_sum(pattern: tuple[int, ...], count: int) -> int:
    if not 0 <= count <= len(pattern):
        raise ValueError(f"prefix count is outside the Christoffel schedule: {count}")
    return sum(pattern[:count])


def segment(base: int, wicket: int) -> int:
    return base + prefix_sum(SEGMENT_DELTAS, wicket - 3)


def long_x(base: int, wicket: int, direction: int) -> int:
    return base + direction * prefix_sum(LONG_X_DELTAS, wicket - 3)


def make_row(
    source_index: int,
    x: int,
    y: int,
    sign: int,
    under_segment: int,
    moving_wicket: int,
    other_wicket: int,
    geometry: str,
) -> list[Any]:
    return [
        source_index,
        x,
        y,
        sign,
        "m_2",
        under_segment,
        "r_xy",
        6 if geometry == "R" else 2,
        moving_wicket,
        other_wicket,
        -1 if max(moving_wicket, other_wicket) == 44 else 1,
        geometry,
    ]


def generate_rows() -> list[list[Any]]:
    rows: list[list[Any]] = []

    # Right leg, positive sweep: the return wicket precedes 3,...,43.
    rows.append(make_row(180, 3984, -10496, 1, 1243, 1, 44, "R"))
    for wicket in ORDINARY_WICKETS:
        rows.append(
            make_row(
                wicket + 178,
                long_x(4080, wicket, 1),
                -10496,
                1,
                segment(27, wicket),
                1,
                wicket,
                "R",
            )
        )

    # Right leg, negative sweep: the return wicket precedes 43,...,3.
    rows.append(make_row(222, 49040, -10496, -1, 1237, 1, 44, "R"))
    for wicket in ORDINARY_WICKETS:
        rows.append(
            make_row(
                266 - wicket,
                long_x(53248, wicket, -1),
                -10496,
                -1,
                segment(21, wicket),
                1,
                wicket,
                "R",
            )
        )

    # Left leg repeats the two long sweeps with moving/other roles reversed.
    for wicket in ORDINARY_WICKETS:
        rows.append(
            make_row(
                177 - wicket,
                long_x(53248, wicket, -1),
                -10488,
                1,
                segment(21, wicket),
                wicket,
                1,
                "L",
            )
        )
    rows.append(make_row(133, 49040, -10488, 1, 1237, 44, 1, "L"))

    rows.append(make_row(91, 3984, -10488, -1, 1243, 44, 1, "L"))
    for wicket in ORDINARY_WICKETS:
        rows.append(
            make_row(
                wicket + 89,
                long_x(4080, wicket, 1),
                -10488,
                -1,
                segment(27, wicket),
                wicket,
                1,
                "L",
            )
        )

    # The two short return sweeps have constant x step 16 and the two
    # intermediate segment offsets 23 and 25.
    for wicket in ORDINARY_WICKETS:
        rows.append(
            make_row(
                89 - wicket,
                3728 - 16 * (wicket - 3),
                -10488,
                1,
                segment(25, wicket),
                wicket,
                1,
                "L",
            )
        )
    rows.append(make_row(45, 3072, -10488, -1, 1239, 44, 1, "L"))

    for wicket in ORDINARY_WICKETS:
        rows.append(
            make_row(
                wicket,
                -3728 + 16 * (wicket - 3),
                -10488,
                -1,
                segment(23, wicket),
                wicket,
                1,
                "L",
            )
        )
    rows.append(make_row(44, -3072, -10488, 1, 1241, 44, 1, "L"))

    rows.sort(key=lambda row: row[0])
    if len(rows) != 252 or len({row[0] for row in rows}) != 252:
        raise AssertionError("compact schema did not generate 252 distinct rows")
    return rows


def inverse_word(word: list[int]) -> list[int]:
    return [-letter for letter in reversed(word)]


def left_pure_generator(i: int, j: int, sign: int) -> list[int]:
    return (
        list(range(j - 1, i, -1))
        + [sign * i, sign * i]
        + [-k for k in range(i + 1, j)]
    )


def right_pure_generator(i: int, j: int, sign: int) -> list[int]:
    return (
        list(range(i, j - 1))
        + [sign * (j - 1), sign * (j - 1)]
        + [-k for k in range(j - 2, i - 1, -1)]
    )


def row_word(row: list[Any]) -> list[int]:
    data = dict(zip(COLUMNS, row))
    i = min(data["moving_wicket"], data["other_wicket"])
    j = max(data["moving_wicket"], data["other_wicket"])
    if data["geometry"] == "L":
        return left_pure_generator(i, j, data["sign"])
    return right_pure_generator(i, j, data["sign"])


def artin_permutation(word: list[int], strand_count: int) -> list[int]:
    permutation = list(range(strand_count))
    for letter in word:
        index = abs(letter) - 1
        permutation[index], permutation[index + 1] = (
            permutation[index + 1],
            permutation[index],
        )
    return permutation


def expected_chronology() -> list[int]:
    return list(range(180, 264)) + list(range(174, 90, -1)) + list(range(86, 2, -1))


def verify(input_path: Path) -> dict[str, Any]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    point_push = data["point_push"]
    if point_push["crossing_row_columns"] != COLUMNS:
        raise AssertionError("public crossing schema differs")

    generated = generate_rows()
    if generated != point_push["crossing_rows"]:
        by_index = {row[0]: row for row in point_push["crossing_rows"]}
        mismatch = next(
            row for row in generated if by_index.get(row[0]) != row
        )
        raise AssertionError(f"generated row differs at source {mismatch[0]}")
    if canonical_sha(generated) != point_push["crossing_rows_sha256"]:
        raise AssertionError("generated crossing-row SHA differs")

    chronology = expected_chronology()
    if chronology != point_push["oriented_source_indices"]:
        raise AssertionError("compact chronology differs")
    by_index = {row[0]: row for row in generated}
    nonpure = [
        row[0]
        for row in generated
        if artin_permutation(row_word(row), 44) != list(range(44))
    ]
    if nonpure:
        raise AssertionError(f"row factors are not pure: {nonpure[:3]}")
    word = [letter for index in chronology for letter in row_word(by_index[index])]
    integrity = point_push["derived_integrity"]
    if len(word) != integrity["B44_length"]:
        raise AssertionError("compact B44 length differs")
    if canonical_sha(word) != integrity["B44_sha256"]:
        raise AssertionError("compact B44 identity differs")
    if artin_permutation(word, 44) != list(range(44)):
        raise AssertionError("compact B44 permutation is not the identity")
    writhe = sum(1 if letter > 0 else -1 for letter in word)
    if writhe != 0:
        raise AssertionError("compact B44 writhe is not zero")

    return {
        "schema": "t73_compact_point_push_six_sweeps/v1",
        "ordinary_wickets": [3, 43],
        "return_wicket": 44,
        "sweeps": 6,
        "factors_per_sweep": 42,
        "factor_count": len(generated),
        "pure_factor_count": len(generated),
        "B44_permutation": "identity",
        "B44_writhe": writhe,
        "B44_positive_letters": sum(letter > 0 for letter in word),
        "B44_negative_letters": sum(letter < 0 for letter in word),
        "segment_delta_period": list(SEGMENT_DELTAS),
        "long_x_delta_period": list(LONG_X_DELTAS),
        "crossing_rows_sha256": canonical_sha(generated),
        "B44_length": len(word),
        "B44_sha256": canonical_sha(word),
        "verdict": "PASS",
        "scope": "local marked collar braid only; no full Kirby identification",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    print(json.dumps(verify(args.input.resolve()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
