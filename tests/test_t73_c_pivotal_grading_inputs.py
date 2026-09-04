import importlib.util
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_t73_c_pivotal_grading_inputs.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("c_pivotal_grading", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CPivotalGradingFailClosedTest(unittest.TestCase):
    def test_current_repository_remains_open(self):
        checker = load_checker()
        report = checker.generate()
        self.assertEqual(report["status"], "OPEN")
        self.assertFalse(report["pivotal_coefficients_certified"])
        self.assertFalse(report["degree_494_certified"])
        self.assertEqual(report["detector_braid_writhe"], 0)
        self.assertEqual(report["derived"]["formal_sum"], 494)
        missing = "\n".join(report["missing"])
        self.assertIn("T73_C_PIVOTAL_GRADING_INPUT.json", missing)
        self.assertIn("V/V_dual", missing)
        self.assertIn("writhe ledger", missing)

    def test_every_endpoint_names_the_missing_primitive(self):
        checker = load_checker()
        report = checker.generate()
        diagnostics = report["endpoint_diagnostics"]
        self.assertEqual(len(diagnostics), 88)
        self.assertEqual(
            {item["tensor_position_from_boundary_order"] for item in diagnostics},
            set(range(88)),
        )
        self.assertEqual(len({item["physical_endpoint_id"] for item in diagnostics}), 88)
        for item in diagnostics:
            self.assertEqual(item["variance"], "UNDETERMINED")
            self.assertEqual(item["pivotal_sign"], "UNDETERMINED")
            self.assertEqual(item["q_power"], "UNDETERMINED")
            missing = set(item["exact_absent_primitives"])
            self.assertIn("boundary_face_source_or_target", missing)
            self.assertIn("ordered_BPW_A4_duality_atom_path", missing)
            self.assertIn("blanchet_binding_or_detachment_local_normal", missing)

    def test_legacy_all_ones_cannot_certify(self):
        checker = load_checker()
        report = checker.generate()
        legacy = report["legacy_endpoint_coefficients"]
        self.assertEqual(legacy["endpoint_count"], 88)
        self.assertTrue(legacy["all_coefficients_plus_q0"])
        self.assertEqual(legacy["primitive_derivation_count"], 0)
        self.assertFalse(legacy["accepted_for_pivotal_certification"])
        # Two reversed passages contribute two cable copies each.  The old
        # builder used only copy sign and therefore disagrees on four entries.
        self.assertEqual(len(legacy["orientation_disagreement_endpoint_ids"]), 4)
        self.assertFalse(report["pivotal_coefficients_certified"])

    def test_command_exits_nonzero_without_primitive_input(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('"status": "OPEN"', result.stdout)


if __name__ == "__main__":
    unittest.main()
