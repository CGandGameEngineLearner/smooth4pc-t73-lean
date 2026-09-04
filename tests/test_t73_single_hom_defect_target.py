from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_single_hom_defect_target.py"


def load_script():
    spec = importlib.util.spec_from_file_location("single_hom_target", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SingleHomDefectTargetTest(unittest.TestCase):
    def test_target_is_explicit_and_source_map_stays_open(self) -> None:
        result = load_script().verify()
        self.assertEqual(result["T73_SINGLE_HOM_DEFECT_TARGET"], "PASS_TARGET_ONLY")
        self.assertEqual(result["MORPHISM"], "P86_TO_P88")
        self.assertEqual(result["THROUGH"], 86)
        self.assertEqual(result["CUP"], 1)
        self.assertEqual(result["SOURCE_INTERVALS"], 630)
        self.assertEqual(result["SOURCE_TO_TARGET_MAP"], "OPEN")
        self.assertEqual(result["GRADING"], "UNDETERMINED")


if __name__ == "__main__":
    unittest.main()
