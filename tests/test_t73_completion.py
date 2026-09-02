from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_t73_completion.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_t73_completion", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompletionGateTest(unittest.TestCase):
    def test_current_repository_passes(self) -> None:
        load_checker().check()

    def test_partial_status_mutant_is_rejected(self) -> None:
        checker = load_checker()
        with self.assertRaises(AssertionError):
            checker.reject("P1/C & \\Partial", "& \\Partial", Path("mutant.tex"))


if __name__ == "__main__":
    unittest.main()
