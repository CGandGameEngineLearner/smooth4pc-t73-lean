import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band_canonical_r3_cell_atlas.py"


class XBandCanonicalR3CellAtlasTest(unittest.TestCase):
    def test_all_actual_band_disks(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_ALL_X_BAND_CANONICAL_R3_CELL_ATLAS_FULL",
        )
        self.assertEqual(result["actual_source_band_cells"], 1513)
        self.assertEqual(result["lane_ribbon_triangles"], 12104)
        self.assertEqual(result["surface_product_tetrahedra"], 18156)
        self.assertEqual(result["global_port_gluing"], "OPEN")


if __name__ == "__main__":
    unittest.main()
