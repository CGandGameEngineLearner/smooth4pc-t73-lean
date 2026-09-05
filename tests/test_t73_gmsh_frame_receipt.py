from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_gmsh_frame_verification_receipt.py"
PREFIX20 = ROOT / "geometry/examples/t73_selected_source_gmsh_prefix20_frame.json"
RECEIPT20 = ROOT / "audit/t73_selected_source_gmsh_prefix20_frame_verification.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("gmsh_frame_receipt", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GmshFrameReceiptTest(unittest.TestCase):
    def test_committed_receipt_binds_verified_frame(self):
        builder = load_builder()
        receipt = json.loads(builder.OUTPUT.read_text(encoding="utf-8"))
        builder.check_files(receipt)
        self.assertEqual(receipt["status"], "PASS_PREFIX_ONLY")
        self.assertEqual(receipt["result"]["ribbons"], 10)
        self.assertEqual(receipt["result"]["exact_exterior_volume"], "63968")

    def test_committed_prefix20_receipt_binds_verified_frame(self):
        builder = load_builder()
        expected = builder.expected_counts(
            prefix=20,
            vertices=4134,
            tetrahedra=23725,
            arcs=20,
            ribbons=20,
            boundary_components=5,
            exact_exterior_volume="63968",
        )
        receipt = json.loads(RECEIPT20.read_text(encoding="utf-8"))
        builder.check_files(receipt, PREFIX20, expected)
        self.assertEqual(receipt["status"], "PASS_PREFIX_ONLY")
        self.assertEqual(receipt["result"]["vertices"], 4134)
        self.assertEqual(receipt["result"]["tetrahedra"], 23725)
        self.assertEqual(receipt["result"]["ribbons"], 20)

    def test_rehashed_status_promotion_is_rejected(self):
        builder = load_builder()
        receipt = json.loads(builder.OUTPUT.read_text(encoding="utf-8"))
        mutant = copy.deepcopy(receipt)
        mutant["result"]["verdict"] = "PASS_COMPLETE"
        mutant["sha256"] = builder.canonical_sha(
            {key: value for key, value in mutant.items() if key != "sha256"}
        )
        with self.assertRaises(AssertionError):
            builder.check_files(mutant)

    def test_rehashed_verifier_path_mutation_is_rejected(self):
        builder = load_builder()
        receipt = json.loads(builder.OUTPUT.read_text(encoding="utf-8"))
        mutant = copy.deepcopy(receipt)
        mutant["verifier"] = "scripts/not_the_independent_verifier.py"
        mutant["sha256"] = builder.canonical_sha(
            {key: value for key, value in mutant.items() if key != "sha256"}
        )
        with self.assertRaisesRegex(AssertionError, "verifier path"):
            builder.check_files(mutant)


if __name__ == "__main__":
    unittest.main()
