import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCRIPT = SCRIPTS / "audit_t73_x_band_global_r3_push_disk_obstruction.py"


class XBandGlobalR3PushDiskObstructionTest(unittest.TestCase):
    def test_first_exact_collision(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            spec = importlib.util.spec_from_file_location("audit", SCRIPT)
            assert spec and spec.loader
            audit = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(audit)
            result = audit.build()
        finally:
            sys.path.remove(str(SCRIPTS))
        self.assertEqual(
            result["verdict"],
            "PASS_X_BAND_GLOBAL_PUSH_DISK_COLLISION_OBSTRUCTION",
        )
        self.assertEqual(result["first_exact_collision"], {
            "band_index": 0,
            "core_triangle_index": 0,
            "push_triangle_index": 2,
        })
        self.assertEqual(result["global_push_disk_status"], "REFUTED")


if __name__ == "__main__":
    unittest.main()
