from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExternalGeometryBoundaryTest(unittest.TestCase):
    def test_no_fake_external_geometry_inhabitant(self) -> None:
        path = ROOT / "scripts" / "check_t73_external_geometry_boundary.py"
        spec = importlib.util.spec_from_file_location("external_boundary", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check()

    def test_default_pdf_destination(self) -> None:
        source = (ROOT / "scripts" / "build_papers.sh").read_text(encoding="utf-8")
        self.assertIn('output_dir="$repo_root/output/pdf"', source)
        self.assertIn('mode="${1:---english}"', source)
        self.assertIn("spc4-t73-candidate.pdf", source)


if __name__ == "__main__":
    unittest.main()
