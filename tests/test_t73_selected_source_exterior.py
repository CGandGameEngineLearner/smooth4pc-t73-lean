from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_selected_source_exterior.py"


def load_script():
    spec = importlib.util.spec_from_file_location("selected_source_exterior", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SelectedSourceExteriorTest(unittest.TestCase):
    def test_full_endpoint_incidence_and_routes(self) -> None:
        result = load_script().verify()
        self.assertEqual(
            result["T73_SELECTED_SOURCE_EXTERIOR"],
            "PASS_CANONICAL_REPRESENTATIVE",
        )
        self.assertEqual(result["CABLED_PASSAGES"], {"y": 88, "z": 542})
        self.assertEqual(
            result["SPHERE_ENDPOINTS"],
            {"Y_minus": 88, "Y_plus": 88, "Z_minus": 542, "Z_plus": 542},
        )
        self.assertEqual(result["TOTAL_ENDPOINTS"], 1260)
        self.assertEqual(result["EXTERIOR_INTERVALS"], 630)
        self.assertEqual(result["RULED_RIBBON_TRIANGLES"], 2520)
        self.assertEqual(result["DISTINCT_RULED_RIBBONS"], "PASS")
        self.assertEqual(
            result["INTERVAL_COUNTS_BY_COPY"],
            {
                "negative": {"active_y_z": 88, "residual_z_z": 227},
                "positive": {"active_y_z": 88, "residual_z_z": 227},
            },
        )
        self.assertEqual(result["CYCLIC_SEAMS"], 4)
        self.assertEqual(result["ACTUAL_AR_RELATIVE_ISOTOPY"], "OPEN")
        self.assertEqual(set(result["MUTATIONS"].values()), {"FAIL"})


if __name__ == "__main__":
    unittest.main()
