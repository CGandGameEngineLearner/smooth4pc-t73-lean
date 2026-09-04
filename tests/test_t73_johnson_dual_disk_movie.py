from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_johnson_dual_disk_movie.py"
    spec = importlib.util.spec_from_file_location("dual_disk_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonDualDiskMovieTest(unittest.TestCase):
    def test_dual_disk_movie_and_mutation(self):
        result = load_verifier().verify()
        self.assertEqual(result["ACTUAL_H1_DISK_TRANSPORT"], "PASS")
        self.assertEqual(result["FACTORS"], 93)
        self.assertEqual(
            result["SPHERE_COLUMNS"],
            [[-1311, -189, 41], [8608, 1241, -269], [-1, 0, 1]],
        )
        self.assertEqual(result["MUTATION_DISK_SLIDE_ORIENTATION"], "FAIL")
        self.assertEqual(result["POST_CANCELLATION_SURFACE_MAP"], "OPEN")


if __name__ == "__main__":
    unittest.main()
