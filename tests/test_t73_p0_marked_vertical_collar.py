from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_p0_marked_vertical_collar.py"


def load_script():
    spec = importlib.util.spec_from_file_location("marked_collar_verifier", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class P0MarkedVerticalCollarTest(unittest.TestCase):
    def test_static_marked_collar(self) -> None:
        result = load_script().verify()
        self.assertEqual(result["T73_P0_MARKED_VERTICAL_COLLAR"], "PASS")
        self.assertEqual(result["ARCS"], 44)
        self.assertEqual(result["ENDPOINTS"], 88)
        self.assertEqual(result["OWNER_COUNTS"], {"m_2": 42, "r_xy": 2})
        self.assertEqual(result["BRAID_IN_P0"], "ABSENT")
        self.assertEqual(set(result["MUTATIONS"].values()), {"FAIL"})


if __name__ == "__main__":
    unittest.main()
