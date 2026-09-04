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
