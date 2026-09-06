import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_support_cut_r3_shell.py"


class SupportCutR3ShellTest(unittest.TestCase):
    def test_exact_shell(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(result["verdict"], "PASS_X_M1_SUPPORT_CUT_EXACT_R3_SHELL")
        self.assertEqual(result["tetrahedra"], 144)
        self.assertEqual(result["exact_volume"], "992")
        self.assertEqual(result["recognized_type"], "S2 x I")


if __name__ == "__main__":
    unittest.main()
