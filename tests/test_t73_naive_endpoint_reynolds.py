from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class NaiveEndpointReynoldsTests(unittest.TestCase):
    def test_naive_full_endpoint_average_is_a_zero_negative_control(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "check_t73_naive_endpoint_reynolds.py"
        spec = importlib.util.spec_from_file_location("negative_control", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import endpoint Reynolds control")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.check()
        self.assertEqual(result["verdict"], "ZERO_AS_EXPECTED")
        self.assertEqual(result["h_coefficients_0_to_6"], [0] * 7)


if __name__ == "__main__":
    unittest.main()
