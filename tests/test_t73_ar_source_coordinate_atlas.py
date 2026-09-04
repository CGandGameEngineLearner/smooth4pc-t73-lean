from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "geometry" / "t73_ar_source_coordinate_atlas.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ARSourceCoordinateAtlasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load("build_t73_ar_source_coordinate_atlas")
        cls.verifier = load("verify_t73_ar_source_coordinate_atlas")
        cls.stored = json.loads(ATLAS.read_text(encoding="utf-8"))

    def test_committed_atlas_is_live_rebuild(self) -> None:
        self.assertEqual(self.stored, self.builder.build(write=False))
        result = self.verifier.validate(self.stored)
        self.assertEqual(result["verdict"], "PASS_PREFIX_ONLY")
        self.assertEqual(result["common_kirby_presentation"], "OPEN")
        self.assertEqual(result["t_belt_constant_u_lift"], "PASS")
        self.assertEqual(result["x_belt_positive_normal_face"], "PASS")

    def test_all_seven_actual_pre_cancel_cores_are_bound(self) -> None:
        cores = self.stored["pre_cancellation_cores"]
        self.assertEqual(
            set(cores),
            {"m_1", "m_2", "m_3", "h_CS", "r_xy", "r_yz", "r_zx"},
        )
        self.assertTrue(all(record["closed_verified"] for record in cores.values()))
        self.assertEqual(cores["m_2"]["coordinate_dimension"], [4])
        self.assertEqual(cores["r_xy"]["coordinate_dimension"], [3])
        self.assertEqual(cores["m_3"]["vertex_count"], 8783)

    def test_framing_gap_is_not_hidden(self) -> None:
        cores = self.stored["pre_cancellation_cores"]
        for name in ("m_1", "m_2", "m_3", "h_CS"):
            self.assertEqual(cores[name]["framing"]["status"], "PROCEDURAL_SOURCE_DATA")
        for name in ("r_xy", "r_yz", "r_zx"):
            self.assertEqual(cores[name]["framing"]["status"], "OPEN")
            self.assertIn("no closed push-off", cores[name]["framing"]["reason"])
        status = self.stored["status"]
        self.assertEqual(status["upstream_actual_framed_ar_link_claim"], "PASS")
        self.assertEqual(status["explicit_dual_cell_ribbon_count"], 0)
        self.assertEqual(status["explicit_pre_cancellation_dotted_meridian_count"], 0)

    def test_pre_and_post_snapshots_are_not_mixed(self) -> None:
        snapshots = self.stored["presentation_snapshots"]
        self.assertEqual(
            (snapshots["pre_cancellation"]["required_dotted_meridians"],
             snapshots["pre_cancellation"]["required_two_handle_cores"]),
            (4, 7),
        )
        self.assertEqual(
            (snapshots["post_cancellation"]["required_dotted_meridians"],
             snapshots["post_cancellation"]["required_two_handle_cores"]),
            (2, 5),
        )

    def test_first_missing_transitions_are_exact(self) -> None:
        missing = self.stored["missing_transitions_in_order"]
        self.assertEqual(
            [item["id"] for item in missing[:2]],
            [
                "fiber_dual_H2_to_mapping_torus",
                "x_belt_local_to_mapping_torus_or_cut_handlebody",
            ],
        )
        self.assertIn("not nu=u", missing[1]["required_choice"])
        self.assertIn("invariance of domain", self.stored["global_embedding_obstruction"]["proof"])

    def test_mutations_are_rejected(self) -> None:
        self.assertEqual(
            set(self.verifier.mutation_checks(self.stored).values()),
            {"FAIL_DETECTED"},
        )
        false_closure = copy.deepcopy(self.stored)
        false_closure["pre_cancellation_cores"]["r_zx"]["closed_verified"] = False
        with self.assertRaisesRegex(AssertionError, "closure"):
            self.verifier.validate(false_closure)


if __name__ == "__main__":
    unittest.main()
