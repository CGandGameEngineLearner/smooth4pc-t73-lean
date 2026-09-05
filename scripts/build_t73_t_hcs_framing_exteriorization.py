#!/usr/bin/env python3
"""Choose outward collar normals for the state-6 framed link."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states, symmetric_coordinate

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
MOVIE = ROOT / "geometry/t73_t_band_sequential_movie.json"
OUTPUT = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def encode(value):
    return [str(coordinate) for coordinate in value]


def spatial_representative(value):
    return tuple(symmetric_coordinate(coordinate) for coordinate in value[:3])


def supporting_faces(first, second, radius):
    if first == second:
        return []
    return [
        signs
        for signs in itertools.product((-1, 1), repeat=3)
        if sum(Fraction(signs[axis]) * first[axis] for axis in range(3)) == radius
        and sum(Fraction(signs[axis]) * second[axis] for axis in range(3)) == radius
    ]


def parallel(first, second):
    return all(
        first[left] * second[right] == first[right] * second[left]
        for left in range(3)
        for right in range(left + 1, 3)
    )


def closest_outward_normal(old_normal, face_constraints, tangent_directions, width):
    candidates = []
    for integer_vector in itertools.product((-1, 0, 1), repeat=3):
        if integer_vector == (0, 0, 0):
            continue
        if min(
            sum(face[axis] * integer_vector[axis] for axis in range(3))
            for face in face_constraints
        ) <= 0:
            continue
        if any(parallel(integer_vector, tangent) for tangent in tangent_directions):
            continue
        normal = tuple(width * coordinate for coordinate in integer_vector) + (Fraction(0),)
        squared_change = sum(
            (normal[axis] - old_normal[axis]) ** 2 for axis in range(4)
        )
        candidates.append((squared_change, integer_vector, normal))
    if not candidates:
        raise AssertionError("no outward integer normal satisfies adjacent collar faces")
    return min(candidates)[2]


def exteriorize_component(points, normals, radius, width):
    spatial = [spatial_representative(value) for value in points]
    segment_faces = [
        supporting_faces(first, second, radius)
        for first, second in zip(spatial, spatial[1:])
    ]
    output = list(normals)
    replacements = []
    for index, (value, old_normal) in enumerate(zip(spatial, normals)):
        if sum(abs(coordinate) for coordinate in value) != radius:
            continue
        constraints = []
        incident_indices = {index - 1, index}
        if index in (0, len(points) - 1):
            incident_indices.update((0, len(points) - 2))
        tangent_directions = []
        for segment_index in sorted(incident_indices):
            if 0 <= segment_index < len(segment_faces):
                constraints.extend(segment_faces[segment_index])
                first = spatial[segment_index]
                second = spatial[segment_index + 1]
                direction = tuple(second[axis] - first[axis] for axis in range(3))
                if direction != (0, 0, 0):
                    tangent_directions.append(direction)
        if not constraints:
            constraints = [
                tuple(
                    -1 if coordinate < 0 else 1 if coordinate > 0 else 0
                    for coordinate in value
                )
            ]
        try:
            new_normal = closest_outward_normal(
                old_normal, constraints, tangent_directions, width / 16
            )
        except AssertionError as error:
            raise AssertionError(f"belt vertex {index}: {error}") from error
        output[index] = new_normal
        if new_normal != old_normal:
            replacements.append({
                "vertex_index": index,
                "old_normal": encode(old_normal),
                "new_normal": encode(new_normal),
                "adjacent_supporting_faces": [list(face) for face in constraints],
            })
    if output[-1] != output[0]:
        raise AssertionError("exteriorized framing does not close by the component deck translation")
    return output, replacements


def build() -> dict:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    radius = Fraction(belts["t_handle"]["belt_sphere"]["radius"])
    components = {}
    for component, (points, normals, seams) in final_states().items():
        width = Fraction(ar_link["components"][component]["full_framing_annulus"]["width"])
        new_normals, replacements = exteriorize_component(
            points, normals, radius, width
        )
        push = [
            tuple(value[axis] + normal[axis] for axis in range(4))
            for value, normal in zip(points, new_normals)
        ]
        components[component] = {
            "width": str(width),
            "outward_collar_width": str(width / 16),
            "replacement_count": len(replacements),
            "normal_replacements": replacements,
            "exteriorized_normal_field_sha256": canonical_sha(
                [encode(value) for value in new_normals]
            ),
            "exteriorized_push_off_sha256": canonical_sha(
                [encode(value) for value in push]
            ),
            "inherited_seam_segment_indices": sorted(seams),
        }
    result = {
        "schema": "t73_t_hcs_framing_exteriorization/v1",
        "ar_link_sha256": ar_link["sha256"],
        "belt_spheres_sha256": belts["sha256"],
        "sequential_movie_sha256": movie["sha256"],
        "selection_rule": (
            "at every belt-sphere vertex choose, from {-1,0,+1}^3 times the "
            "framing width/16, the squared-nearest vector having positive dot "
            "product with every adjacent octahedral supporting-face normal and "
            "not parallel to an incident core edge"
        ),
        "components": components,
        "completion_status": "STATE6_OUTWARD_FRAMING_NORMALS_CONSTRUCTED",
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
        raise AssertionError("t-h_CS framing exteriorization is stale")
    print("T73_T_HCS_FRAMING=STATE6_OUTWARD_FRAMING_NORMALS_CONSTRUCTED")


if __name__ == "__main__":
    main()
