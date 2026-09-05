from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_m1_parallel_annulus_ambient_ejection.py"


class M1ParallelAnnulusAmbientEjectionTest(unittest.TestCase):
    def test_local_ambient_ejection_cells(self):
        spec = importlib.util.spec_from_file_location("verify_m1_ejection", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_LOCAL_CELLS")
        self.assertEqual(result["tetrahedra"], 408)
        self.assertEqual(result["support_clearance_status"], "OPEN_EXTENDED_MINUS1_TO2_TUBE_CLEARANCE")


if __name__ == "__main__": unittest.main()
