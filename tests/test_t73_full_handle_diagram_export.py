from __future__ import annotations

from collections import Counter
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "geometry" / "examples" / "seven_component_framed_unlink_input.json"
OUTPUT = ROOT / "geometry" / "examples" / "seven_component_framed_unlink_export.json"
ENGINE_RECEIPT = ROOT / "geometry" / "examples" / "seven_component_framed_unlink_open_source_receipt.json"


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FullHandleDiagramExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.exporter = load_script("export_t73_full_handle_diagram")
        cls.builder = load_script("build_t73_full_handle_diagram_example")
        cls.data = json.loads(INPUT.read_text(encoding="utf-8"))
        cls.exported = cls.exporter.export(cls.data)

    def test_committed_fixture_and_export_are_reproducible(self) -> None:
        self.assertEqual(self.data, self.builder.build())
        self.assertEqual(
            self.exported,
            json.loads(OUTPUT.read_text(encoding="utf-8")),
        )

    def test_complete_pd_and_halfedge_cycles(self) -> None:
        self.assertEqual(self.exported["crossing_count"], 7)
        self.assertEqual(self.exported["crossingless_components"], [])
        self.assertEqual(
            list(self.exported["component_halfedge_cycles"]),
            self.exporter.REQUIRED_NAMES,
        )
        self.assertTrue(
            all(len(cycle) == 2 for cycle in self.exported["component_halfedge_cycles"].values())
        )
        counts = Counter(
            label for row in self.exported["standard_pd_code"] for label in row
        )
        self.assertEqual(set(counts.values()), {2})
        self.assertEqual(
            self.exported["standard_pd_code"],
            [[2 * i, 2 * i + 1, 2 * i + 1, 2 * i] for i in range(7)],
        )

    def test_exact_crossings_and_framing_matrices(self) -> None:
        self.assertEqual(
            [crossing["sign"] for crossing in self.exported["crossings"]],
            [-1] * 7,
        )
        self.assertTrue(
            all(crossing["over_parameter"] == "1/2" for crossing in self.exported["crossings"])
        )
        self.assertEqual(
            self.exported["integer_surgery_framings"],
            {name: 1 for name in self.exporter.TWO_HANDLE_NAMES},
        )
        self.assertEqual(
            self.exported["two_handle_surgery_matrix"]["matrix"],
            [[int(i == j) for j in range(5)] for i in range(5)],
        )
        framed = self.exported["framed_link"]
        self.assertEqual(len(framed["component_order"]), 12)
        self.assertEqual(framed["crossing_count"], 42)
        self.assertEqual(framed["crossingless_components"], [])
        for index, name in enumerate(self.exporter.TWO_HANDLE_NAMES):
            push_index = framed["component_order"].index(f"{name}__push_off")
            self.assertEqual(framed["pairwise_linking_matrix"][index][push_index], 1)

    def test_missing_component_and_push_off_fail_closed(self) -> None:
        missing_component = copy.deepcopy(self.data)
        missing_component["components"].pop()
        with self.assertRaisesRegex(self.exporter.DiagramError, "component order/names"):
            self.exporter.export(missing_component)
        missing_push = copy.deepcopy(self.data)
        del missing_push["components"][0]["closed_push_off_polyline"]
        with self.assertRaisesRegex(self.exporter.DiagramError, "push_off"):
            self.exporter.export(missing_push)

    def test_wrong_successor_and_actual_intersection_fail_closed(self) -> None:
        wrong_successor = copy.deepcopy(self.data)
        wrong_successor["components"][0]["cyclic_segment_successor"] = [0, 1, 2, 3]
        with self.assertRaisesRegex(self.exporter.DiagramError, "explicit oriented cyclic order"):
            self.exporter.export(wrong_successor)
        intersection = copy.deepcopy(self.data)
        # Equalize the two heights at the bow-tie crossing of m_2.
        intersection["components"][0]["closed_core_polyline"][1][2] = "-2"
        with self.assertRaisesRegex(self.exporter.DiagramError, r"meet in Q\^3"):
            self.exporter.export(intersection)

    def test_collapsed_projection_and_reversed_orientation_fail_closed(self) -> None:
        collapsed = copy.deepcopy(self.data)
        first = collapsed["components"][0]["closed_core_polyline"][0]
        collapsed["components"][0]["closed_core_polyline"][1] = [
            first[0],
            first[1],
            "2",
        ]
        with self.assertRaisesRegex(self.exporter.DiagramError, "collapses under projection"):
            self.exporter.export(collapsed)
        reversed_orientation = copy.deepcopy(self.data)
        reversed_orientation["ambient"]["projection_basis"].reverse()
        with self.assertRaisesRegex(self.exporter.DiagramError, "reverses standard_xyz"):
            self.exporter.export(reversed_orientation)

    def test_open_source_receipt_is_bound_to_export(self) -> None:
        receipt = json.loads(ENGINE_RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["export_sha256"], self.exported["sha256"])
        self.assertEqual(receipt["spherogram_components"], 7)
        self.assertEqual(receipt["snappy_cusps"], 7)
        self.assertEqual(receipt["snappy_tetrahedra"], receipt["regina_tetrahedra"])
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["spherogram_framed_link"]["verdict"], "PASS")
        self.assertEqual(receipt["spherogram_framed_link"]["components"], 12)
        self.assertEqual(receipt["spherogram_framed_link"]["crossings"], 42)
        self.assertTrue(receipt["regina_valid"])
        self.assertTrue(receipt["regina_orientable"])
        self.assertTrue(receipt["regina_connected"])
        self.assertTrue(receipt["regina_ideal"])
        self.assertEqual(receipt["regina_boundary_components"], 7)
        self.assertEqual(
            receipt["sha256"],
            self.exporter.canonical_sha(
                {key: value for key, value in receipt.items() if key != "sha256"}
            ),
        )

    def test_exact_polygonal_hopf_link_has_nonzero_linking(self) -> None:
        f = Fraction
        first = {
            "name": "a",
            "points": [
                (f(3), f(0), f(0)),
                (f(0), f(3), f(0)),
                (f(-3), f(0), f(0)),
                (f(0), f(-3), f(0)),
                (f(3), f(0), f(0)),
            ],
        }
        second = {
            "name": "b",
            "points": [
                (f(4), f(0), f(0)),
                (f(2), f(0), f(2)),
                (f(0), f(0), f(0)),
                (f(2), f(0), f(-2)),
                (f(4), f(0), f(0)),
            ],
        }
        basis = [(f(2), f(-1), f(0)), (f(3), f(0), f(-1))]
        height = (f(1), f(2), f(3))
        linking, crossings = self.exporter.linking_number_between(
            first, second, basis, height
        )
        self.assertEqual(linking, -1)
        self.assertEqual([crossing["sign"] for crossing in crossings], [-1, -1])
        pd, cycles, crossingless = self.exporter.pd_and_cycles(
            ["a", "b"], crossings
        )
        self.assertEqual(crossingless, [])
        self.assertEqual([len(cycles[name]) for name in ("a", "b")], [2, 2])
        self.assertEqual(set(Counter(label for row in pd for label in row).values()), {2})


class FullHandleInputGapTest(unittest.TestCase):
    def test_current_gap_is_located_before_band_splicing(self) -> None:
        module = load_script("check_t73_full_handle_diagram_input_gap")
        result = module.inspect()
        self.assertEqual(result["exporter_readiness"], "OPEN")
        self.assertEqual(result["complete_exporter_input_validation"]["status"], "OPEN")
        first = result["first_missing_coordinate_map"]
        self.assertEqual(first["name"], "kappa_AR_to_common_Kirby_presentation")
        self.assertIn("not an ambient embedding", first["map_type"])
        stage_zero = result["ordered_downstream_blockers"][0]
        self.assertEqual(stage_zero["stage"], 0)
        self.assertEqual(
            stage_zero["evidence"]["mapping_torus_point_arities"]["m_2"],
            [4],
        )
        self.assertEqual(
            stage_zero["evidence"]["dual_cell_point_arities"]["r_xy"],
            [3],
        )


if __name__ == "__main__":
    unittest.main()
