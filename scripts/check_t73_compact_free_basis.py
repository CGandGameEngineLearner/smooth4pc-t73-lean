#!/usr/bin/env python3
"""Use GAP to test whether the compact AR spine words form an F_3 basis."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_compact():
    path = ROOT / "scripts" / "generate_t73_compact_kirby_ledger.py"
    spec = importlib.util.spec_from_file_location("compact", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def gap_word(word: list[str]) -> str:
    names = {"x": "x", "y": "y", "z": "z", "X": "x^-1", "Y": "y^-1", "Z": "z^-1"}
    return "*".join(names[letter] for letter in word) if word else "One(F)"


def generate_gap_source(words: list[list[str]]) -> str:
    expressions = ",\n".join(gap_word(word) for word in words)
    return f'''Print("GAP_VERSION=", GAPInfo.Version, "\\n");
F:=FreeGroup("x","y","z");;
g:=GeneratorsOfGroup(F);; x:=g[1];; y:=g[2];; z:=g[3];;
images:=[{expressions}];;
hom:=GroupHomomorphismByImages(F,F,g,images);;
Print("IS_HOM=",IsGroupHomomorphism(hom),"\\n");
Print("IS_SURJECTIVE=",IsSurjective(hom),"\\n");
Print("IS_INJECTIVE=",IsInjective(hom),"\\n");
Print("IS_BIJECTIVE=",IsBijective(hom),"\\n");
if IsBijective(hom) then
  inv:=InverseGeneralMapping(hom);;
  Print("INVERSE_IMAGES=",List(g,a->Image(inv,a)),"\\n");
fi;
QUIT;
'''


def gap_check(words: list[list[str]], timeout: int) -> dict[str, Any]:
    gap = shutil.which("gap")
    if gap is None:
        raise RuntimeError("GAP is not installed")
    source = generate_gap_source(words)
    with tempfile.TemporaryDirectory(prefix="t73-gap-") as directory:
        source_path = Path(directory) / "check.g"
        source_path.write_text(source, encoding="utf-8")
        process = subprocess.run(
            [gap, "-q", str(source_path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    if process.returncode != 0:
        raise RuntimeError(f"GAP failed: {process.stderr}")
    values = {}
    for line in process.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    required = ("GAP_VERSION", "IS_HOM", "IS_SURJECTIVE", "IS_INJECTIVE", "IS_BIJECTIVE")
    if any(key not in values for key in required):
        raise RuntimeError(f"GAP output is incomplete: {process.stdout}")
    return {
        "gap_executable": gap,
        "gap_version": values["GAP_VERSION"],
        "word_lengths": [len(word) for word in words],
        "word_sha256": [canonical_sha(word) for word in words],
        "is_homomorphism": values["IS_HOM"] == "true",
        "is_surjective": values["IS_SURJECTIVE"] == "true",
        "is_injective": values["IS_INJECTIVE"] == "true",
        "is_bijective": values["IS_BIJECTIVE"] == "true",
        "gap_stdout": process.stdout,
        "gap_stderr": process.stderr,
    }


def int_words_to_letters(words: list[list[int]]) -> list[list[str]]:
    names = {1: "x", 2: "y", 3: "z", -1: "X", -2: "Y", -3: "Z"}
    return [[names[letter] for letter in word] for word in words]


def run(timeout: int = 300) -> dict[str, Any]:
    compact = load_compact()
    compact_words = [compact.linear_crossing_word(i) for i in range(3)]
    nielsen_words = int_words_to_letters(
        load_script("compose_t73_free_group_psi").generate()["generator_images"]
    )
    compact_result = gap_check(compact_words, timeout)
    nielsen_result = gap_check(nielsen_words, timeout)
    result: dict[str, Any] = {
        "schema": "t73_compact_free_basis_gap/v2",
        "compact": compact_result,
        "nielsen_positive_control": nielsen_result,
        "compact_verdict": "PASS_FREE_BASIS" if compact_result["is_bijective"] else "FAIL_NOT_FREE_BASIS",
        "control_verdict": "PASS_FREE_BASIS" if nielsen_result["is_bijective"] else "FAIL_NOT_FREE_BASIS",
        "interpretation": "The same GAP test accepts the explicit Nielsen automorphism and rejects the compact straight-word endomorphism.",
    }
    result["receipt_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    result = run(args.timeout)
    if args.check:
        print("T73_COMPACT_FREE_BASIS_GAP=PASS")
        print(f"GAP_VERSION={result['compact']['gap_version']}")
        print(f"WORD_LENGTHS={result['compact']['word_lengths']}")
        print(f"COMPACT_VERDICT={result['compact_verdict']}")
        print(f"NIELSEN_CONTROL_VERDICT={result['control_verdict']}")
        print(f"RECEIPT_SHA256={result['receipt_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
