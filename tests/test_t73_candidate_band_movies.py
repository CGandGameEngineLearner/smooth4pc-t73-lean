from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_candidate_band_movies.py"


def load():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("verify_candidate_band_movies", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CandidateBandMovieTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load()
        cls.rectangles = json.loads(cls.verifier.RECTANGLES.read_text(encoding="utf-8"))
        cls.splices = json.loads(cls.verifier.SPLICES.read_text(encoding="utf-8"))

    def test_complete_candidate_movie_records_pass(self):
        self.assertEqual(self.verifier.verify()["verdict"], "PASS_CANDIDATE_MOVIE_RECORDS_ONLY")

    def test_state_chain_mutation_is_rejected(self):
        movie = json.loads(self.verifier.MOVIES["t"].read_text(encoding="utf-8"))
        source = json.loads(self.verifier.SOURCES["t"].read_text(encoding="utf-8"))
        mutant = copy.deepcopy(movie)
        mutant["bands"][1]["current_link_before"] = "wrong_state"
        rectangles = {(item["kind"], item["index"], item["segment_index"]): item for item in self.rectangles["bands"]}
        splices = {(item["kind"], item["index"]): item for item in self.splices["bands"]}
        with self.assertRaisesRegex(AssertionError, "source state chain"):
            self.verifier.verify_movie("t", mutant, source, rectangles, splices)


if __name__ == "__main__":
    unittest.main()
