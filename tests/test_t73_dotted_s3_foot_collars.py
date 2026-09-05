from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_dotted_s3_foot_collars.py"


class DottedS3FootCollarsTest(unittest.TestCase):
    def test_four_reflection_paired_framed_collars(self):
        spec = importlib.util.spec_from_file_location("verify_foot_collars", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_REFLECTION_PAIRED_FRAMED_MARKED_STRIP_COLLARS_TO_DOTTED_S3")
        self.assertEqual(result["passages"], 1785)
        self.assertEqual(result["push_endpoint_checks"], 3570)


if __name__ == "__main__":
    unittest.main()
