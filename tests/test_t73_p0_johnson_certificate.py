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
        self.assertFalse(result["checks"]["geometric_braid"])
        self.assertEqual(result["P0_status"], "OPEN")
        self.assertTrue(all(value for key, value in result["checks"].items() if key not in {"geometric_braid", "noncircular_source_order"}))


if __name__ == "__main__":
    unittest.main()
