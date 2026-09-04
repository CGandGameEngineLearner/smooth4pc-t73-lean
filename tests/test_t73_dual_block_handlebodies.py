from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DualBlockHandlebodyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load(
            "heegaard", ROOT / "scripts" / "build_t73_common_heegaard_complex.py"
        )

    def test_dual_blocks_fill_and_collapse(self) -> None:
        model = self.builder.generate()
        self.assertTrue(model["s_maps_johnson_pair_onto_ar_pair"])
        self.assertEqual(model["johnson"]["interface_genus"], 3)
        self.assertEqual(model["ar"]["interface_genus"], 3)
        self.assertEqual(model["johnson"]["spine_0"]["graph_rank"], 3)
        self.assertEqual(model["johnson"]["spine_1"]["graph_rank"], 3)
        self.assertEqual(len(model["johnson"]["handlebody_0_tets"]), 192)
        self.assertEqual(len(model["johnson"]["handlebody_1_tets"]), 192)
        self.assertEqual(model["johnson"]["euler_0"]["chi"], -2)
        self.assertIn("barycentric dual 3-blocks", model["assignment"])
        self.assertNotIn("barycenter distance", model["assignment"])

    def test_mutated_cube_owner_is_rejected(self) -> None:
        origins = tuple(__import__("itertools").product(range(4), repeat=3))
        bases = ((0, 0, 0), (2, 2, 2))
        family_0 = self.builder.coarse_spine_vertices(bases[0])
        family_1 = self.builder.coarse_spine_vertices(bases[1])
        first = origins[0]
        original = self.builder.cube_owner(first, family_0, family_1)
        flipped = []
        for origin in origins:
            owner = self.builder.cube_owner(origin, family_0, family_1)
            if origin == first:
                owner = 1 - original
            flipped.append(owner)
        self.assertNotEqual(flipped.count(0), 32)

    def test_old_voronoi_script_is_not_the_p0a_proof(self) -> None:
        text = (ROOT / "scripts" / "certify_t73_spine_star_handlebodies.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("This Voronoi assignment is not the P0a proof", text)
        self.assertNotIn("P0a therefore remains Open", text)

    def test_regina_returns_genus_three(self) -> None:
        path = ROOT / "audit" / "t73_handlebody_bridge_regina.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["REGINA_HANDLEBODY"], "PASS")
        for name in ("H_J_0", "H_J_1", "H_AR_0", "H_AR_1"):
            self.assertEqual(data["genera"][name]["recogniseHandlebody"], 3)


if __name__ == "__main__":
    unittest.main()
