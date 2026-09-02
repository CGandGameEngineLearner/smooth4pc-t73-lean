#!/usr/bin/env python3
"""Generate the unique B88 position-to-physical-passage table.

The Artin word uses the collar wicket numbering.  This generator joins that
numbering to the west-boundary physical endpoints in HATTORI_Y_TANGLE.json.
It does not consume the conflicting THXY B88 index labels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_COLLAR = Path(r"D:\tmp\r6\agents\t73_collar_braid\T73_COLLAR_BRAID.json")
DEFAULT_HATTORI = Path(r"D:\tmp\r6\agents\t73_collar_braid\HATTORI_Y_TANGLE.json")
DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "B88_POSITION_TO_PASSAGE_TABLE.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def passage_from_endpoint(endpoint_id: str) -> str:
    if not endpoint_id.startswith("ep:") or endpoint_id.rsplit(":", 1)[-1] not in {"entry", "exit"}:
        raise ValueError(f"unexpected endpoint id: {endpoint_id}")
    return "pass:" + endpoint_id[3:].rsplit(":", 1)[0]


def collar_wickets(collar: dict[str, Any]) -> dict[int, dict[str, Any]]:
    source = collar["wickets"]
    result = {
        1: {"owner": source["W1"]["owner"], "word_letter": source["W1"]["word_letter"]},
        2: {"owner": source["W2"]["owner"], "word_letter": source["W2"]["word_letter"]},
    }
    for row in source["m2"]:
        result[row["wicket"]] = {
            "owner": "m_2",
            "word_letter": row["word_letter_index"],
        }
    if sorted(result) != list(range(1, 45)):
        raise ValueError("collar wicket numbering is not exactly 1..44")
    return result


def west_endpoints(hattori: dict[str, Any]) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for row in hattori["standard_z_contraction"]["component_ledger"]:
        if row.get("component_type") != "Y_WICKET_PATH" or row.get("y_boundary_side") != "west":
            continue
        wicket = int(row["wicket_label"])
        signs: dict[str, str] = {}
        for endpoint in row["y_endpoints"]:
            key = "neg" if endpoint["cable_sign"] == "negative" else "pos"
            signs[key] = endpoint["endpoint_id"]
        if set(signs) != {"neg", "pos"}:
            raise ValueError(f"wicket {wicket} lacks one west endpoint sign")
        if wicket in result:
            raise ValueError(f"duplicate west endpoint record for wicket {wicket}")
        result[wicket] = signs
    if sorted(result) != list(range(1, 45)):
        raise ValueError("Hattori west records do not cover wickets 1..44")
    return result


def build(collar_path: Path, hattori_path: Path) -> dict[str, Any]:
    collar = json.loads(collar_path.read_text(encoding="utf-8"))
    hattori = json.loads(hattori_path.read_text(encoding="utf-8"))
    wickets = collar_wickets(collar)
    endpoints = west_endpoints(hattori)
    positions = []
    for wicket in range(1, 45):
        for offset, sign in enumerate(("neg", "pos")):
            endpoint_id = endpoints[wicket][sign]
            positions.append(
                {
                    "index": 2 * (wicket - 1) + offset,
                    "wicket": wicket,
                    "owner": wickets[wicket]["owner"],
                    "word_letter": wickets[wicket]["word_letter"],
                    "sign": sign,
                    "passage_id": passage_from_endpoint(endpoint_id),
                    "endpoint_id": endpoint_id.rsplit(":", 1)[0],
                }
            )
    return {
        "schema": "b88_position_to_passage_table/v1",
        "coordinate_authority": "T73_COLLAR_BRAID.json/wickets",
        "endpoint_binding": "HATTORI_Y_TANGLE.json/standard_z_contraction/component_ledger west Y_WICKET_PATH rows",
        "sources": {
            "T73_COLLAR_BRAID.json": {
                "sha256": sha256(collar_path),
                "bytes": collar_path.stat().st_size,
            },
            "HATTORI_Y_TANGLE.json": {
                "sha256": sha256(hattori_path),
                "bytes": hattori_path.stat().st_size,
            },
        },
        "positions": positions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collar", type=Path, default=DEFAULT_COLLAR)
    parser.add_argument("--hattori", type=Path, default=DEFAULT_HATTORI)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(args.collar.resolve(), args.hattori.resolve())
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
            raise SystemExit("B88 position table is absent or stale")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8", newline="\n")
    output_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest().upper()
    print(f"ROWS={len(payload['positions'])}")
    print(f"OUTPUT_SHA256={output_sha}")
    print("INDEX2=" + json.dumps(payload["positions"][2], sort_keys=True, separators=(",", ":")))
    print("INDEX87=" + json.dumps(payload["positions"][87], sort_keys=True, separators=(",", ":")))
    print("VERIFY=PASS")


if __name__ == "__main__":
    main()
