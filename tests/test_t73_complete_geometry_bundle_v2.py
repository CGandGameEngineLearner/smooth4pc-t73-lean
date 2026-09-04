from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_t73_complete_geometry_bundle_v2.py"
MANIFEST = ROOT / "geometry" / "t73_complete_geometry_bundle_manifest.v2.json"
SCHEMA = ROOT / "data" / "T73_COMPLETE_GEOMETRY_BUNDLE_V2.schema.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("t73_bundle_v2", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompleteGeometryBundleV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_is_exact_live_rebuild(self):
        self.builder.validate(self.manifest)
        self.assertEqual(self.manifest["bundle_status"], "OPEN")
        self.assertEqual(len(self.manifest["artifacts"]), 10)
        self.assertEqual(len(self.manifest["t73_completion_gates"]), 4)

    def test_schema_and_closed_counts(self):
        import jsonschema

        jsonschema.validate(
            self.manifest, json.loads(SCHEMA.read_text(encoding="utf-8"))
        )
        self.assertEqual(
            self.manifest["verified_counts"],
            {
                "source_endpoints": 1260,
                "source_intervals": 630,
                "source_ruled_ribbon_triangles": 2520,
                "coend_wrong_side_intervals": 8,
                "coend_oriented_band_obligations": 4,
                "tetgen_prefix_ribbons": 10,
                "pd_fixture_core_components": 7,
                "gmsh_probe_ribbons": 20,
                "gmsh_frame_ribbons": 10,
            },
        )

    def test_fixture_prefix_and_typing_never_promote_completion(self):
        self.assertTrue(
            all(
                item["t73_completion_status"] == "OPEN"
                for item in self.manifest["artifacts"]
            )
        )
        self.assertTrue(
            all(item["status"] == "OPEN" for item in self.manifest["t73_completion_gates"])
        )
        mutant = copy.deepcopy(self.manifest)
        mutant["artifacts"][-1]["t73_completion_status"] = "VERIFIED"
        with self.assertRaises(AssertionError):
            self.builder.validate(mutant)


if __name__ == "__main__":
    unittest.main()
