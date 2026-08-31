from __future__ import annotations

import argparse
import hashlib
import re
import sys
import tempfile
from pathlib import Path

import generate_certificate_data


EXPECTED_SOURCE_SHA256 = (
    "8B4A0B39ABABD7CFA284E67189A8AF4E60473F88CADC8722A1ABA8321B72EB86"
)
FIXED_COMMENTS = (
    "-- Generated from the frozen global falsification certificate.",
    f"-- Source certificate SHA256: {EXPECTED_SOURCE_SHA256}",
    "-- Regenerate with scripts/generate_certificate_data.py; do not edit.",
)
EXPECTED_FIELDS_AND_TYPES = (
    ("sourceCertificateSha256", "String"),
    ("matrixA", "List (List Int)"),
    ("matrixAMinusI", "List (List Int)"),
    ("detAExpected", "Int"),
    ("detAMinusIExpected", "Int"),
    ("oneHandleActualCapH3", "Int"),
    ("degree", "List Int"),
    ("sphereColumns", "List (List Int)"),
    ("sphereDetExpected", "Int"),
    ("th1Sigma0Scalar", "Int"),
    ("th1Sigma1MinusIdScalar", "Int"),
    ("th2Sigma0Scalar", "Int"),
    ("th2Sigma1MinusIdScalar", "Int"),
    ("thxySigma0Scalar", "Int"),
    ("thxySigma1MinusIdScalar", "Int"),
)

_INTEGER_LITERAL = r"-?(?:0|[1-9][0-9]*)"
_INTEGER_LIST_LITERAL = rf"\[{_INTEGER_LITERAL}(?:, {_INTEGER_LITERAL})*\]"
_INTEGER_MATRIX_LITERAL = (
    rf"\[{_INTEGER_LIST_LITERAL}(?:, {_INTEGER_LIST_LITERAL})*\]"
)
_DEFINITION = re.compile(
    r"def (?P<name>[A-Za-z][A-Za-z0-9]*) : "
    r"(?P<type>String|Int|List Int|List \(List Int\)) := (?P<rhs>.+)"
)


class DataOnlySyntaxError(ValueError):
    pass


def _validate_literal(field_name: str, field_type: str, rhs: str) -> None:
    if field_type == "String":
        expected = f'"{EXPECTED_SOURCE_SHA256}"'
        if field_name != "sourceCertificateSha256" or rhs != expected:
            raise DataOnlySyntaxError(
                f"{field_name} must be the exact frozen SHA String literal"
            )
        return

    pattern_by_type = {
        "Int": _INTEGER_LITERAL,
        "List Int": _INTEGER_LIST_LITERAL,
        "List (List Int)": _INTEGER_MATRIX_LITERAL,
    }
    if re.fullmatch(pattern_by_type[field_type], rhs) is None:
        raise DataOnlySyntaxError(
            f"{field_name} must use a literal RHS of type {field_type}"
        )


def validate_data_only_syntax(raw: bytes) -> None:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise DataOnlySyntaxError(f"generated Lean is not UTF-8: {error}") from error

    nonblank: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line == "":
            continue
        if line.strip() == "":
            raise DataOnlySyntaxError(
                f"line {line_number}: blank lines must contain zero bytes"
            )
        nonblank.append((line_number, line))

    expected_nonblank_count = len(FIXED_COMMENTS) + len(EXPECTED_FIELDS_AND_TYPES) + 2
    if len(nonblank) != expected_nonblank_count:
        raise DataOnlySyntaxError(
            "expected exactly "
            f"{expected_nonblank_count} nonblank lines, got {len(nonblank)}"
        )

    for index, expected_comment in enumerate(FIXED_COMMENTS):
        line_number, line = nonblank[index]
        if line != expected_comment:
            raise DataOnlySyntaxError(
                f"line {line_number}: expected fixed comment {expected_comment!r}"
            )

    namespace_index = len(FIXED_COMMENTS)
    namespace_line_number, namespace_line = nonblank[namespace_index]
    if namespace_line != "namespace Smooth4PC":
        raise DataOnlySyntaxError(
            f"line {namespace_line_number}: expected exact namespace Smooth4PC"
        )

    declarations_start = namespace_index + 1
    for offset, (expected_name, expected_type) in enumerate(
        EXPECTED_FIELDS_AND_TYPES
    ):
        line_number, line = nonblank[declarations_start + offset]
        match = _DEFINITION.fullmatch(line)
        if match is None:
            raise DataOnlySyntaxError(
                f"line {line_number}: only canonical def declarations are allowed"
            )
        actual_name = match.group("name")
        actual_type = match.group("type")
        if (actual_name, actual_type) != (expected_name, expected_type):
            raise DataOnlySyntaxError(
                f"line {line_number}: expected {expected_name} : {expected_type}, "
                f"got {actual_name} : {actual_type}"
            )
        _validate_literal(actual_name, actual_type, match.group("rhs"))

    end_line_number, end_line = nonblank[-1]
    if end_line != "end Smooth4PC":
        raise DataOnlySyntaxError(
            f"line {end_line_number}: expected exact end Smooth4PC"
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    repo = _repo_root()
    parser = argparse.ArgumentParser(
        description="Regenerate CertificateData.lean temporarily and compare bytes."
    )
    parser.add_argument(
        "--certificate",
        type=Path,
        default=repo / "data" / "GLOBAL_FALSIFICATION_CHAIN_CERT.json",
    )
    parser.add_argument(
        "--generated",
        type=Path,
        default=repo / "Smooth4PC" / "CertificateData.lean",
    )
    return parser.parse_args(argv)


def _first_difference(expected: bytes, actual: bytes) -> int:
    for index, (expected_byte, actual_byte) in enumerate(zip(expected, actual)):
        if expected_byte != actual_byte:
            return index
    return min(len(expected), len(actual))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        with tempfile.TemporaryDirectory(prefix="certificate-data-check-") as tmp:
            regenerated_path = Path(tmp) / "CertificateData.lean"
            expected = generate_certificate_data.generate_file(
                args.certificate, regenerated_path
            )
            if regenerated_path.read_bytes() != expected:
                raise RuntimeError("temporary regeneration was not byte-stable")
        actual = args.generated.read_bytes()
    except (generate_certificate_data.CertificateDataError, OSError, RuntimeError) as error:
        print(f"generated-data gate: FAIL: {error}", file=sys.stderr)
        return 1

    if actual != expected:
        offset = _first_difference(expected, actual)
        expected_sha = hashlib.sha256(expected).hexdigest().upper()
        actual_sha = hashlib.sha256(actual).hexdigest().upper()
        print(
            "generated-data gate: FAIL: byte mismatch "
            f"at offset {offset}; expected SHA256 {expected_sha}, "
            f"got {actual_sha}",
            file=sys.stderr,
        )
        return 1

    try:
        validate_data_only_syntax(expected)
        validate_data_only_syntax(actual)
    except DataOnlySyntaxError as error:
        print(f"data-only syntax gate: FAIL: {error}", file=sys.stderr)
        return 1

    print("data-only syntax gate: PASS")
    print(
        "generated-data gate: PASS: "
        f"{hashlib.sha256(actual).hexdigest().upper()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
