from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LeanGeometryDataTest(unittest.TestCase):
    def test_generated_index_matches_certificates(self) -> None:
        module = load("generate_t73_lean_geometry")
        generated = module.generate()
        self.assertEqual(
            (ROOT / "Smooth4PC" / "T73CertificateIndex.lean").read_text(
                encoding="utf-8"
            ),
            generated["index"],
        )
        self.assertEqual(
            (ROOT / "Smooth4PC" / "T73JohnsonTransvections.lean").read_text(
                encoding="utf-8"
            ),
            generated["transvections"],
        )
        e12 = json.loads(
            (ROOT / "audit" / "t73_e12_s4_reduction.json").read_text(encoding="utf-8")
        )
        close = json.loads(
            (ROOT / "audit" / "t73_e13_close.json").read_text(encoding="utf-8")
        )
        ident = json.loads(
            (ROOT / "audit" / "t73_e13_identification.json").read_text(encoding="utf-8")
        )
        index = generated["index"]
        self.assertIn(e12["certificate_sha256"], index)
        self.assertIn(close["certificate_sha256"], index)
        self.assertIn(ident["certificate_sha256"], index)
        self.assertIn(close["attaching_link"]["pd_sha256"], index)

    def test_empty_link_inhabitant_is_not_candidate_geometry(self) -> None:
        inhab = (ROOT / "Smooth4PC" / "T73S4Inhabitant.lean").read_text(
            encoding="utf-8"
        )
        pack = (ROOT / "Smooth4PC" / "T73GeometryPack.lean").read_text(encoding="utf-8")
        self.assertIn("def emptyLinkS4Reduction", inhab)
        self.assertIn("EmptyKhQ", inhab)
        self.assertIn("IsHomotopySphere := fun _ => False", inhab)
        self.assertNotIn("instance ExternalGeometry", inhab)
        self.assertNotIn("instance CSTopologyData", pack)
        self.assertIn("def packExternalGeometry", pack)
        self.assertIn("theorem detectorTransport_on_emptyLink_impossible", pack)
        self.assertIn("theorem conditionalCounterexample_of_pack", pack)
        self.assertNotRegex(pack, r"\btheorem\s+notStandard\b")
        self.assertNotRegex(pack, r"\btheorem\s+counterexample\b")


if __name__ == "__main__":
    unittest.main()
