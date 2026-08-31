from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPECTED_CERTIFICATE_SHA256 = (
    "8B4A0B39ABABD7CFA284E67189A8AF4E60473F88CADC8722A1ABA8321B72EB86"
)


class CertificateGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.certificate = cls.repo / "data" / "GLOBAL_FALSIFICATION_CHAIN_CERT.json"
        cls.generator = cls.repo / "scripts" / "generate_certificate_data.py"
        cls.sha_checker = cls.repo / "scripts" / "check_certificate_sha.py"
        cls.generated_checker = cls.repo / "scripts" / "check_generated_data.py"
        cls.checked_in_generated = cls.repo / "Smooth4PC" / "CertificateData.lean"

    def run_script(self, script: Path, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *(str(arg) for arg in args)],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def generate(self, output: Path) -> bytes:
        result = self.run_script(
            self.generator,
            "--certificate",
            self.certificate,
            "--output",
            output,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return output.read_bytes()

    def test_exact_certificate_sha_gate_accepts_frozen_file(self) -> None:
        result = self.run_script(
            self.sha_checker, "--certificate", self.certificate
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("certificate-sha gate: PASS", result.stdout)
        self.assertIn(EXPECTED_CERTIFICATE_SHA256, result.stdout)
        self.assertEqual(
            hashlib.sha256(self.certificate.read_bytes()).hexdigest().upper(),
            EXPECTED_CERTIFICATE_SHA256,
        )

    def test_exact_certificate_sha_gate_rejects_modified_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mutated = Path(tmp) / self.certificate.name
            mutated.write_bytes(self.certificate.read_bytes() + b" ")

            result = self.run_script(
                self.sha_checker, "--certificate", mutated
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("certificate-sha gate: FAIL", result.stderr)

    def test_generation_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.lean"
            second = Path(tmp) / "second.lean"

            first_bytes = self.generate(first)
            second_bytes = self.generate(second)

        self.assertEqual(first_bytes, second_bytes)

    def test_checked_in_generated_file_passes_generated_data_gate(self) -> None:
        result = self.run_script(
            self.generated_checker,
            "--certificate",
            self.certificate,
            "--generated",
            self.checked_in_generated,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("generated-data gate: PASS", result.stdout)

    def test_stale_generated_sha_comment_fails_generated_data_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "CertificateData.lean"
            original = self.generate(generated).decode("utf-8")
            stale = original.replace(EXPECTED_CERTIFICATE_SHA256, "0" * 64, 1)
            self.assertNotEqual(stale, original)
            generated.write_text(stale, encoding="utf-8", newline="")

            result = self.run_script(
                self.generated_checker,
                "--certificate",
                self.certificate,
                "--generated",
                generated,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated-data gate: FAIL", result.stderr)
        self.assertNotIn("certificate-sha gate: FAIL", result.stderr)

    def test_generated_numeric_byte_mutation_fails_generated_data_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "CertificateData.lean"
            original = self.generate(generated).decode("utf-8")
            mutated = original.replace("1240", "1241", 1)
            self.assertNotEqual(mutated, original)
            generated.write_text(mutated, encoding="utf-8", newline="")

            result = self.run_script(
                self.generated_checker,
                "--certificate",
                self.certificate,
                "--generated",
                generated,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated-data gate: FAIL", result.stderr)
        self.assertNotIn("certificate-sha gate: FAIL", result.stderr)

    def test_generated_lean_contains_data_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "CertificateData.lean"
            text = self.generate(generated).decode("utf-8")

        for forbidden in (
            "theorem",
            "Prop",
            "proof",
            "sorry",
            "CANDIDATE_CLOSED_PENDING_HOSTILE",
            "logical_consequence_if_hostile_passes",
            '"PASS"',
            "HJ_replacement",
            "S4_control",
        ):
            self.assertNotIn(forbidden, text)

        declarations = [
            line for line in text.splitlines() if line.startswith(("def ", "theorem "))
        ]
        self.assertTrue(declarations)
        self.assertTrue(all(line.startswith("def ") for line in declarations))


if __name__ == "__main__":
    unittest.main()
