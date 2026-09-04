from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_t73_complete_geometry_bundle.py"
MANIFEST = ROOT / "geometry" / "t73_complete_geometry_bundle_manifest.v1.json"
SCHEMA = ROOT / "data" / "T73_COMPLETE_GEOMETRY_BUNDLE_MANIFEST.schema.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("complete_geometry_bundle", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompleteGeometryBundleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_hashes_counts_and_fail_closed_gates(self) -> None:
        self.builder.validate_manifest(self.manifest)
        self.assertEqual(self.manifest["bundle_status"], "OPEN")
        entries = {entry["id"]: entry for entry in self.manifest["artifacts"]}
        self.assertEqual(
            set(entries),
            {
                "selected_source_exterior",
                "selected_canopolis_target_v2",
                "single_hom_defect_target",
                "defect_aware_currying_audit",
            },
        )
        self.assertTrue(
            all(entry["reconstruction_status"] == "VERIFIED" for entry in entries.values())
        )
        self.assertTrue(all(entry["completion_status"] == "OPEN" for entry in entries.values()))
        self.assertTrue(all(entry["status"] == "OPEN" for entry in entries.values()))

    def test_saved_geometry_counts_are_complete(self) -> None:
        entries = {entry["id"]: entry for entry in self.manifest["artifacts"]}
        source = entries["selected_source_exterior"]["geometry_counts"]
        target = entries["selected_canopolis_target_v2"]["geometry_counts"]
        single = entries["single_hom_defect_target"]["geometry_counts"]
        defect = entries["defect_aware_currying_audit"]["geometry_counts"]
        self.assertEqual(source["total_boundary_endpoints"], 1260)
        self.assertEqual(source["exterior_intervals"], 630)
        self.assertEqual(source["ruled_ribbon_triangles"], 2520)
        self.assertTrue(source["distinct_ribbon_clearance"])
        self.assertEqual(target["target_arcs"], 630)
        self.assertEqual(target["endpoints_per_insertion_ball"], {
            "Y_source": 88,
            "Y_target": 88,
            "Z_source": 542,
            "Z_target": 542,
        })
        self.assertEqual((single["bottom_endpoints"], single["top_endpoints"]), (86, 88))
        self.assertEqual(single["source_to_target_interval_map_entries"], 0)
        self.assertEqual(defect["wrong_side_intervals"], 8)
        self.assertEqual(defect["minimum_independent_reconnections"], 4)

    def test_open_to_verified_mutant_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.manifest)
        mutant["artifacts"][0]["completion_status"] = "VERIFIED"
        mutant["artifacts"][0]["status"] = "VERIFIED"
        payload = {
            key: value for key, value in mutant.items() if key != "manifest_payload_sha256"
        }
        mutant["manifest_payload_sha256"] = self.builder.canonical_sha(payload)
        with self.assertRaises(AssertionError):
            self.builder.validate_manifest(mutant)

        edge_mutant = copy.deepcopy(self.manifest)
        edge_mutant["dependency_edges"][-1]["status"] = "VERIFIED"
        payload = {
            key: value
            for key, value in edge_mutant.items()
            if key != "manifest_payload_sha256"
        }
        edge_mutant["manifest_payload_sha256"] = self.builder.canonical_sha(payload)
        with self.assertRaises(AssertionError):
            self.builder.validate_manifest(edge_mutant)

    def test_schema_freezes_status_vocabulary(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["$defs"]["status"]["enum"], ["VERIFIED", "OPEN"])
        self.assertEqual(schema["properties"]["bundle_status"], {"const": "OPEN"})
        artifact = schema["$defs"]["artifact"]
        self.assertEqual(artifact["properties"]["completion_status"], {"const": "OPEN"})
        self.assertEqual(artifact["properties"]["status"], {"const": "OPEN"})


if __name__ == "__main__":
    unittest.main()
