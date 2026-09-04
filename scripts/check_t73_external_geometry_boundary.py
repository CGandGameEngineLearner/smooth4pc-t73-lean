#!/usr/bin/env python3
"""Reject fake Lean inhabitants while reporting the remaining analytic gap."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SMOOTH = ROOT / "Smooth4PC"


def check() -> None:
    sources = {
        path: path.read_text(encoding="utf-8")
        for path in SMOOTH.glob("*.lean")
    }
    forbidden = (
        "instance ExternalGeometry",
        "instance CSTopologyData",
        "def t73ExternalGeometry",
        "axiom t73ExternalGeometry",
        "axiom t73CSTopologyData",
    )
    for path, text in sources.items():
        for token in forbidden:
            if token in text:
                raise AssertionError(f"fake or unreviewed geometry inhabitant in {path}: {token}")
    joined = "\n".join(sources.values())
    required_interfaces = (
        "structure ExternalGeometry",
        "structure CSTopologyData",
        "IsActualMWWCoequalizer",
        "IsActualMWWTransport",
        "diffeomorphismEquiv",
    )
    for token in required_interfaces:
        if token not in joined:
            raise AssertionError(f"formal boundary no longer exposes {token}")


def main() -> None:
    check()
    print("T73_EXTERNAL_GEOMETRY=OPEN_MISSING_ANALYTIC_MWW_FOUNDATIONS")
    print("T73_FAKE_INHABITANT=ABSENT")


if __name__ == "__main__":
    main()
