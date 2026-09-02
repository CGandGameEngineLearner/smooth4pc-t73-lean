from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


EXPECTED_CERTIFICATE_SHA256 = (
    "5BB04100EE9BA52959D2086FECEC079CC3E8DA5086D01A83EA3791E62848E961"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify the exact frozen global certificate bytes."
    )
    parser.add_argument(
        "--certificate",
        type=Path,
        default=_repo_root() / "data" / "GLOBAL_FALSIFICATION_CHAIN_CERT.json",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        actual = hashlib.sha256(args.certificate.read_bytes()).hexdigest().upper()
    except OSError as error:
        print(f"certificate-sha gate: FAIL: {error}", file=sys.stderr)
        return 1

    if actual != EXPECTED_CERTIFICATE_SHA256:
        print(
            "certificate-sha gate: FAIL: "
            f"expected {EXPECTED_CERTIFICATE_SHA256}, got {actual}",
            file=sys.stderr,
        )
        return 1

    print(f"certificate-sha gate: PASS: {actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
