from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_t73_claim_boundary.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_t73_claim_boundary", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClaimBoundaryTest(unittest.TestCase):
    def test_current_paper_retains_open_candidate_joins(self) -> None:
        load_checker().check()

    def test_unconditional_claim_is_rejected(self) -> None:
        checker = load_checker()
        source = Path("mutant.tex")
        with self.assertRaises(AssertionError):
            checker.reject(
                "gives a counterexample to the smooth",
                "gives a counterexample to the smooth",
                source,
            )


if __name__ == "__main__":
    unittest.main()
