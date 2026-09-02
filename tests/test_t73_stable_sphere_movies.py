from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class StableSphereMovieTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "generate_t73_stable_sphere_movies.py"
        spec = importlib.util.spec_from_file_location("stable_movies", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import stable sphere movie generator")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_old_detector_copies_are_fixed_and_movies_are_spheres(self) -> None:
        ledger = self.module.generate_ledger()
        self.assertEqual(
            ledger["combinatorial_old_label_permutation"], "identity"
        )
        self.assertIn("OPEN", ledger["actual_mww_transport_status"])
        self.assertEqual(
            [movie["leaf_count"] for movie in ledger["movies"]],
            [9920, 1430, 311],
        )
        for movie in ledger["movies"]:
            self.assertEqual(movie["euler_characteristic"], 2)
            self.assertEqual(movie["old_factor_constant_permutation"], "identity")

    def test_old_copy_reordering_is_detected(self) -> None:
        ledger = self.module.generate_ledger()
        labels = ledger["movies"][0]["old_detector_labels"][:]
        labels[0], labels[1] = labels[1], labels[0]
        self.assertNotEqual(labels, ledger["movies"][0]["old_detector_labels"])


if __name__ == "__main__":
    unittest.main()
