from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFIX10 = ROOT / "geometry" / "examples" / "t73_selected_source_tetrahedral_prefix10.json"
GMSH_PREFIX10 = ROOT / "geometry" / "examples" / "t73_selected_source_gmsh_prefix10_frame.json"
GMSH_PREFIX20 = ROOT / "geometry" / "examples" / "t73_selected_source_gmsh_prefix20_frame.json"
SCHEMA = ROOT / "data" / "T73_SELECTED_SOURCE_TETRAHEDRAL_FRAME.schema.json"


def load(filename: str, name: str):
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def optional_meshing_available() -> bool:
    return all(importlib.util.find_spec(name) is not None for name in ("numpy", "triangle", "tetgen"))


class SelectedSourceTetrahedralFrameTest(unittest.TestCase):
    def test_monolithic_resource_guard_rejects_prefix20_and_full(self) -> None:
        builder = load(
            "build_t73_selected_source_tetrahedral_frame.py", "source_frame_guard"
        )
        source = json.loads(builder.SOURCE.read_text(encoding="utf-8"))
        for limit in (20, None):
            with self.assertRaisesRegex(builder.MeshError, "resource-disabled"):
                builder.tetrahedralise(source, limit=limit)

    def test_saved_prefix10_passes_independent_verifier(self) -> None:
        verifier = load(
            "verify_t73_selected_source_tetrahedral_frame.py", "source_prefix_verifier"
        )
        result = verifier.inspect(PREFIX10)
        self.assertEqual(result["verdict"], "PASS_PREFIX_ONLY")
        self.assertEqual(result["arcs"], 10)
        self.assertEqual(result["ribbons"], 10)
        self.assertEqual(result["boundary_components"], 5)
        self.assertEqual(result["exact_exterior_volume"], "63968")

    def test_saved_prefix10_satisfies_schema(self) -> None:
        import jsonschema

        jsonschema.validate(
            json.loads(PREFIX10.read_text(encoding="utf-8")),
            json.loads(SCHEMA.read_text(encoding="utf-8")),
        )

    def test_saved_gmsh_prefix10_is_a_complete_frame_prefix(self) -> None:
        verifier = load(
            "verify_t73_selected_source_tetrahedral_frame.py",
            "source_gmsh_prefix_verifier",
        )
        result = verifier.inspect(GMSH_PREFIX10)
        self.assertEqual(result["verdict"], "PASS_PREFIX_ONLY")
        self.assertEqual(result["arcs"], 10)
        self.assertEqual(result["ribbons"], 10)
        self.assertEqual(result["vertices"], 2664)
        self.assertEqual(result["tetrahedra"], 14599)
        self.assertEqual(result["exact_exterior_volume"], "63968")

        import jsonschema

        jsonschema.validate(
            json.loads(GMSH_PREFIX10.read_text(encoding="utf-8")),
            json.loads(SCHEMA.read_text(encoding="utf-8")),
        )

    def test_saved_gmsh_prefix20_is_a_complete_frame_prefix(self) -> None:
        verifier = load(
            "verify_t73_selected_source_tetrahedral_frame.py",
            "source_gmsh_prefix20_verifier",
        )
        result = verifier.inspect(GMSH_PREFIX20)
        self.assertEqual(result["verdict"], "PASS_PREFIX_ONLY")
        self.assertEqual(result["arcs"], 20)
        self.assertEqual(result["ribbons"], 20)
        self.assertEqual(result["boundary_components"], 5)
        self.assertEqual(result["vertices"], 4134)
        self.assertEqual(result["tetrahedra"], 23725)
        self.assertEqual(result["exact_exterior_volume"], "63968")

        import jsonschema

        jsonschema.validate(
            json.loads(GMSH_PREFIX20.read_text(encoding="utf-8")),
            json.loads(SCHEMA.read_text(encoding="utf-8")),
        )

    def test_current_artifact_is_fail_closed_or_passes_full_verifier(self) -> None:
        verifier = load(
            "verify_t73_selected_source_tetrahedral_frame.py", "source_frame_verifier"
        )
        result = verifier.inspect()
        if verifier.FRAME.exists():
            self.assertEqual(result["verdict"], "PASS")
            self.assertEqual(result["arcs"], 630)
            self.assertEqual(result["ribbons"], 630)
            self.assertEqual(result["boundary_components"], 5)
            self.assertEqual(result["exact_exterior_volume"], "63968")
        else:
            self.assertEqual(result["verdict"], "OPEN")
            self.assertIn("missing", result["reason"])

    def test_exact_determinant_detects_a_flat_tetrahedron(self) -> None:
        verifier = load(
            "verify_t73_selected_source_tetrahedral_frame.py", "source_frame_det"
        )
        self.assertEqual(
            verifier.determinant6(
                [
                    (verifier.Fraction(0), verifier.Fraction(0), verifier.Fraction(0)),
                    (verifier.Fraction(1), verifier.Fraction(0), verifier.Fraction(0)),
                    (verifier.Fraction(0), verifier.Fraction(1), verifier.Fraction(0)),
                    (verifier.Fraction(1), verifier.Fraction(1), verifier.Fraction(0)),
                ]
            ),
            0,
        )

    @unittest.skipUnless(optional_meshing_available(), "optional TetGen toolchain is absent")
    def test_one_ribbon_tetgen_probe_has_five_spheres_and_exact_volume(self) -> None:
        builder = load(
            "build_t73_selected_source_tetrahedral_frame.py", "source_frame_builder"
        )
        source = json.loads(builder.SOURCE.read_text(encoding="utf-8"))
        result = builder.tetrahedralise(source, limit=1)
        summary = builder.verify_result(result, 1)
        self.assertEqual(summary["verdict"], "PASS")
        self.assertEqual(summary["boundary_components"], 5)
        self.assertEqual(summary["exact_exterior_volume"], "63968")
        self.assertEqual(summary["arcs"], 1)
        self.assertEqual(summary["ribbons"], 1)

    @unittest.skipUnless(optional_meshing_available(), "optional Triangle toolchain is absent")
    def test_missing_saved_ruled_triangle_is_rejected(self) -> None:
        builder = load(
            "build_t73_selected_source_tetrahedral_frame.py", "source_frame_mutation"
        )
        source = json.loads(builder.SOURCE.read_text(encoding="utf-8"))
        mutant = copy.deepcopy(source)
        mutant["exterior_intervals"][0]["ruled_ribbon_triangles"].pop()
        with self.assertRaisesRegex(builder.MeshError, "exactly four"):
            builder.build_plc(mutant, limit=1)


if __name__ == "__main__":
    unittest.main()
