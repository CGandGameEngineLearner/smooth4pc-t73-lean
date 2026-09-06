import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_core_push_clearance_verification.py"
)


class OuterCollarCorePushClearanceTest(unittest.TestCase):
    def test_saved_full_gmp_run(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        self.assertEqual(receipt["status"], "PASS_SAVED_FULL_GMP_RUN")
        self.assertEqual(
            receipt["full_result"]["pair_results"]["core/core"]["permitted_incidences"],
            4,
        )
        self.assertEqual(
            receipt["full_result"]["pair_results"]["core/push"]["exact_segment_checks"],
            4_469_079,
        )
        self.assertTrue(receipt["full_result"]["global_core_push_clearance"])


if __name__ == "__main__":
    unittest.main()
