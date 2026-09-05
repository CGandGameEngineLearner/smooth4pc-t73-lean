from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_dotted_disk_ambient_extensions.py"


class DottedDiskAmbientExtensionsTest(unittest.TestCase):
    def test_reflection_paired_pl_extensions(self):
        spec = importlib.util.spec_from_file_location("verify_dotted_ambient", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_REFLECTION_PAIRED_AMBIENT_DOTTED_DISK_EXTENSIONS",
        )
        self.assertEqual(result["moves"], 1785)
        self.assertEqual(result["track_segments"], 3570)
        self.assertEqual(result["physical_tetrahedron_instances"], 257040)


if __name__ == "__main__":
    unittest.main()
