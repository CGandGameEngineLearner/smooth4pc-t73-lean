from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_selected_canopolis_normal_form.py"


def load_script():
    spec = importlib.util.spec_from_file_location("canopolis_normal_form", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SelectedCanopolisNormalFormTest(unittest.TestCase):
    def test_four_box_split_normal_form(self) -> None:
        result = load_script().verify()
        self.assertEqual(
            result["T73_SELECTED_CANOPOLIS_NORMAL_FORM"],
            "PASS_COMPLETE_TARGET_TEMPLATE",
        )
        self.assertEqual(result["ACTIVE_YZ_PER_CLOSURE"], 88)
        self.assertEqual(result["RESIDUAL_ZZ_PER_CLOSURE"], 227)
        self.assertEqual(result["CYCLIC_CONNECTOR"], "PASS")
        self.assertEqual(result["TARGET_SEPARATING_SPHERE"], "PASS")
        self.assertEqual(result["BRAID_DATA"], "ABSENT")
        self.assertEqual(result["TOTAL_ENDPOINTS"], 1260)
        self.assertEqual(result["TARGET_ARCS"], 630)
        self.assertEqual(result["SOURCE_RELATIVE_ISOTOPY"], "REFUTED_LITERAL_SPLIT")
        self.assertEqual(result["DEFECT_AWARE_CURRYING"], "OPEN")
        self.assertEqual(set(result["MUTATIONS"].values()), {"FAIL"})


if __name__ == "__main__":
    unittest.main()
