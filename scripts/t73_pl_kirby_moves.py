"""Exact rational PL primitives used by the reconstructed T73 Kirby movie.

This module deliberately uses ``Fraction`` rather than floating-point arrays:
the move verifier must decide equality, boundary matching and framing exactly.
NumPy is appropriate for later broad-phase collision searches, but not these
certificate-defining predicates.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

Point = tuple[Fraction, ...]


def as_point(values: Iterable[str | int | Fraction]) -> Point:
    return tuple(Fraction(value) for value in values)


def encode(point: Point) -> list[str]:
    return [str(value) for value in point]


def add(left: Point, right: Point) -> Point:
    if len(left) != len(right):
        raise ValueError("point dimensions differ")
    return tuple(a + b for a, b in zip(left, right))


def negate(point: Point) -> Point:
    return tuple(-value for value in point)


def reflection(point: Point, matrix: Sequence[Sequence[str | int | Fraction]]) -> Point:
    if len(matrix) != len(point) or any(len(row) != len(point) for row in matrix):
        raise ValueError("reflection matrix has incompatible dimension")
    return tuple(sum(Fraction(entry) * value for entry, value in zip(row, point)) for row in matrix)


@dataclass(frozen=True)
class BandRectangle:
    """A framed rectangle around one oriented PL segment."""

    start: Point
    end: Point
    normal: Point
    push_normal: Point

    def __post_init__(self) -> None:
        if len(self.start) != len(self.end) or len(self.start) != len(self.normal):
            raise ValueError("band rectangle dimensions differ")
        if self.start == self.end:
            raise ValueError("band rectangle has a zero-length center segment")

    def vertices(self) -> tuple[Point, Point, Point, Point]:
        left_start, left_end = add(self.start, self.normal), add(self.end, self.normal)
        right_end, right_start = add(self.end, negate(self.normal)), add(self.start, negate(self.normal))
        return left_start, left_end, right_end, right_start

    def triangles(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        return (0, 1, 2), (0, 2, 3)

    def push_off_vertices(self) -> tuple[Point, Point, Point, Point]:
        return tuple(add(vertex, self.push_normal) for vertex in self.vertices())  # type: ignore[return-value]


def validate_polyline(polyline: Sequence[Point]) -> None:
    if len(polyline) < 2:
        raise ValueError("polyline has fewer than two points")
    if any(first == second for first, second in zip(polyline, polyline[1:])):
        raise ValueError("polyline has a zero-length segment")


def inverse_move_name(name: str) -> str:
    return name[8:] if name.startswith("inverse_") else f"inverse_{name}"
