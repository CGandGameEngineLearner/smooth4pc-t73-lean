import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_t73_x_m1_complete_framed_outer_interface_gap.py"


class CompleteFramedOuterInterfaceGapTest(unittest.TestCase):
    def test_all_outer_interfaces_are_explicit_and_open(self):
        spec = importlib.util.spec_from_file_location("audit", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["interface_count"], 3026)
        self.assertEqual(result["core_port_match_count"], 0)
        self.assertEqual(result["push_port_match_count"], 0)
        self.assertEqual(result["distinct_core_displacement_count"], 3026)
        self.assertEqual(
            result["integration_status"], "OPEN_3026_RELATIVE_FRAMED_COLLAR_EXTENSIONS"
        )


if __name__ == "__main__":
    unittest.main()
