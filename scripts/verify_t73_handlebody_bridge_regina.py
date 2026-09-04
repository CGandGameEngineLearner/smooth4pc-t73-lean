#!/usr/bin/env python3
"""Call Regina recogniseHandlebody on the four dual-block handlebodies.

This script does not read a self-reported PASS field.  It builds a Regina
triangulation from the stored face gluings and asks Regina for the genus.
If the Regina engine is not available, the status is UNAVAILABLE and P0a
stays Open.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TORUS = ROOT / "geometry" / "t73_common_torus_triangulation.json"
AUDIT = ROOT / "audit" / "t73_handlebody_bridge_regina.json"


REGINA_RUNNER = r"""
import json
import sys

import regina

payload = json.loads(sys.stdin.read())
results = {}
for name, block in payload["gluings"].items():
    tri = regina.Triangulation3()
    simplices = [tri.newSimplex() for _ in range(block["simplex_count"])]
    for source, facet, target, perm in block["gluings"]:
        simplices[source].join(facet, simplices[target], regina.Perm4(*perm))
    if tri.size() != block["simplex_count"]:
        raise SystemExit(f"{name}: simplex count mismatch")
    if tri.countBoundaryFacets() != block["boundary_triangles"]:
        raise SystemExit(
            f"{name}: boundary {tri.countBoundaryFacets()} != {block['boundary_triangles']}"
        )
    tri.intelligentSimplify()
    genus = int(tri.recogniseHandlebody())
    results[name] = {
        "recogniseHandlebody": genus,
        "simplified_size": tri.size(),
        "is_handlebody": genus == 3,
    }
json.dump(results, sys.stdout)
print()
"""


def find_regina_python() -> list[str] | None:
    try:
        import regina  # noqa: F401

        return [sys.executable]
    except ImportError:
        pass
    local = Path.home() / ".venvs" / "regina" / "bin" / "python"
    if local.is_file():
        return [str(local)]
    wsl = [
        "wsl",
        "-e",
        "bash",
        "-lc",
        "$HOME/.venvs/regina/bin/python",
    ]
    try:
        probe = subprocess.run(
            [
                "wsl",
                "-e",
                "bash",
                "-lc",
                "$HOME/.venvs/regina/bin/python -c 'import regina'",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if probe.returncode == 0:
            return wsl
    except OSError:
        return None
    return None


def run_regina(gluings: dict[str, Any], python_cmd: list[str]) -> dict[str, Any]:
    payload = json.dumps({"gluings": gluings})
    if python_cmd[:1] == ["wsl"]:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", suffix=".py", delete=False
        ) as handle:
            handle.write(REGINA_RUNNER)
            runner = handle.name
        try:
            win = Path(runner)
            wsl_runner = "/mnt/" + win.drive[0].lower() + win.as_posix()[2:]
            data_path = win.with_suffix(".json")
            data_path.write_text(payload, encoding="utf-8")
            wsl_data = "/mnt/" + data_path.drive[0].lower() + data_path.as_posix()[2:]
            command = [
                "wsl",
                "-e",
                "bash",
                "-lc",
                f"$HOME/.venvs/regina/bin/python {wsl_runner} < {wsl_data}",
            ]
            completed = subprocess.run(
                command, check=False, capture_output=True, text=True
            )
        finally:
            os.unlink(runner)
            data_json = Path(runner).with_suffix(".json")
            if data_json.exists():
                data_json.unlink()
    else:
        completed = subprocess.run(
            python_cmd + ["-c", REGINA_RUNNER],
            check=False,
            input=payload,
            capture_output=True,
            text=True,
        )
    if completed.returncode != 0:
        raise RuntimeError(
            "Regina runner failed:\n"
            + completed.stdout
            + completed.stderr
        )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("Regina runner produced no JSON")
    return json.loads(lines[-1])


def verify() -> dict[str, Any]:
    torus = json.loads(TORUS.read_text(encoding="utf-8"))
    gluings = torus["gluings"]
    expected = ("H_J_0", "H_J_1", "H_AR_0", "H_AR_1")
    if tuple(gluings) != expected and set(gluings) != set(expected):
        raise AssertionError("torus file is missing a handlebody gluing")
    python_cmd = find_regina_python()
    result: dict[str, Any] = {
        "schema": "t73_handlebody_bridge_regina/v1",
        "engine": None,
        "REGINA_HANDLEBODY": "UNAVAILABLE",
        "genera": {},
        "P0A_BY_REGINA": "OPEN",
    }
    if python_cmd is None:
        result["reason"] = "Regina Python engine is not installed"
        return result
    result["engine"] = python_cmd
    genera = run_regina(gluings, python_cmd)
    result["genera"] = genera
    mutated = json.loads(json.dumps(gluings["H_J_0"]))
    mutated["gluings"][0][3] = list(reversed(mutated["gluings"][0][3]))
    try:
        bad = run_regina({"H_J_0": mutated}, python_cmd)
        mutation = "FAIL" if bad["H_J_0"].get("recogniseHandlebody") != 3 else "UNEXPECTED_PASS"
    except (RuntimeError, KeyError, json.JSONDecodeError):
        mutation = "FAIL"
    result["MUTATION_GLUING"] = mutation
    if mutation != "FAIL":
        result["REGINA_HANDLEBODY"] = "FAIL"
        result["P0A_BY_REGINA"] = "OPEN"
        result["reason"] = "mutated gluing was still accepted as a genus-3 handlebody"
        return result
    if all(entry.get("recogniseHandlebody") == 3 for entry in genera.values()) and set(
        genera
    ) == set(expected):
        result["REGINA_HANDLEBODY"] = "PASS"
        result["P0A_BY_REGINA"] = "PROVED"
    else:
        result["REGINA_HANDLEBODY"] = "FAIL"
        result["P0A_BY_REGINA"] = "OPEN"
        result["reason"] = "Regina did not return genus 3 for every handlebody"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.write:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        AUDIT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE={AUDIT}")
    if args.check:
        print(f"REGINA_HANDLEBODY={result['REGINA_HANDLEBODY']}")
        print(f"P0A_BY_REGINA={result['P0A_BY_REGINA']}")
        if result["REGINA_HANDLEBODY"] == "PASS":
            print("P0A_STATUS=PROVED")
        else:
            print("P0A_STATUS=OPEN")
        for name, entry in sorted(result.get("genera", {}).items()):
            print(f"{name}_GENUS={entry.get('recogniseHandlebody')}")
        if result.get("MUTATION_GLUING"):
            print(f"MUTATION_GLUING={result['MUTATION_GLUING']}")
        if result["REGINA_HANDLEBODY"] == "UNAVAILABLE":
            print(f"REASON={result.get('reason')}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
