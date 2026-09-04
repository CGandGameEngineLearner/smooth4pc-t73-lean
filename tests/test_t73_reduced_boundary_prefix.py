from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReducedBoundaryPrefixTest(unittest.TestCase):
    def test_connected_sum_boundary_and_generators(self) -> None:
        module = load("build_t73_reduced_boundary_prefix")
        gate = load("verify_t73_gs1_gp3")
        result = module.build_boundary()
        checked = gate.validate_closed_3_complex(
            result["boundary_complex"], "boundary"
        )
        self.assertEqual(len(checked["vertices"]), 20)
        self.assertEqual(len(checked["tetrahedra"]), 70)
        self.assertEqual(result["boundary_sha256"], checked["sha256"])
        self.assertIsNone(
            result["attaching_components"]["simplicial_edge_cycles"]
        )
        self.assertIsNone(
            result["attaching_components"][
                "framing_annulus_triangle_subcomplexes"
            ]
        )

    def test_identity_dehn_filling_replays(self) -> None:
        module = load("build_t73_reduced_boundary_prefix")
        gate = load("verify_t73_gs1_gp3")
        solid = module.canonical_solid_torus()
        first_tets = solid["tetrahedra"]
        boundary_vertices = {
            vertex
            for face in module.boundary_faces(
                [tuple(tet) for tet in first_tets], gate
            )
            for vertex in face
        }
        second_map = []
        next_interior = 12
        for vertex in range(12):
            if vertex in boundary_vertices:
                second_map.append(vertex)
            else:
                second_map.append(next_interior)
                next_interior += 1
        second_tets = [
            sorted(second_map[vertex] for vertex in tet) for tet in first_tets
        ]
        source = {
            "vertices": [{"double_vertex": index} for index in range(next_interior)],
            "tetrahedra": first_tets + second_tets,
        }
        gate.validate_closed_3_complex(source, "solid_torus_double")
        removed_interior = {3, 7, 11}
        surviving = [
            vertex for vertex in range(next_interior)
            if vertex not in removed_interior
        ]
        reindex = {old: new for new, old in enumerate(surviving)}
        new_vertices = [
            {"fresh_filling_core": index} for index in range(3)
        ]
        filling_map = [
            (
                f"new:{[3, 7, 11].index(vertex)}"
                if vertex in removed_interior
                else vertex
            )
            for vertex in range(12)
        ]
        mapped_first_tets = []
        for tet in first_tets:
            mapped = []
            for vertex in tet:
                if vertex in removed_interior:
                    mapped.append(
                        len(surviving) + [3, 7, 11].index(vertex)
                    )
                else:
                    mapped.append(reindex[vertex])
            mapped_first_tets.append(sorted(mapped))
        result = {
            "vertices": [source["vertices"][vertex] for vertex in surviving]
            + new_vertices,
            "tetrahedra": [
                sorted(reindex[vertex] for vertex in tet)
                for tet in second_tets
            ] + mapped_first_tets,
        }
        step = {
            "component": "synthetic_core",
            "removed_tetrahedra": list(range(len(first_tets))),
            "removal_vertex_map": list(range(12)),
            "attaching_curve": solid["core"],
            "filling_vertex_map": filling_map,
            "new_vertices": new_vertices,
            "result_vertex_reindex": [
                [old, reindex[old]] for old in surviving
            ],
            "framing_curve": solid["meridian"],
            "result": result,
        }
        self.assertEqual(
            module.replay_dehn_filling_step(source, step), result
        )
        mutant = copy.deepcopy(step)
        mutant["framing_curve"] = solid["longitude"]
        with self.assertRaisesRegex(ValueError, "filling meridian"):
            module.replay_dehn_filling_step(source, mutant)
        reuse = copy.deepcopy(step)
        reuse["filling_vertex_map"][3] = 3
        with self.assertRaisesRegex(ValueError, "fresh new:k"):
            module.replay_dehn_filling_step(source, reuse)

    def test_dehn_filling_rejects_boolean_only_step(self) -> None:
        module = load("build_t73_reduced_boundary_prefix")
        boundary = module.build_boundary()["boundary_complex"]
        with self.assertRaisesRegex(
            ValueError, "missing required fields"
        ):
            module.replay_dehn_filling_step(
                boundary, {"component": "m_2", "status": "PASS"}
            )


if __name__ == "__main__":
    unittest.main()
