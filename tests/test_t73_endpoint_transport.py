from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EndpointTransportTest(unittest.TestCase):
    def test_convention_records_all_eighty_eight_endpoints(self) -> None:
        builder = load("build_t73_endpoint_transport")
        convention = builder.build_convention()
        self.assertEqual(convention["dimension"], 88)
        self.assertEqual(len(convention["endpoints"]), 88)
        self.assertTrue(convention["no_unresolved_signs"])
        required = {
            "physical_endpoint_id",
            "owner",
            "orientation",
            "geometric_order",
            "public_order",
            "pivotal_coefficient",
            "weight_defect_basis_vector",
        }
        for endpoint in convention["endpoints"]:
            self.assertTrue(required.issubset(endpoint))
            self.assertIn(endpoint["pivotal_coefficient"]["sign"], (-1, 1))

    def test_public_pairing_is_derived_not_hardcoded_as_input(self) -> None:
        builder = load("build_t73_endpoint_transport")
        source = (ROOT / "scripts" / "build_t73_endpoint_transport.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("u_public = e2 - e87", source)
        pairing = builder.public_pairing_terms()
        self.assertEqual({tuple(term) for term in pairing["u_terms"]}, {(2, 1), (87, -1)})
        self.assertEqual({tuple(term) for term in pairing["ell_terms"]}, {(87, 1), (2, -1)})
        self.assertIn("P(q)", pairing["source"])

    def test_recompute_does_not_read_handwritten_u_ell_terms(self) -> None:
        source = (ROOT / "scripts" / "recompute_t73_delta3.py").read_text(encoding="utf-8")
        self.assertNotIn('data["endpoint_model"]["u_terms"]', source)
        self.assertNotIn('data["endpoint_model"]["ell_terms"]', source)
        self.assertIn("public_pairing_terms", source)

    def test_mutations_fail(self) -> None:
        verifier = load("verify_t73_endpoint_transport")
        result = verifier.verify(write=False)
        self.assertEqual(result["ENDPOINT_TRANSPORT"], "PASS")
        self.assertEqual(result["NO_UNRESOLVED_SIGNS"], "PASS")
        for name, status in result["failing_mutation_tests"].items():
            self.assertTrue(status.startswith("FAIL"), msg=f"{name}: {status}")


if __name__ == "__main__":
    unittest.main()
