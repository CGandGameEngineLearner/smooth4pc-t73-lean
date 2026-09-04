import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_t73_c_pivotal_grading_input.py"
INPUT = ROOT / "data" / "T73_C_PIVOTAL_GRADING_INPUT.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("standard_pivotal_input", BUILDER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StandardPivotalInputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.payload = cls.builder.build(write=False)
        cls.checker = cls.builder.load_checker()

    def test_committed_input_rebuilds(self):
        self.assertEqual(json.loads(INPUT.read_text(encoding="utf-8")), self.payload)

    def test_mixed_variance_is_derived(self):
        charts = self.payload["endpoint_duality_charts"]
        self.assertEqual(sum(item["variance"] == "V" for item in charts), 44)
        self.assertEqual(sum(item["variance"] == "V_dual" for item in charts), 44)
        for item in charts:
            orientation = item["base_passage_orientation"] * item["copy_orientation_multiplier"]
            self.assertEqual(item["orientation"], orientation)
            self.assertEqual(item["variance"], "V" if orientation == 1 else "V_dual")

    def test_nonconstant_q_powers_and_cubic(self):
        report = self.checker.generate()
        coefficients = report["standard_convention"]["endpoint_coefficients"]
        self.assertEqual(sum(item["q_power"] == 0 for item in coefficients), 44)
        self.assertEqual(sum(item["q_power"] == 1 for item in coefficients), 44)
        self.assertTrue(all(item["sign"] == 1 for item in coefficients))
        self.assertEqual(
            report["standard_convention"]["derived_public_cup"],
            [
                {"public_position": 2, "q_power": -1, "sign": 1},
                {"public_position": 87, "q_power": 1, "sign": 1},
            ],
        )
        self.assertEqual(
            report["standard_convention"]["derived_public_cap"],
            [
                {"public_position": 2, "q_power": 0, "sign": 1},
                {"public_position": 87, "q_power": 0, "sign": 1},
            ],
        )
        self.assertEqual(report["standard_convention"]["derived_h3"], 2624)

    def test_absolute_degree_stays_open(self):
        report = self.checker.generate()
        self.assertEqual(report["status"], "PIVOTAL_CERTIFIED_DEGREE_OPEN")
        self.assertFalse(report["degree_494_certified"])
        self.assertEqual(
            set(report["missing"]),
            {
                "grading_diagrams[cabled_state_s0]",
                "grading_diagrams[hattori_target_closure]",
                "grading_diagrams[mww_selected_coefficient_closure]",
                "grading_diagrams[mww_to_bhpw_selected_comparison]",
            },
        )


if __name__ == "__main__":
    unittest.main()
