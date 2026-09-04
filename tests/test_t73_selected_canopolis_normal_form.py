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
        self.assertEqual(result["T73_SELECTED_CANOPOLIS_NORMAL_FORM"], "PASS_TARGET_ONLY")
        self.assertEqual(result["TARGET_ACTIVE_CORRIDORS"], 44)
        self.assertEqual(result["TARGET_ADDED_Z_ARCS"], 227)
        self.assertEqual(result["TARGET_CYCLIC_CONNECTOR"], "PASS")
        self.assertEqual(result["TARGET_SEPARATING_SPHERE"], "PASS")
        self.assertEqual(result["TARGET_BRAID_DATA"], "ABSENT")
        self.assertEqual(result["SOURCE_RELATIVE_ISOTOPY"], "OPEN")
        self.assertEqual(result["BOUNDARY_ENDPOINT_INCIDENCE"], "OPEN")
        self.assertEqual(set(result["MUTATIONS"].values()), {"FAIL"})


if __name__ == "__main__":
    unittest.main()
