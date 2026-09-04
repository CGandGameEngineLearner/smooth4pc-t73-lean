from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "build_t73_sigma_minus_typed.py"
    spec = importlib.util.spec_from_file_location("t73_sigma_minus_typed", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SigmaMinusTypedTest(unittest.TestCase):
    def test_actual_parameterized_movies(self) -> None:
        module = load()
        result = module.build()
        self.assertEqual(result["schema"], "t73_sigma_minus_typed/v1")
        self.assertEqual(
            [movie["boundary_word_length"] for movie in result["movies"]],
            [12578, 1824, 409],
        )
        for movie in result["movies"]:
            self.assertEqual(movie["event_counts"]["births"], 0)
            self.assertEqual(
                movie["event_counts"]["saddles"],
                movie["boundary_word_length"] - 1,
            )
            self.assertEqual(
                movie["event_counts"]["caps"], movie["boundary_word_length"]
            )
            permutation = movie["endpoint_permutation"]
            self.assertEqual(
                sorted(permutation["old_to_new"]),
                list(range(movie["boundary_word_length"])),
            )
            self.assertEqual(movie["local_frobenius"]["on_1"], 0)
            self.assertEqual(movie["local_frobenius"]["on_X"], 1)
            self.assertEqual(movie["required_shadow_map"]["status"], "OPEN")
        self.assertEqual(result["S_status"], "OPEN")

    def test_frobenius_formula_matches_small_expansion(self) -> None:
        module = load()
        # Terms are words in {1,X}. Delta(X)=XX and
        # Delta(1)=1X+X1; epsilon kills every word containing 1.
        terms = {"1": [("1",)], "X": [("X",)]}
        for b in range(1, 7):
            if b > 1:
                next_terms = {}
                for basis, words in terms.items():
                    expanded = []
                    for word in words:
                        head, tail = word[0], word[1:]
                        pieces = (
                            [("1", "X"), ("X", "1")]
                            if head == "1"
                            else [("X", "X")]
                        )
                        expanded.extend(piece + tail for piece in pieces)
                    next_terms[basis] = expanded
                terms = next_terms
            for basis in ("1", "X"):
                brute = sum(all(letter == "X" for letter in word) for word in terms[basis])
                self.assertEqual(
                    brute, module.epsilon_iterated_delta(b, basis)
                )

    def test_owner_word_mutation_is_detected(self) -> None:
        module = load()
        source = __import__("json").loads(
            module.SURFACES.read_text(encoding="utf-8")
        )
        mutant = copy.deepcopy(source["surfaces"][0])
        mutant["mapping_torus_boundary_word"][0] *= -1
        with self.assertRaisesRegex(AssertionError, "profile disagrees"):
            module.build_movie(mutant)

    def test_invalid_endpoint_owner_is_rejected(self) -> None:
        module = load()
        with self.assertRaisesRegex(AssertionError, "invalid owner"):
            module.stable_owner_permutation([1, 4, -2])


if __name__ == "__main__":
    unittest.main()
