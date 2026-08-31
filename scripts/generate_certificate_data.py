from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_CERTIFICATE_SHA256 = (
    "8B4A0B39ABABD7CFA284E67189A8AF4E60473F88CADC8722A1ABA8321B72EB86"
)


class CertificateDataError(ValueError):
    pass


def certificate_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def verify_certificate_bytes(raw: bytes) -> str:
    actual = certificate_sha256(raw)
    if actual != EXPECTED_CERTIFICATE_SHA256:
        raise CertificateDataError(
            "certificate SHA-256 mismatch: "
            f"expected {EXPECTED_CERTIFICATE_SHA256}, got {actual}"
        )
    return actual


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CertificateDataError(f"{path} must be an object")
    return value


def _sequence(value: Any, path: str, length: int) -> list[Any]:
    if not isinstance(value, list) or len(value) != length:
        raise CertificateDataError(f"{path} must be a list of length {length}")
    return value


def _integer(value: Any, path: str) -> int:
    if type(value) is not int:
        raise CertificateDataError(f"{path} must be an integer")
    return value


def _matrix_3x3(value: Any, path: str) -> list[list[int]]:
    rows = _sequence(value, path, 3)
    return [
        [
            _integer(entry, f"{path}[{row_index}][{column_index}]")
            for column_index, entry in enumerate(
                _sequence(row, f"{path}[{row_index}]", 3)
            )
        ]
        for row_index, row in enumerate(rows)
    ]


def extract_whitelisted_data(document: Any) -> dict[str, Any]:
    root = _mapping(document, "$")
    candidate = _mapping(root.get("candidate"), "candidate")
    chain = _mapping(root.get("chain"), "chain")
    one_handle = _mapping(chain.get("one_handle"), "chain.one_handle")
    scalar_pairs = _mapping(
        chain.get("sphere_scalar_pairs"), "chain.sphere_scalar_pairs"
    )

    def scalar(branch: str, key: str) -> int:
        branch_data = _mapping(
            scalar_pairs.get(branch), f"chain.sphere_scalar_pairs.{branch}"
        )
        return _integer(
            branch_data.get(key), f"chain.sphere_scalar_pairs.{branch}.{key}"
        )

    degree = _sequence(chain.get("degree"), "chain.degree", 2)
    return {
        "matrix_a": _matrix_3x3(candidate.get("matrix_A"), "candidate.matrix_A"),
        "matrix_a_minus_i": _matrix_3x3(
            candidate.get("matrix_A_minus_I"), "candidate.matrix_A_minus_I"
        ),
        "det_a_expected": _integer(candidate.get("det_A"), "candidate.det_A"),
        "det_a_minus_i_expected": _integer(
            candidate.get("det_A_minus_I"), "candidate.det_A_minus_I"
        ),
        "one_handle_actual_cap_h3": _integer(
            one_handle.get("actual_cap_h3"), "chain.one_handle.actual_cap_h3"
        ),
        "degree": [
            _integer(entry, f"chain.degree[{index}]")
            for index, entry in enumerate(degree)
        ],
        "sphere_columns": _matrix_3x3(
            chain.get("sphere_columns"), "chain.sphere_columns"
        ),
        "sphere_det_expected": _integer(
            chain.get("sphere_det"), "chain.sphere_det"
        ),
        "th1_sigma0_scalar": scalar("TH1", "C_Sigma0_input_h3"),
        "th1_sigma1_minus_id_scalar": scalar(
            "TH1", "C_(Sigma1-Id)_input_h3"
        ),
        "th2_sigma0_scalar": scalar("TH2", "C_Sigma0_input_h3"),
        "th2_sigma1_minus_id_scalar": scalar(
            "TH2", "C_(Sigma1-Id)_input_h3"
        ),
        "thxy_sigma0_scalar": scalar("THXY", "C_Sigma0_input_h3"),
        "thxy_sigma1_minus_id_scalar": scalar(
            "THXY", "C_(Sigma1-Id)_input_h3"
        ),
    }


def _lean_int(value: int) -> str:
    return str(value)


def _lean_int_list(values: list[int]) -> str:
    return "[" + ", ".join(_lean_int(value) for value in values) + "]"


def _lean_int_matrix(rows: list[list[int]]) -> str:
    return "[" + ", ".join(_lean_int_list(row) for row in rows) + "]"


def render_lean(data: dict[str, Any], source_sha256: str) -> bytes:
    lines = [
        "-- Generated from the frozen global falsification certificate.",
        f"-- Source certificate SHA256: {source_sha256}",
        "-- Regenerate with scripts/generate_certificate_data.py; do not edit.",
        "",
        "namespace Smooth4PC.CertificateData",
        "",
        f'def sourceCertificateSha256 : String := "{source_sha256}"',
        f"def matrixA : List (List Int) := {_lean_int_matrix(data['matrix_a'])}",
        "def matrixAMinusI : List (List Int) := "
        + _lean_int_matrix(data["matrix_a_minus_i"]),
        f"def detAExpected : Int := {_lean_int(data['det_a_expected'])}",
        "def detAMinusIExpected : Int := "
        + _lean_int(data["det_a_minus_i_expected"]),
        "def oneHandleActualCapH3 : Int := "
        + _lean_int(data["one_handle_actual_cap_h3"]),
        f"def degree : List Int := {_lean_int_list(data['degree'])}",
        "def sphereColumns : List (List Int) := "
        + _lean_int_matrix(data["sphere_columns"]),
        "def sphereDetExpected : Int := "
        + _lean_int(data["sphere_det_expected"]),
        "def th1Sigma0Scalar : Int := " + _lean_int(data["th1_sigma0_scalar"]),
        "def th1Sigma1MinusIdScalar : Int := "
        + _lean_int(data["th1_sigma1_minus_id_scalar"]),
        "def th2Sigma0Scalar : Int := " + _lean_int(data["th2_sigma0_scalar"]),
        "def th2Sigma1MinusIdScalar : Int := "
        + _lean_int(data["th2_sigma1_minus_id_scalar"]),
        "def thxySigma0Scalar : Int := "
        + _lean_int(data["thxy_sigma0_scalar"]),
        "def thxySigma1MinusIdScalar : Int := "
        + _lean_int(data["thxy_sigma1_minus_id_scalar"]),
        "",
        "end Smooth4PC.CertificateData",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def generate_bytes(certificate: Path) -> bytes:
    raw = certificate.read_bytes()
    source_sha256 = verify_certificate_bytes(raw)
    try:
        document = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CertificateDataError(f"invalid certificate JSON: {error}") from error
    data = extract_whitelisted_data(document)
    return render_lean(data, source_sha256)


def generate_file(certificate: Path, output: Path) -> bytes:
    generated = generate_bytes(certificate)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(generated)
    return generated


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    repo = _repo_root()
    parser = argparse.ArgumentParser(
        description="Generate data-only Lean constants from the frozen certificate."
    )
    parser.add_argument(
        "--certificate",
        type=Path,
        default=repo / "data" / "GLOBAL_FALSIFICATION_CHAIN_CERT.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repo / "Smooth4PC" / "CertificateData.lean",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        generated = generate_file(args.certificate, args.output)
    except (CertificateDataError, OSError) as error:
        print(f"certificate-generation gate: FAIL: {error}", file=sys.stderr)
        return 1
    print(
        "certificate-generation gate: OK: "
        f"{args.output} ({len(generated)} bytes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
