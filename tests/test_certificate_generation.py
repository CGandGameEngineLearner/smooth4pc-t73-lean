from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPECTED_CERTIFICATE_SHA256 = (
    "5BB04100EE9BA52959D2086FECEC079CC3E8DA5086D01A83EA3791E62848E961"
)

SYNCHRONIZED_COMMAND_MUTANTS = (
    ("axiom", "axiom illicitAxiom : False"),
    ("opaque", "opaque illicitOpaque : Nat := 0"),
    ("instance", "instance : Inhabited Nat := ⟨0⟩"),
    ("example", "example : True := by trivial"),
    ("abbrev", "abbrev illicitAbbrev : Nat := 0"),
    ("syntax", 'syntax "illicitSyntax" : term'),
    ("macro", 'macro "illicitMacro" : term => `(0)'),
    ("eval", "#eval 1"),
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


class CertificateGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.certificate = cls.repo / "data" / "GLOBAL_FALSIFICATION_CHAIN_CERT.json"
        cls.generator = cls.repo / "scripts" / "generate_certificate_data.py"
        cls.sha_checker = cls.repo / "scripts" / "check_certificate_sha.py"
        cls.generated_checker = cls.repo / "scripts" / "check_generated_data.py"
        cls.checked_in_generated = cls.repo / "Smooth4PC" / "CertificateData.lean"

    def run_script(
        self, script: Path, *args: object, cwd: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *(str(arg) for arg in args)],
            cwd=cwd or self.repo,
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
        self.assertIn("data-only syntax gate: PASS", result.stdout)
        self.assertIn("generated-data gate: PASS", result.stdout)

    def test_generated_lean_has_exact_namespace_fields_and_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "CertificateData.lean"
            lines = self.generate(generated).decode("utf-8").splitlines()

        self.assertIn("namespace Smooth4PC", lines)
        self.assertIn("end Smooth4PC", lines)
        declarations = [line for line in lines if line.startswith("def ")]
        names_and_types = []
        for declaration in declarations:
            head, _separator, _rhs = declaration.partition(" := ")
            name, field_type = head.removeprefix("def ").split(" : ", 1)
            names_and_types.append((name, field_type))
        self.assertEqual(tuple(names_and_types), EXPECTED_FIELDS_AND_TYPES)

    def test_synchronized_generator_and_output_command_mutants_fail_data_only_gate(
        self,
    ) -> None:
        anchor = '    return "\\n".join(lines).encode("utf-8")'
        for mutant_name, command in SYNCHRONIZED_COMMAND_MUTANTS:
            with self.subTest(mutant=mutant_name), tempfile.TemporaryDirectory() as tmp:
                mutant_repo = Path(tmp)
                mutant_scripts = mutant_repo / "scripts"
                mutant_data = mutant_repo / "data"
                mutant_output = mutant_repo / "Smooth4PC" / "CertificateData.lean"
                mutant_scripts.mkdir(parents=True)
                mutant_data.mkdir(parents=True)
                mutant_output.parent.mkdir(parents=True)

                mutant_generator = mutant_scripts / self.generator.name
                mutant_checker = mutant_scripts / self.generated_checker.name
                mutant_certificate = mutant_data / self.certificate.name
                shutil.copy2(self.generator, mutant_generator)
                shutil.copy2(self.generated_checker, mutant_checker)
                shutil.copy2(self.certificate, mutant_certificate)

                source = mutant_generator.read_text(encoding="utf-8")
                self.assertEqual(source.count(anchor), 1)
                injected = f"    lines.insert(-2, {command!r})\n{anchor}"
                mutant_generator.write_text(
                    source.replace(anchor, injected), encoding="utf-8", newline=""
                )

                generation = self.run_script(
                    mutant_generator,
                    "--certificate",
                    mutant_certificate,
                    "--output",
                    mutant_output,
                    cwd=mutant_repo,
                )
                self.assertEqual(
                    generation.returncode, 0, generation.stdout + generation.stderr
                )

                check = self.run_script(
                    mutant_checker,
                    "--certificate",
                    mutant_certificate,
                    "--generated",
                    mutant_output,
                    cwd=mutant_repo,
                )

                self.assertNotEqual(check.returncode, 0, command)
                self.assertIn("data-only syntax gate: FAIL", check.stderr)

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
