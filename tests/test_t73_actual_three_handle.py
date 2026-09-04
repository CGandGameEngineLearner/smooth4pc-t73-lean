from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ActualThreeHandleTest(unittest.TestCase):
    def test_actual_spheres_and_hemisphere_maps(self):
        spheres = load("verify_t73_actual_sphere_system").verify()
        self.assertEqual(spheres["REVERSED_SPHERE_MODEL"], "PASS")
        self.assertEqual(spheres["ACTUAL_W2_BOUNDARY"], "OPEN")
        self.assertEqual(spheres["ACTUAL_SPHERE_SYSTEM"], "OPEN")
        self.assertEqual(spheres["CORE_DISK_COUNTS"], [1541, 10118, 2])
        self.assertEqual(spheres["MUTATION_BOUNDARY_COPY"], "FAIL")
        hemispheres = load("verify_t73_hemisphere_movies").verify()
        self.assertEqual(hemispheres["ACTUAL_HEMISPHERE_MOVIES"], "OPEN")
        self.assertFalse(hemispheres["ACTUAL_W2_LASAGNA_MAP"])
        self.assertEqual(hemispheres["A0_IDENTITY"], "PASS_REVERSED_MODEL_ONLY")
        self.assertEqual(hemispheres["A1_ZERO"], "PASS_REVERSED_MODEL_ONLY")
        self.assertEqual(hemispheres["MUTATION_A1_ACTION"], "FAIL")


if __name__ == "__main__":
    unittest.main()
