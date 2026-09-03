from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless((Path("/usr/bin/gap")).is_file(), "GAP is not installed")
class IARepresentativeTest(unittest.TestCase):
    def test_inner_correction_restores_44_channels_but_not_exact_word(self) -> None:
        path = ROOT / "scripts" / "search_t73_ia_representative.py"
        spec = importlib.util.spec_from_file_location("search_ia", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate(max_length=1)
        self.assertTrue(result["gap_is_bijective"])
        self.assertEqual(result["m2_length"], 311)
        self.assertEqual(result["total_y_channels"], 44)
        self.assertFalse(result["exact_compact_m2_match"])

    def test_ia_word_has_exact_movie_to_compact_word(self) -> None:
        path = ROOT / "scripts" / "construct_t73_ia_to_compact_movie.py"
        spec = importlib.util.spec_from_file_location("ia_movie", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertEqual(result["source_length"], 311)
        self.assertEqual(result["target_length"], 311)
        self.assertEqual(result["word_movie_status"], "PASS")

    def test_ia_movie_has_local_band_schedule_and_net_minus_40(self) -> None:
        schedule_path = ROOT / "scripts" / "generate_t73_ia_band_schedule.py"
        spec = importlib.util.spec_from_file_location("ia_bands", schedule_path)
        assert spec and spec.loader
        bands = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bands)
        self.assertEqual(bands.generate()["schedule_length"], 11756)
        framing_path = ROOT / "scripts" / "audit_t73_ia_framing.py"
        spec2 = importlib.util.spec_from_file_location("ia_framing", framing_path)
        assert spec2 and spec2.loader
        framing = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(framing)
        self.assertEqual(framing.generate()["net_oriented_r_yz_slide_coefficient"], -40)
        self.assertEqual(framing.generate(0)["framing_status"], "PASS")

    def test_inner_correction_is_only_a_based_representative(self) -> None:
        path = ROOT / "scripts" / "audit_t73_inner_conjugation_geometry.py"
        spec = importlib.util.spec_from_file_location("inner_geometry", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertTrue(result["outer_automorphism_unchanged"])
        self.assertFalse(result["channel_count_invariant_under_basepoint_change"])
        self.assertEqual(result["geometric_verdict"], "BASEPOINT_CHANGE_ONLY_NOT_AN_EMBEDDED_44_CHANNEL_WITNESS")


if __name__ == "__main__":
    unittest.main()
