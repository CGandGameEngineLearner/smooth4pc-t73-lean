from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_selected_source_gmsh_probe.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("gmsh_probe_verifier", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SelectedSourceGmshProbeTest(unittest.TestCase):
    def test_saved_prefix20_receipt_is_hash_bound_and_open(self):
        verifier = load_verifier()
        receipt = json.loads(verifier.RECEIPT.read_text(encoding="utf-8"))
        result = verifier.verify(receipt)
        self.assertEqual(result["verdict"], "PASS_RECEIPT_ONLY")
        self.assertEqual(result["route_prefix"], 20)
        self.assertEqual(result["full_630_frame"], "OPEN")

    def test_count_and_scope_mutations_fail(self):
        verifier = load_verifier()
        receipt = json.loads(verifier.RECEIPT.read_text(encoding="utf-8"))
        for mutate in (
            lambda item: item.__setitem__("tetrahedra", 1),
            lambda item: item.__setitem__("status", "PASS_COMPLETE"),
        ):
            mutant = copy.deepcopy(receipt)
            mutate(mutant)
            mutant["sha256"] = verifier.canonical_sha(
                {key: value for key, value in mutant.items() if key != "sha256"}
            )
            with self.assertRaises(AssertionError):
                verifier.verify(mutant)


if __name__ == "__main__":
    unittest.main()
