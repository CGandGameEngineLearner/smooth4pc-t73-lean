import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_t73_defect_aware_currying.py"
ARTIFACT = ROOT / "audit" / "t73_defect_aware_currying.json"


def load_audit():
    spec = importlib.util.spec_from_file_location("defect_currying", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DefectAwareCurryingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_audit()
        cls.result = cls.module.build()

    def test_committed_artifact(self):
        self.assertEqual(json.loads(ARTIFACT.read_text(encoding="utf-8")), self.result)

    def test_eight_exceptions_come_from_two_negative_y_sources(self):
        self.assertEqual(self.result["active_interval_count"], 176)
        self.assertEqual(self.result["correct_side_count"], 168)
        self.assertEqual(self.result["wrong_side_count"], 8)
        self.assertEqual(
            self.result["negative_base_y_sources"],
            ["m_2:C_i", "r_xy:vertex:1"],
        )

    def test_four_reconnections_do_not_make_one_defect(self):
        self.assertEqual(self.result["minimum_independent_reconnections"], 4)
        self.assertEqual(len(self.result["proposed_endpoint_reconnections"]), 4)
        self.assertEqual(self.result["active_boundary_endpoints_after_pivotal_mates"], 176)
        self.assertEqual(self.result["P86_to_P88_boundary_endpoints"], 174)
        self.assertFalse(self.result["one_defect_derived_from_eight_wrong_intervals"])
        for item in self.result["proposed_endpoint_reconnections"]:
            self.assertEqual(
                item["left_or_right_mate"], "NOT_APPLICABLE_TO_RECONNECTION"
            )
            self.assertEqual(item["Blanchet_sign"], "UNDETERMINED")
            self.assertTrue(item["orientation_checked"])
            self.assertEqual(item["status"], "UNREALIZED")


if __name__ == "__main__":
    unittest.main()
