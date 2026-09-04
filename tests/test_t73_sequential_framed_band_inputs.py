from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_t73_sequential_framed_band_inputs.py"
T_BANDS = ROOT / "geometry" / "t73_cancel_t_hcs.json"
X_BANDS = ROOT / "geometry" / "t73_cancel_x_m1.json"


def load_script():
    spec = importlib.util.spec_from_file_location("framed_band_gate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SequentialFramedBandInputTest(unittest.TestCase):
    def test_current_movie_fails_at_first_band_current_link(self) -> None:
        result = load_script().check()
        self.assertEqual(result["verdict"], "OPEN")
        self.assertEqual(
            result["first_missing"],
            {
                "movie": "t_hcs",
                "band_index": 0,
                "field": "current_link_before",
                "reason": (
                    "the entire current framed link is required because "
                    "earlier slides change the obstacle set"
                ),
            },
        )

    def test_next_gap_is_the_source_attaching_interval(self) -> None:
        module = load_script()
        t_data = json.loads(T_BANDS.read_text(encoding="utf-8"))
        x_data = json.loads(X_BANDS.read_text(encoding="utf-8"))
        mutant = copy.deepcopy(t_data)
        mutant["slide_bands"][0]["current_link_before"] = {
            "components": [],
            "sha256": "0" * 64,
        }
        gap = module.first_gap(mutant, x_data)
        self.assertIsNotNone(gap)
        self.assertEqual(gap["movie"], "t_hcs")
        self.assertEqual(gap["band_index"], 0)
        self.assertEqual(gap["field"], "source_attaching_interval")

    def test_declared_twist_mutation_cannot_bypass_missing_geometry(self) -> None:
        module = load_script()
        t_data = json.loads(T_BANDS.read_text(encoding="utf-8"))
        x_data = json.loads(X_BANDS.read_text(encoding="utf-8"))
        mutant = copy.deepcopy(t_data)
        mutant["slide_bands"][0]["relative_twist"] = 73
        gap = module.first_gap(mutant, x_data)
        self.assertEqual(gap["field"], "current_link_before")

    def test_cli_exits_nonzero_on_current_artifacts(self) -> None:
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["verdict"], "OPEN")


if __name__ == "__main__":
    unittest.main()
