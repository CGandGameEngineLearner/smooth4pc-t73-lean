from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class P0JohnsonCertificateTest(unittest.TestCase):
    def test_fast_certificate_has_only_geometric_braid_pending(self):
        path = ROOT / "scripts" / "certify_t73_p0_johnson.py"
        spec = importlib.util.spec_from_file_location("p0_johnson", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate(run_geometric_braid=False)
        self.assertEqual(result["P0_status"], "OPEN")
        self.assertFalse(result["checks"]["johnson_ar_affine_bridge"])
        self.assertFalse(result["checks"]["two_cancellations"])
        self.assertFalse(result["checks"]["embedded_framed_collar"])
        self.assertFalse(result["checks"]["ar_passage_binding"])
        self.assertFalse(result["checks"]["geometric_braid"])
        self.assertTrue(result["checks"]["six_sweep_word"])
        self.assertTrue(result["checks"]["gap_free_basis"])
        self.assertTrue(result["checks"]["exact_compact_m2"])
        self.assertTrue(result["checks"]["forty_four_channels"])


if __name__ == "__main__":
    unittest.main()
