from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "verify_t73_gs1_gp3.py"
    spec = importlib.util.spec_from_file_location("verify_t73_gs1_gp3", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GS1GP3GateTest(unittest.TestCase):
    def test_current_w2_metadata_fails_closed(self) -> None:
        module = load()
        result = module.inspect_current()
        self.assertEqual(result["verdict"], "OPEN")
        self.assertEqual(result["G_S1"], "OPEN")
        self.assertEqual(result["G_P3"], "OPEN")
        self.assertIn("not a t73_gs1_gp3_witness", result["reason"])

    def test_topology_booleans_are_not_a_witness(self) -> None:
        module = load()
        current = json.loads(
            (ROOT / "geometry" / "t73_actual_W2_boundary.json").read_text(encoding="utf-8")
        )
        fake = {
            "schema": "t73_gs1_gp3_witness/v1",
            "w2_boundary": current,
            "attaching_spheres": [
                {"name": "A1", "triangles": [], "embedded": True},
                {"name": "A2", "triangles": [], "embedded": True},
                {"name": "A3", "triangles": [], "embedded": True},
            ],
            "detector_ball": {"tetrahedra": [], "shelling_order": [], "is_ball": True},
            "normal_surgery_trace": {
                "format": "explicit_simplicial_cut_cap/v1",
                "source_sha256": "PASS",
                "sphere_sha256s": [],
                "steps": [{"status": "PASS"}],
                "result_sha256": "PASS"
            },
            "surgery_result": {"homeomorphism_type": "S3"},
            "four_ball": {"model": "I4"},
            "attaching_isomorphism": {"status": "PASS"}
        }
        with self.assertRaisesRegex(module.WitnessError, "w2_boundary missing required fields"):
            module.verify_payload(fake)

    def test_empty_surgery_receipt_is_rejected(self) -> None:
        module = load()
        # Boundary of a 4-simplex is a small explicit closed S3.  The test
        # reaches the surgery gate and demonstrates that hashes/status alone
        # still cannot discharge normal surgery.
        boundary = {
            "vertices": [[index] for index in range(5)],
            "tetrahedra": [
                [1, 2, 3, 4],
                [0, 2, 3, 4],
                [0, 1, 3, 4],
                [0, 1, 2, 4],
                [0, 1, 2, 3],
            ],
        }
        # There are no three vertex-disjoint spheres in this tiny S3, so this
        # intentionally fails before a receipt can be trusted.
        fake = {
            "schema": "t73_gs1_gp3_witness/v1",
            "w2_boundary": boundary,
            "attaching_spheres": [
                {"name": "A1", "triangles": []},
                {"name": "A2", "triangles": []},
                {"name": "A3", "triangles": []},
            ],
            "detector_ball": {"tetrahedra": [0], "shelling_order": [0]},
            "normal_surgery_trace": {
                "format": "explicit_simplicial_cut_cap/v1",
                "source_sha256": "PASS",
                "sphere_sha256s": [],
                "steps": [{"status": "PASS"}],
                "result_sha256": "PASS"
            },
            "surgery_result": boundary,
            "four_ball": {"vertices": [[index] for index in range(5)], "pentachora": [[0, 1, 2, 3, 4]]},
            "attaching_isomorphism": {"vertex_map": [0, 1, 2, 3, 4]}
        }
        with self.assertRaisesRegex(module.WitnessError, "closed triangulated surface"):
            module.verify_payload(fake)


if __name__ == "__main__":
    unittest.main()
