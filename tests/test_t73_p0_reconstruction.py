from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "reconstruct_t73_p0.py"


def load():
    spec = importlib.util.spec_from_file_location("reconstruct_t73_p0", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class P0ReconstructionTest(unittest.TestCase):
    def test_p0a_handlebody_pair_is_parseable(self) -> None:
        module = load()
        pair = json.loads((ROOT / "audit" / "t73_p0a_handlebody_pair.json").read_text())
        parsed = module.parse_p0a_handlebody_pair(pair)
        self.assertEqual(parsed["heegaard_handlebody_complex"], "PASS")
        self.assertEqual(parsed["s_maps_johnson_pair_onto_ar_pair"], "PASS")
        self.assertEqual(parsed["ar_tetrahedra"], [192, 192])
        self.assertFalse(parsed["uniqueness_of_regular_neighborhoods_used"])
        with self.assertRaises(AssertionError):
            module.verify(pair)

    def test_symbolic_witness_is_rejected(self) -> None:
        module = load()
        candidate = json.loads((ROOT / "audit" / "t73_ar_product_witness.json").read_text())
        with self.assertRaises(AssertionError):
            module.verify(candidate)

    def test_schema_requires_geometric_payload(self) -> None:
        schema = json.loads((ROOT / "audit" / "t73_p0_reconstruction_schema.json").read_text())
        self.assertIn("ambient_ball", schema["required_top_level_fields"])
        self.assertIn("ar_passage_binding", schema["required_geometric_payload"]["detector_collar"])
        self.assertIn("normal_vectors", schema["required_geometric_payload"]["strand"])

    def test_public_target_has_252_physical_factors(self) -> None:
        module = load()
        target = module.expected_public_word()
        self.assertEqual(len(target), 11340)
        self.assertEqual(len(module.json.loads(module.PUBLIC_INPUT.read_text())["point_push"]["crossing_rows"]), 252)

    def test_pure_factor_expansion_is_252_to_11340(self) -> None:
        module = load()
        data = module.json.loads(module.PUBLIC_INPUT.read_text())
        rows = {row[0]: row for row in data["point_push"]["crossing_rows"]}
        word = []
        for index in data["point_push"]["oriented_source_indices"]:
            row = rows[index]
            word.extend(module.pure_factor(row[8], row[9], row[3], row[11]))
        self.assertEqual(len(word), 11340)

    def test_geometry_derivation_finds_an_exact_adjacent_crossing(self) -> None:
        module = load()
        strands = []
        for strand_id in range(1, 45):
            x0, x1 = strand_id, strand_id
            if strand_id == 1:
                x1 = 2
            elif strand_id == 2:
                x1 = 1
            strands.append({
                "id": strand_id,
                "vertices": [[x0, strand_id, 0], [x1, strand_id, 1]],
                "normal_vectors": [[0, 1, 0], [0, 1, 0]],
            })
        collar = {
            "strands": strands,
            "pairwise_disjointness_certificate": {"status": "PASS"},
            "normal_field_certificate": {"status": "PASS"},
        }
        events = module.derive_elementary_events(collar)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["moving_strand"], 1)
        self.assertEqual(events[0]["other_strand"], 2)
        self.assertEqual(events[0]["artin_letter"], 1)

    def test_public_word_control_is_recovered_from_pl_strands(self) -> None:
        module = load()
        generator_path = ROOT / "scripts" / "generate_t73_target_braid_control.py"
        spec = importlib.util.spec_from_file_location("target_control", generator_path)
        assert spec and spec.loader
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        collar = generator.control_collar(module)
        events = module.derive_elementary_events(collar)
        self.assertEqual(len(events), 11340)
        self.assertEqual(
            [event["artin_letter"] for event in events],
            module.expected_public_word(),
        )


if __name__ == "__main__":
    unittest.main()
