from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_t73_ar_product_witness.py"
WITNESS = ROOT / "audit" / "t73_ar_product_witness.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_t73_ar_product_witness", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ARProductWitnessTest(unittest.TestCase):
    def test_committed_witness_regenerates(self) -> None:
        generator = load_generator()
        generator.verify_committed(WITNESS)

    def test_matrix_bridge_is_unimodular_and_exact(self) -> None:
        generator = load_generator()
        bridge = generator.matrix_bridge()
        self.assertEqual(bridge["det_R"], 1)
        self.assertEqual(bridge["identity"], "C_AR * R = R * A")

    def test_local_knotting_mutant_is_not_the_witness(self) -> None:
        generator = load_generator()
        mutant = generator.generate_witness()
        mutant["actual_framed_link"]["component_parametrizations"]["m_i"][
            "local_knot"
        ] = "trefoil"
        self.assertNotEqual(mutant, json.loads(WITNESS.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
