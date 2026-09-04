from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "geometry" / "t73_c_defect_coend_typing_graph.json"


def load(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def one_dimensional_complex(q_degree: int = 0):
    return {
        "basis_by_degree": [
            {
                "degree": 0,
                "basis": [{"id": "v", "quantum_degree": q_degree}],
            }
        ],
        "differentials": [],
    }


def linear_map(value, q_degree=0, homological_degree=0):
    return {
        "homological_degree": homological_degree,
        "quantum_degree": q_degree,
        "components": [{"from_degree": 0, "matrix": [[value]]}],
    }


def zero_homotopy(q_degree=0):
    return {
        "homological_degree": -1,
        "quantum_degree": q_degree,
        "components": [],
    }


def toy_chain_certificate():
    return {
        "fibers": [
            {
                "fiber_id": "fiber:T:T_prime",
                "source_complex": one_dimensional_complex(),
                "target_complex": one_dimensional_complex(),
                "theta": linear_map(1),
                "theta_inverse": linear_map(1),
                "source_homotopy": zero_homotopy(),
                "target_homotopy": zero_homotopy(),
            }
        ],
        "residual_naturality": [
            {
                "name": "left_generator",
                "side": "C44_left",
                "from_fiber": "fiber:T:T_prime",
                "to_fiber": "fiber:T:T_prime",
                "source_action": linear_map(1),
                "target_action": linear_map(1),
                "homotopy": zero_homotopy(),
            },
            {
                "name": "right_generator",
                "side": "C44_right",
                "from_fiber": "fiber:T:T_prime",
                "to_fiber": "fiber:T:T_prime",
                "source_action": linear_map(1),
                "target_action": linear_map(1),
                "homotopy": zero_homotopy(),
            },
        ],
    }


def toy_presentation():
    return {
        "fibers": [
            {
                "fiber_id": "fiber:T:T_prime",
                "T_object": "T",
                "T_prime_object": "T_prime",
            }
        ],
        "residual_action_generators": [
            {
                "name": "left_generator",
                "side": "C44_left",
                "from_fiber": "fiber:T:T_prime",
                "to_fiber": "fiber:T:T_prime",
            },
            {
                "name": "right_generator",
                "side": "C44_right",
                "from_fiber": "fiber:T:T_prime",
                "to_fiber": "fiber:T:T_prime",
            },
        ],
    }


class DefectCoendTypingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load(
            "scripts/build_t73_c_defect_coend_typing_graph.py", "defect_graph_builder"
        )
        cls.verifier = load(
            "scripts/verify_t73_c_defect_coend_witness.py", "defect_coend_verifier"
        )
        cls.graph = json.loads(GRAPH.read_text(encoding="utf-8"))

    def test_committed_graph_is_exact_rebuild(self):
        self.assertEqual(self.graph, self.builder.build())
        self.verifier.validate_graph(self.graph)

    def test_complete_incidence_and_product_category_type(self):
        self.assertEqual(self.graph["counts"]["endpoints"], 1260)
        self.assertEqual(self.graph["counts"]["intervals"], 630)
        self.assertEqual(self.graph["counts"]["Y_port_endpoints"], 176)
        self.assertEqual(self.graph["counts"]["wrong_side_intervals"], 8)
        self.assertEqual(
            self.graph["coefficient_profunctor"]["domain"],
            "C_44^op x C_271^op x C_44 x C_271",
        )

    def test_oriented_obligations_cover_wrong_edges_once(self):
        nodes = {item["endpoint_id"]: item for item in self.graph["endpoint_nodes"]}
        obligations = self.graph["oriented_reconnection_obligations"]
        old = [edge for item in obligations for edge in item["old_interval_ids"]]
        wrong = [
            item["interval_id"]
            for item in self.graph["interval_edges"]
            if item["typing_status"] == "wrong_same_side_active"
        ]
        self.assertEqual(sorted(old), sorted(wrong))
        self.assertEqual(len(obligations), 4)
        for item in obligations:
            self.assertTrue(item["not_a_pivotal_mate"])
            self.assertEqual(item["status"], "UNREALIZED")
            for initial, terminal in item["new_oriented_arcs"]:
                self.assertEqual(nodes[initial]["exterior_incidence"], "exit")
                self.assertEqual(nodes[terminal]["exterior_incidence"], "entry")

    def test_legacy_lexicographic_pairing_has_two_orientation_failures(self):
        diagnostic = self.graph["legacy_lexicographic_pairing_diagnostic"]
        bad = [
            item["legacy_index"]
            for item in diagnostic
            if not item["all_arcs_have_one_exit_one_entry"]
        ]
        self.assertEqual(bad, self.graph["legacy_orientation_incompatible_indices"])
        for item in diagnostic:
            expected = all(
                sorted(pair) == ["entry", "exit"] for pair in item["role_pairs"]
            )
            self.assertEqual(item["all_arcs_have_one_exit_one_entry"], expected)

    def test_pivotal_retyping_does_not_fake_174(self):
        contract = self.graph["pivotal_retyping_contract"]
        accounting = self.graph["single_hom_boundary_accounting"]
        self.assertEqual(contract["effect_on_physical_endpoint_count"], 0)
        self.assertEqual(contract["effect_on_interval_matching"], "identity")
        self.assertEqual(accounting["active_endpoints_after_pivotal_retyping"], 176)
        self.assertEqual(accounting["P86_to_P88_endpoints"], 174)
        self.assertTrue(accounting["external_cup_is_separate_from_wrong_side_repair"])

    def test_current_gate_is_open_not_pass_by_metadata(self):
        result = self.verifier.inspect_current()
        self.assertEqual(result["verdict"], "OPEN")
        self.assertIn("no geometry/t73_c_defect_coend_witness.json", result["reason"])
        fake = {
            "schema": "t73_c_defect_coend_witness/v1",
            "typing_graph_sha256": self.graph["sha256"],
            "route": "direct_derived_bar_comparison",
            "status": "PASS",
        }
        with self.assertRaisesRegex(ValueError, "missing fields"):
            self.verifier.verify_witness(fake, self.graph)

    def test_toy_chain_equivalence_checks_actual_matrices(self):
        checked = self.verifier.validate_chain_certificate(
            toy_chain_certificate(), toy_presentation()
        )
        self.assertEqual(checked["theta_quantum_degree"], 0)
        mutant = toy_chain_certificate()
        mutant["fibers"][0]["theta_inverse"]["components"][0]["matrix"] = [[0]]
        with self.assertRaisesRegex(ValueError, "not homotopic to identity"):
            self.verifier.validate_chain_certificate(mutant)

    def test_missing_one_residual_action_is_rejected(self):
        mutant = toy_chain_certificate()
        mutant["residual_naturality"].pop()
        with self.assertRaisesRegex(ValueError, "does not exhaust"):
            self.verifier.validate_chain_certificate(mutant, toy_presentation())

    def test_graph_endpoint_mutation_is_rejected(self):
        mutant = copy.deepcopy(self.graph)
        mutant["endpoint_nodes"].pop()
        with self.assertRaisesRegex(ValueError, "stale"):
            self.verifier.validate_graph(mutant)

    def test_schema_requires_nonliteral_route_and_formal_receipt(self):
        schema = json.loads(
            (ROOT / "data" / "T73_C_DEFECT_COEND_WITNESS.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["properties"]["literal_split_used"]["const"], False)
        self.assertIn("formal_receipt", schema["required"])
        self.assertEqual(
            schema["properties"]["boundary_accounting"]["properties"]
            ["active_y_endpoints_after_pivotal_retyping"]["const"],
            176,
        )


if __name__ == "__main__":
    unittest.main()
