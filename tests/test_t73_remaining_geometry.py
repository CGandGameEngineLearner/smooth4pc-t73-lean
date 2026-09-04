from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LocalStabilizationTest(unittest.TestCase):
    def test_counit_identities_and_no_split_unknot(self) -> None:
        movies = load("verify_t73_local_psi_movies").generate()
        self.assertFalse(movies["split_unknot_frobenius_factor"])
        self.assertEqual(movies["double_counit_delta"]["1"], 0)
        self.assertEqual(movies["double_counit_delta"]["X"], 1)
        self.assertEqual(len(movies["movies"]), 5)
        self.assertTrue(all(not movie["split_unknot_used"] for movie in movies["movies"]))


class HandleCancellationTest(unittest.TestCase):
    def test_live_intersection_is_not_assumed(self) -> None:
        belts = load("build_t73_belt_spheres").build(write=False)
        self.assertIn(belts["status"]["t_hcs_intersection_one"], ("PASS", "OPEN"))
        self.assertIn(belts["status"]["x_m1_intersection_one"], ("PASS", "OPEN"))
        if belts["t_handle"]["geometric_intersection"] != 1:
            self.assertEqual(belts["status"]["t_hcs_intersection_one"], "OPEN")

    def test_cancellation_mutation_fails(self) -> None:
        verifier = load("verify_t73_handle_cancellation")
        verifier.build(write=True)
        result = verifier.verify()
        self.assertEqual(result["MUTATION_INTERSECTION"], "FAIL")
        self.assertEqual(result["SELF_REPORTED_PASS_REJECTED"], "PASS")


class CutTangleTest(unittest.TestCase):
    def test_cut_tangle_does_not_read_expected_b44(self) -> None:
        load("verify_t73_handle_cancellation").build(write=True)
        tangle = load("build_t73_actual_cut_tangle").build(write=False)
        self.assertFalse(tangle["derived_from_expected_B44"])
        self.assertIn(tangle["status"], ("PASS", "OPEN"))


class SphereSystemTest(unittest.TestCase):
    def test_lasagna_map_stays_false(self) -> None:
        spheres = load("build_t73_actual_sphere_system").build(write=False)
        self.assertFalse(spheres["actual_w2_lasagna_map"])
        self.assertFalse(spheres["hj_lemmas_55_57_invoked"])
        self.assertEqual(spheres["status"], "OPEN")
        hemispheres = load("verify_t73_hemisphere_movies").build(write=False)
        self.assertFalse(hemispheres["actual_w2_lasagna_map"])
        self.assertEqual(hemispheres["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
