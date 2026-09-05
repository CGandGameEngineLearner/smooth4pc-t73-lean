from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_m1_parallel_annulus_tubular_frame.py"


class M1ParallelAnnulusTubularFrameTest(unittest.TestCase):
    def test_local_tubular_frame(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_m1_tube", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_M1_PARALLEL_ANNULUS_LOCAL_TUBULAR_FRAME")
        self.assertEqual(result["tubular_tetrahedra"], 204)
        self.assertEqual(result["nonlocal_tetrahedron_clearance_status"], "OPEN_EXACT_NONINCIDENT_CELL_CHECK")


if __name__ == "__main__": unittest.main()
