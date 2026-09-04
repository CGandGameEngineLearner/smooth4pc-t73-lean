import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_t73_point_push_gauge.py"
ARTIFACT = ROOT / "audit" / "t73_point_push_gauge.json"


def load_audit():
    spec = importlib.util.spec_from_file_location("point_push_gauge", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PointPushGaugeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = load_audit()
        cls.result = cls.audit.generate()

    def test_committed_artifact_rebuilds(self):
        self.assertEqual(json.loads(ARTIFACT.read_text(encoding="utf-8")), self.result)

    def test_inverse_loop_changes_cubic_to_zero(self):
        self.assertEqual(self.result["original"]["h3_cubic"], 2624)
        self.assertEqual(self.result["inverse_loop_composition"]["h3_cubic"], 0)
        self.assertEqual(self.result["inverse_loop_composition"]["free_reduced_length"], 0)
        self.assertEqual(self.result["original"]["writhe"], 0)
        self.assertEqual(self.result["inverse_loop_composition"]["writhe"], 0)

    def test_naturality_distinguishes_conjugation_from_composition(self):
        naturality = self.result["naturality_calculation"]
        self.assertTrue(naturality["coordinate_change"]["invariant"])
        self.assertFalse(naturality["loop_composition"]["invariant"])
        self.assertFalse(self.result["adjudication"]["bpw_mww_naturality_forces_zero"])


if __name__ == "__main__":
    unittest.main()
