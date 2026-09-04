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


class JohnsonPLGeneratorTest(unittest.TestCase):
    def test_manifest_has_ninety_three_generators(self) -> None:
        path = ROOT / "geometry" / "t73_johnson_generators" / "manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["count"], 93)
        self.assertEqual(len(data["generators"]), 93)
        self.assertEqual(data["product_on_H1"], [[0, 269, 1240], [0, 41, 189], [1, 0, 32]])
        for record in data["generators"]:
            self.assertGreater(int(record["arm_restore_cell_count"]), 0)
            self.assertTrue((ROOT / record["path"]).exists())

    def test_generator_has_required_geometric_fields(self) -> None:
        path = ROOT / "geometry" / "t73_johnson_generators" / "alpha_00.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("cell_decomposition", data)
        self.assertNotIn("straightening", data)
        self.assertIn("section_restore", data)
        self.assertIn("johnson_arm_restore", data)
        self.assertIn("explicit_inverse", data)
        self.assertTrue(data["jacobian_positive"])
        self.assertIn("protected_ball_disjointness", data)
        self.assertIn("induced_transvection_on_H1", data)
        self.assertIn("heegaard_pair", data)
        self.assertEqual(
            data["heegaard_pair_preserved"], data["heegaard_pair"]["preserved"]
        )
        self.assertEqual(data["heegaard_pair"]["cube_center_count"], 64)
        self.assertEqual(data["heegaard_pair"]["tetrahedron_barycenter_count"], 384)
        self.assertFalse(data["legacy_square_fan_used"])
        self.assertEqual(data["johnson_arm_restore"]["status"], "PASS")
        self.assertEqual(data["section_restore"]["cell_count"], 162)
        self.assertGreater(
            float(data["protected_ball_disjointness"]["clearance"].split("/")[0]), 0
        )

    def test_heegaard_and_ball_are_live_not_assumed(self) -> None:
        path = ROOT / "geometry" / "t73_johnson_generators" / "manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn(data["heegaard_preserving_representative"], ("PASS", "OPEN"))
        self.assertIn(data["section_ball_identity"], ("PASS", "OPEN"))
        self.assertEqual(data["heegaard_preserved_count"], 93)
        self.assertEqual(data["heegaard_preserving_representative"], "PASS")

    def test_verifier_recomputes_and_mutations_fail(self) -> None:
        verifier = load(
            "verify_pl", ROOT / "scripts" / "verify_t73_pl_homeomorphism.py"
        )
        result = verifier.verify()
        self.assertEqual(result["JACOBIAN_POSITIVE"], "PASS")
        self.assertEqual(result["INVERSE"], "PASS")
        self.assertEqual(result["H1_TRANVECTION_PRODUCT"], "PASS")
        self.assertEqual(result["MUTATION_JACOBIAN"], "FAIL")
        self.assertEqual(result["MUTATION_SIDE_BIT"], "FAIL")
        self.assertEqual(result["SECTION_RESTORE_CELLS"], "PASS")
        self.assertEqual(result["SECTION_BALL"], "PASS")
        self.assertEqual(result["JOHNSON_ARM_RESTORE"], "PASS")
        self.assertEqual(result["LEGACY_SQUARE_FAN_ABSENT"], "PASS")
        self.assertEqual(result["HEEGAARD_PAIR"], "PASS")
        self.assertEqual(result["COUNT"], 93)


class ActualARLinkTest(unittest.TestCase):
    def test_link_is_polylines_not_words(self) -> None:
        path = ROOT / "geometry" / "t73_actual_ar_link.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for name in ("m_1", "m_2", "m_3"):
            core = data["components"][name]
            self.assertTrue(core["not_a_free_group_word"])
            self.assertGreater(len(core["C_i"]), 2)
            self.assertGreater(len(core["psi_A_C_i"]), 2)
            self.assertIn("lambda_i", core)
            self.assertIn("mu_i", core)
            self.assertIn("framing_annulus_bottom", core)
        for name in ("r_xy", "r_yz", "r_zx"):
            component = data["components"][name]
            self.assertFalse(component["embedded_from_free_word"])
            self.assertTrue(component["disk"]["closed"])
            self.assertGreaterEqual(component["disk"]["vertex_count"], 3)
        self.assertEqual(data["component_count"], 7)
        self.assertEqual(data["components"]["h_CS"]["t_handle_passage_count"], 1)
        self.assertEqual(data["components"]["h_CS"]["framing_annulus"]["relative_twist"], 0)

    def test_verifier_rejects_word_substitution(self) -> None:
        verifier = load(
            "verify_ar", ROOT / "scripts" / "verify_t73_actual_ar_link.py"
        )
        result = verifier.verify()
        self.assertEqual(result["ACTUAL_AR_CORE"], "PASS")
        self.assertEqual(result["ACTUAL_AR_LINK"], "PASS")
        self.assertEqual(result["ACTUAL_FRAMING_ANNULI"], "PASS")
        self.assertEqual(result["BOUND_TO_PSI_A"], "PASS")
        # The coordinate-spine evaluator is now closed by the independent
        # ambient-restore/lane binding.  The whole AR link remains OPEN until
        # the top framing ribbons are transported and checked.
        self.assertEqual(result["ACTUAL_CURVE_EVALUATOR"], "PASS")
        self.assertEqual(result["HEEGAARD_PRESERVING_PSI"], "PASS")
        self.assertEqual(result["NOT_FREE_GROUP_WORDS"], "PASS")
        self.assertEqual(result["DUAL_2_CELLS"], "PASS")
        self.assertEqual(result["MUTATION_ORIENTATION"], "FAIL")
        self.assertEqual(result["MUTATION_WORD_SUBSTITUTION"], "FAIL")
        self.assertEqual(result["MUTATION_CUT_ENDPOINT"], "FAIL")
        self.assertEqual(result["MUTATION_RIBBON_DIRECTION"], "FAIL")
        self.assertEqual(result["MUTATION_RIBBON_WIDTH"], "FAIL")
        self.assertEqual(result["MUTATION_RIBBON_TWIST"], "FAIL")
        self.assertEqual(result["MUTATION_HCS_PASSAGE"], "FAIL")
        self.assertEqual(result["ALL_SEVEN_COMPONENTS"], "PASS")


if __name__ == "__main__":
    unittest.main()
