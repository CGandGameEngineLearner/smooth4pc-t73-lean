from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_paired_saddle_topology.py"


def load_script():
    spec = importlib.util.spec_from_file_location("paired_saddle_topology", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PairedSaddleTopologyTest(unittest.TestCase):
    def test_all_four_supports_satisfy_the_pl_ball_disk_hypotheses(self) -> None:
        result = load_script().verify()
        self.assertEqual(result["verdict"], "PASS_PL_TOPOLOGICAL_HYPOTHESES")
        self.assertEqual(len(result["movies"]), 4)
        self.assertEqual(
            [movie["support_tetrahedra"] for movie in result["movies"]],
            [85, 83, 122, 122],
        )
        self.assertTrue(
            all(movie["boundary_euler"] == 2 for movie in result["movies"])
        )
        self.assertTrue(
            all(movie["source_disk_euler"] == 1 for movie in result["movies"])
        )
        self.assertTrue(
            all(movie["target_disk_euler"] == 1 for movie in result["movies"])
        )


if __name__ == "__main__":
    unittest.main()
