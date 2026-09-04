import copy
import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_t73_all_owner_product_primitives.py"
ARTIFACT = ROOT / "geometry" / "t73_all_owner_product_primitives.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("all_owner_product", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AllOwnerProductPrimitiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.payload = cls.builder.build(write=False)

    def test_committed_artifact_rebuilds_exactly(self):
        committed = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(committed, self.payload)

    def test_counts_and_m3_reduction(self):
        self.assertEqual(self.payload["counts"]["n_y"], [42, 189, 2, 2, 0])
        self.assertEqual(self.payload["counts"]["n_z"], [269, 1271, 2, 2, 0])
        self.assertEqual(self.payload["counts"]["rectangles_per_balanced_cable_pair"], 235)
        self.assertEqual(self.payload["counts"]["leftover_circles_per_balanced_cable_pair"], 1309)
        reductions = self.payload["primitive_geometry"]["m_3"]["free_reduction_pairs"]
        self.assertEqual(len(reductions), 1)
        self.assertEqual(
            {reductions[0]["left_source_id"], reductions[0]["right_source_id"]},
            {"c2:letter:1460", "m_3:C_i"},
        )
        self.assertEqual(
            len(self.payload["primitive_geometry"]["r_zx"]["free_reduction_pairs"]), 2
        )
        self.assertEqual(self.payload["primitive_geometry"]["r_zx"]["reduced_events"], [])

    def test_dual_component_orientation_is_consistent(self):
        rxy = self.payload["primitive_geometry"]["r_xy"]
        self.assertEqual(rxy["reduced_word"], ["z", "y", "Z", "Y"])
        x_events = [
            event
            for event in rxy["reduced_events"]
            if event["source_geometry"]["kind"] == "dual_x_slide_z_replacement"
        ]
        self.assertEqual(
            [(event["source_id"], event["orientation"]) for event in x_events],
            [("r_xy:vertex:7", 1), ("r_xy:vertex:3", -1)],
        )
        for event in x_events:
            geometry = event["source_geometry"]
            self.assertEqual(
                geometry["replacement_orientation"],
                -geometry["stored_slide_forward_orientation"],
            )
            self.assertEqual(geometry["component_traversal_orientation_factor"], -1)

    def test_every_z_source_is_partitioned(self):
        for owner in self.payload["owners"]:
            record = self.payload["primitive_geometry"][owner]
            z_sources = {
                event["source_id"] for event in record["reduced_events"] if event["label"] == "z"
            }
            paired = {item["z_source_id"] for item in record["product_rectangles"]}
            leftover = {item["z_source_id"] for item in record["leftover_z_circles"]}
            self.assertFalse(paired & leftover)
            self.assertEqual(paired | leftover, z_sources)

    def test_arbitrary_parallel_formula_is_conditional(self):
        theorem = self.payload["parallel_copy_theorem"]
        self.assertEqual(theorem["rectangle_count_formula"], "sum_i r_i*n_y_i")
        self.assertEqual(
            theorem["leftover_circle_count_formula"], "sum_i r_i*(n_z_i-n_y_i)"
        )
        self.assertFalse(self.payload["ambient_scope"]["actual_partial_W2_claimed"])

    def test_hostile_mutations_fail(self):
        self.assertTrue(all(self.builder.mutation_results(self.payload).values()))
        mutant = copy.deepcopy(self.payload)
        mutant["parallel_copy_theorem"]["rectangle_count_formula"] = "sum_i n_y_i"
        with self.assertRaises(AssertionError):
            self.builder.verify_payload(mutant)


if __name__ == "__main__":
    unittest.main()
