from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

import generate_certificate_data


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
        actual = args.generated.read_bytes()
        with tempfile.TemporaryDirectory(prefix="certificate-data-check-") as tmp:
            regenerated_path = Path(tmp) / "CertificateData.lean"
            expected = generate_certificate_data.generate_file(
                args.certificate, regenerated_path
            )
            if regenerated_path.read_bytes() != expected:
                raise RuntimeError("temporary regeneration was not byte-stable")
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

    print(
        "generated-data gate: PASS: "
        f"{hashlib.sha256(actual).hexdigest().upper()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
