from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "verify_t73_coefficient_exterior.py"
    spec = importlib.util.spec_from_file_location("coefficient_exterior", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tetra_ball_frame():
    return {
        "complex": {
            "vertices": [[0], [1], [2], [3]],
            "tetrahedra": [[0, 1, 2, 3]],
        },
        "boundary_components": {
            "outer": [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]
        },
        "arcs": [],
        "ribbons": [],
    }


def tetra_ball_with_framed_arc():
    frame = tetra_ball_frame()
    frame["arcs"] = [
        {
            "name": "a",
            "edge_path": [0, 1],
            "start_boundary": "outer",
            "end_boundary": "outer",
        }
    ]
    frame["ribbons"] = [
        {
            "name": "R_a",
            "core_arc": "a",
            "push_off_path": [2, 3],
            "triangles": [[0, 1, 3], [0, 3, 2]],
        }
    ]
    return frame


class CoefficientExteriorTest(unittest.TestCase):
    def test_current_constructor_output_fails_closed(self) -> None:
        module = load()
        result = module.inspect_current()
        self.assertEqual(result["verdict"], "OPEN")
        self.assertIn("not a t73_coefficient_exterior", result["reason"])

    def test_simple_ball_frame_and_identity_ambient_map(self) -> None:
        module = load()
        frame = tetra_ball_frame()
        before = module.validate_frame(frame, expected_components=1)
        after = module.validate_frame(copy.deepcopy(frame), expected_components=1)
        module.verify_ambient_isomorphism(
            before, after, {"vertex_map": [0, 1, 2, 3]}
        )

    def test_ambient_vertex_mutation_is_rejected(self) -> None:
        module = load()
        frame = tetra_ball_frame()
        before = module.validate_frame(frame, expected_components=1)
        after = module.validate_frame(copy.deepcopy(frame), expected_components=1)
        with self.assertRaisesRegex(module.ExteriorError, "not a bijection"):
            module.verify_ambient_isomorphism(
                before, after, {"vertex_map": [0, 0, 2, 3]}
            )

    def test_hashes_and_booleans_are_not_geometry(self) -> None:
        module = load()
        fake = {
            "schema": "t73_coefficient_exterior_isotopy/v1",
            "initial": {"triangulated": True, "sha256": "PASS"},
            "moves": [],
            "final": {"split": True},
        }
        with self.assertRaisesRegex(ValueError, "dependencies|missing"):
            module.verify_payload(fake)

    def test_empty_identity_movie_is_rejected(self) -> None:
        module = load()
        dependencies, _source, _target = module.current_dependencies()
        fake = {
            "schema": "t73_coefficient_exterior_isotopy/v1",
            "dependencies": dependencies,
            "initial": tetra_ball_frame(),
            "moves": [],
            "final": tetra_ball_frame(),
            "initial_source_binding": [],
            "final_target_binding": [],
        }
        with self.assertRaisesRegex(ValueError, "nonempty ambient movie"):
            module.verify_payload(fake)

    def test_stale_source_target_dependencies_are_rejected(self) -> None:
        module = load()
        dependencies, _source, _target = module.current_dependencies()
        dependencies["source_exterior_sha256"] = "0" * 64
        fake = {
            "schema": "t73_coefficient_exterior_isotopy/v1",
            "dependencies": dependencies,
            "initial": tetra_ball_frame(),
            "moves": [{"kind": "unsupported", "after": tetra_ball_frame()}],
            "final": tetra_ball_frame(),
            "initial_source_binding": [],
            "final_target_binding": [],
        }
        with self.assertRaisesRegex(ValueError, "dependencies"):
            module.verify_payload(fake)

    def test_schema_requires_dependencies_and_bijections(self) -> None:
        module = load()
        schema = json.loads(module.SCHEMA.read_text(encoding="utf-8"))
        self.assertTrue(
            {
                "dependencies",
                "initial_source_binding",
                "final_target_binding",
            }
            <= set(schema["required"])
        )

    def test_duplicate_source_interval_binding_is_rejected(self) -> None:
        module = load()
        _dependencies, source, target = module.current_dependencies()
        endpoint_ball = {
            endpoint["endpoint_id"]: sphere["name"]
            for sphere in source["insertion_spheres"]
            for endpoint in sphere["endpoints"]
        }
        boundary = {
            "Y_minus": "y_left",
            "Y_plus": "y_right",
            "Z_minus": "z_left",
            "Z_plus": "z_right",
        }
        arcs, bindings = [], []
        for index, interval in enumerate(source["exterior_intervals"]):
            name = f"arc:{index}"
            vertices = [2 * index, 2 * index + 1]
            arcs.append(
                {
                    "name": name,
                    "edge_path": vertices,
                    "start_boundary": boundary[endpoint_ball[interval["from_endpoint_id"]]],
                    "end_boundary": boundary[endpoint_ball[interval["to_endpoint_id"]]],
                }
            )
            bindings.append(
                {
                    "source_interval_id": interval["interval_id"],
                    "arc_name": name,
                    "endpoint_ids": [
                        interval["from_endpoint_id"], interval["to_endpoint_id"]
                    ],
                    "endpoint_vertices": vertices,
                }
            )
        bindings[1] = copy.deepcopy(bindings[0])
        frame = {"raw": {"arcs": arcs}}
        payload = {
            "initial_source_binding": bindings,
            "final_target_binding": [{} for _ in range(630)],
        }
        with self.assertRaisesRegex(ValueError, "not bijective"):
            module.verify_source_target_bindings(payload, frame, frame, source, target)

    def test_explicit_framed_arc_subcomplex(self) -> None:
        module = load()
        module.validate_frame(tetra_ball_with_framed_arc(), expected_components=1)

    def test_subdivided_connectors_and_unequal_side_paths_are_accepted(self) -> None:
        module = load()
        # A fan triangulation of a disk with boundary
        # 0--1--2--3--4--5--0.  Core, push-off and connector paths need not
        # have matching subdivision counts.
        frame = {
            "complex": {
                "vertices": [[i] for i in range(7)],
                "tetrahedra": [
                    [0, 1, 6, 5],
                    [1, 2, 6, 5],
                    [2, 3, 6, 5],
                    [3, 4, 6, 5],
                ],
            },
            "boundary_components": {},
            "arcs": [],
            "ribbons": [],
        }
        # Exercise only the ribbon-disk helper with an independently valid
        # abstract disk; full ambient validation is covered by the other tests.
        triangles = [(0, 1, 6), (1, 2, 6), (2, 3, 6), (3, 4, 6), (4, 5, 6), (5, 0, 6)]
        boundary, _vertices = module.validate_surface_disk(
            triangles, module.load_gate(), "subdivided ribbon"
        )
        expected = {
            (0, 1), (1, 2),  # core
            (3, 4),          # push
            (2, 3),          # direct end connector
            (4, 5), (0, 5),  # subdivided start connector
        }
        self.assertEqual(boundary, expected)

    def test_ribbon_boundary_mutation_is_rejected(self) -> None:
        module = load()
        mutant = tetra_ball_with_framed_arc()
        mutant["ribbons"][0]["triangles"].pop()
        with self.assertRaisesRegex(ValueError, "disk|boundary"):
            module.validate_frame(mutant, expected_components=1)


if __name__ == "__main__":
    unittest.main()
