from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FORBIDDEN_DECLARATIONS: tuple[tuple[str, str], ...] = (
    ("axiom", r"\baxiom\b"),
    ("constant", r"\bconstant\b"),
    ("opaque", r"\bopaque\b"),
    ("unsafe", r"\bunsafe\b"),
    ("extern", r"\bextern\b"),
    ("implemented_by", r"\bimplemented_by\b"),
    ("run_tac", r"\brun_tac\b"),
    ("sorry", r"\bsorry\b"),
    ("sorryAx", r"\bsorryAx\b"),
    ("admit", r"\badmit\b"),
    ("native_decide", r"\bnative_decide\b"),
    ("Lean.ofReduceBool", r"\bLean\.ofReduceBool\b"),
)

CONCLUSION_TOKENS = (
    "False",
    "notStandard",
    "finalClassSurvives",
    "c3Nonzero",
    "valueAtW3",
)


def lean_sources(root: Path, requested: list[Path]) -> list[Path]:
    if requested:
        return [root / source for source in requested]
    return sorted(path for path in root.rglob("*.lean") if ".lake" not in path.parts)


def collect_forbidden_aliases(text: str) -> set[str]:
    aliases: set[str] = set()
    alias_pattern = re.compile(r"^\s*(?:abbrev|def)\s+([A-Za-z][A-Za-z0-9_']*)\b.*:=\s*(.*)$")
    for line in text.splitlines():
        match = alias_pattern.match(line)
        if not match:
            continue
        name, body = match.groups()
        if any(token in body for token in CONCLUSION_TOKENS):
            aliases.add(name)
    return aliases


def field_type_blocks(text: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^\s*[A-Za-z][A-Za-z0-9_']*\s*:\s*(.*)$", line)
        if not match:
            index += 1
            continue
        start = index + 1
        pieces = [match.group(1)]
        index += 1
        while index < len(lines):
            next_line = lines[index]
            if re.match(r"^\s*[A-Za-z][A-Za-z0-9_']*\s*:\s*", next_line):
                break
            if next_line.startswith("  ") or next_line.startswith("\t"):
                pieces.append(next_line.strip())
                index += 1
                continue
            break
        blocks.append((start, " ".join(piece for piece in pieces if piece)))
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail closed on unreviewed Lean declarations.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source", type=Path, action="append", default=[])
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    field_errors: list[str] = []
    for source in lean_sources(root, args.source):
        if not source.is_file():
            errors.append(f"missing source: {source}")
            continue
        text = source.read_text(encoding="utf-8")
        forbidden_aliases = collect_forbidden_aliases(text)
        for label, pattern in FORBIDDEN_DECLARATIONS:
            if re.search(pattern, text):
                errors.append(f"{source}: forbidden {label}")
        forbidden_type_names = "|".join(re.escape(token) for token in (*CONCLUSION_TOKENS, *forbidden_aliases))
        for line_number, field_type in field_type_blocks(text):
            if forbidden_type_names and re.search(rf"\b(?:{forbidden_type_names})\b", field_type):
                field_errors.append(f"{source}:{line_number}: broad conclusion-carrying interface field")
            elif re.search(r"\bDiffeomorphic\b.*→\s*0\s*=\s*1|\bDiffeomorphic\b.*->\s*0\s*=\s*1", field_type):
                field_errors.append(f"{source}:{line_number}: broad conclusion-carrying interface field")
    if errors:
        print("declaration gate: FAIL", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    if field_errors:
        print("interface-field gate: FAIL", file=sys.stderr)
        print("\n".join(field_errors), file=sys.stderr)
        return 1
    print("declaration gate: PASS")
    print("interface-field gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
