from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPECTED_TASK3_MANIFEST_SHA256 = (
    "121AD27A90D9BE103FD491EC37C2B0070B81E6AFE0A968C7FAA551416744E25E"
)
TASK3_GROUPS = {
    "positive": ("AuditArithmetic.lean", None, 0),
    "degree_mutant": (
        "tests/fixtures/arithmetic_mutants/degree_mutant.lean",
        ("degreeMutant_494_should_fail",),
        1,
    ),
    "det_implementation_mutant": (
        "tests/fixtures/arithmetic_mutants/det_implementation_mutant.lean",
        ("detImplementationMutant_should_fail",),
        1,
    ),
    "entry_mutant": (
        "tests/fixtures/arithmetic_mutants/entry_mutant.lean",
        ("entryMutant_det_should_fail",),
        1,
    ),
    "transpose_mutant": (
        "tests/fixtures/arithmetic_mutants/transpose_mutant.lean",
        ("transposeMutant_rowMajorEntry_should_fail",),
        1,
    ),
    "value_mutant": (
        "tests/fixtures/arithmetic_mutants/value_mutant.lean",
        ("valueMutant_h3_should_fail",),
        1,
    ),
    "exact_data_sync_mutant": (
        "AuditArithmetic.lean",
        (
            "exactData_matrixA",
            "exactData_matrixAMinusI",
            "exactData_sphereColumns",
        ),
        1,
    ),
}
EXACT_DATA_THEOREM_FRAGMENTS = (
    "theorem exactData_matrixA : matrixA = [[0, 269, 1240], [0, 41, 189], [1, 0, 32]] := by",
    "theorem exactData_matrixAMinusI : matrixAMinusI = [[-1, 269, 1240], [0, 40, 189], [1, 0, 31]] := by",
    "theorem exactData_sphereColumns : sphereColumns = [[-1311, 8608, -1], [-189, 1241, 0], [41, -269, 1]] := by",
    "theorem exactData_oneHandleActualCapH3 : oneHandleActualCapH3 = -59072 := by",
    "theorem exactData_degree : degree = [0, 494] := by",
    "theorem exactData_detAExpected : detAExpected = 1 := by",
    "theorem exactData_detAMinusIExpected : detAMinusIExpected = 1 := by",
    "theorem exactData_sphereDetExpected : sphereDetExpected = 1 := by",
    "theorem exactData_th1Sigma0Scalar : th1Sigma0Scalar = 0 := by",
    "theorem exactData_th1Sigma1MinusIdScalar : th1Sigma1MinusIdScalar = 0 := by",
    "theorem exactData_th2Sigma0Scalar : th2Sigma0Scalar = 0 := by",
    "theorem exactData_th2Sigma1MinusIdScalar : th2Sigma1MinusIdScalar = 0 := by",
    "theorem exactData_thxySigma0Scalar : thxySigma0Scalar = 0 := by",
    "theorem exactData_thxySigma1MinusIdScalar : thxySigma1MinusIdScalar = 0 := by",
)
EXACT_GENERATED_DEFINITIONS = (
    "def matrixA : List (List Int) := [[0, 269, 1240], [0, 41, 189], [1, 0, 32]]",
    "def matrixAMinusI : List (List Int) := [[-1, 269, 1240], [0, 40, 189], [1, 0, 31]]",
    "def sphereColumns : List (List Int) := [[-1311, 8608, -1], [-189, 1241, 0], [41, -269, 1]]",
    "def oneHandleActualCapH3 : Int := -59072",
    "def degree : List Int := [0, 494]",
    "def detAExpected : Int := 1",
    "def detAMinusIExpected : Int := 1",
    "def sphereDetExpected : Int := 1",
    "def th1Sigma0Scalar : Int := 0",
    "def th1Sigma1MinusIdScalar : Int := 0",
    "def th2Sigma0Scalar : Int := 0",
    "def th2Sigma1MinusIdScalar : Int := 0",
    "def thxySigma0Scalar : Int := 0",
    "def thxySigma1MinusIdScalar : Int := 0",
)
ALTERNATE_DET_ONE_MATRICES = {
    "matrix_a": [[1, 269, 0], [0, 1, 0], [0, 0, 1]],
    "matrix_a_minus_i": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    "sphere_columns": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
}


class ArithmeticAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.arithmetic = cls.repo / "Smooth4PC" / "Arithmetic.lean"
        cls.audit = cls.repo / "AuditArithmetic.lean"
        cls.fixture_dir = cls.repo / "tests" / "fixtures" / "arithmetic_mutants"
        cls.generated = cls.repo / "Smooth4PC" / "CertificateData.lean"
        cls.generator = cls.repo / "scripts" / "generate_certificate_data.py"
        cls.generated_checker = cls.repo / "scripts" / "check_generated_data.py"
        cls.certificate = cls.repo / "data" / "GLOBAL_FALSIFICATION_CHAIN_CERT.json"
        cls.task3_root = cls.repo / "evidence" / "task3"
        cls.task3_evidence = cls.task3_root / "logs" / "task3"

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

    def exact_data_gate(self, generated: Path) -> tuple[int, str]:
        compact_audit = re.sub(
            r"\s+", " ", self.audit.read_text(encoding="utf-8")
        )
        for fragment in EXACT_DATA_THEOREM_FRAGMENTS:
            if fragment not in compact_audit:
                return 1, f"exact-data gate: FAIL: missing {fragment}"

        generated_lines = set(generated.read_text(encoding="utf-8").splitlines())
        for definition in EXACT_GENERATED_DEFINITIONS:
            if definition not in generated_lines:
                return 1, f"exact-data gate: FAIL: missing {definition}"
        return 0, "exact-data gate: PASS"

    def test_required_arithmetic_sources_exist(self) -> None:
        self.assertTrue(self.arithmetic.is_file(), "Smooth4PC/Arithmetic.lean is missing")
        self.assertTrue(self.audit.is_file(), "AuditArithmetic.lean is missing")

    def test_forbidden_proof_shortcuts_are_absent(self) -> None:
        forbidden = (
            "native_decide",
            "ofReduceBool",
            "axiom",
            "opaque",
            "sorry",
            "admit",
        )
        combined = self.arithmetic.read_text(encoding="utf-8") + self.audit.read_text(
            encoding="utf-8"
        )
        combined += "".join(
            path.read_text(encoding="utf-8")
            for path in sorted(self.fixture_dir.glob("*.lean"))
        )
        for token in forbidden:
            self.assertNotRegex(combined, rf"\b{re.escape(token)}\b")

    def test_det3_is_explicitly_row_major_and_has_zero_fallback(self) -> None:
        text = self.arithmetic.read_text(encoding="utf-8")
        self.assertIn("Row-major 3 x 3 determinant", text)
        self.assertIn("| [[a, b, c], [d, e, f], [g, h, i]] =>", text)
        self.assertIn("a * (e * i - f * h)", text)
        self.assertIn("- b * (d * i - f * g)", text)
        self.assertIn("+ c * (d * h - e * g)", text)
        self.assertRegex(text, r"(?m)^\s*\| _ => 0$")

    def test_all_required_theorems_exist(self) -> None:
        text = self.audit.read_text(encoding="utf-8")
        names = (
            "matrixA_rowMajor_entry_0_1",
            "det_matrixA_eq_one",
            "det_matrixAMinusI_eq_one",
            "det_sphereColumns_eq_one",
            "cubic_factor_times_epsilon_eq_h3",
            "oneHandleActualCapH3_ne_zero",
            "th1Sigma0_eq_zero",
            "th1Sigma1MinusId_eq_zero",
            "th2Sigma0_eq_zero",
            "th2Sigma1MinusId_eq_zero",
            "thxySigma0_eq_zero",
            "thxySigma1MinusId_eq_zero",
            "degree_subtraction_eq_494",
            "degree_494_ne_zero",
            "certificate_degree_eq",
        )
        for name in names:
            self.assertRegex(text, rf"(?m)^theorem {re.escape(name)}\b")

    def test_exact_data_gate_rejects_synchronized_alternate_det_one_matrices(
        self,
    ) -> None:
        healthy_exit, healthy_message = self.exact_data_gate(self.generated)
        self.assertEqual(healthy_exit, 0, healthy_message)

        def det3(rows: list[list[int]]) -> int:
            (a, b, c), (d, e, f), (g, h, i) = rows
            return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)

        self.assertEqual(ALTERNATE_DET_ONE_MATRICES["matrix_a"][0][1], 269)
        for matrix in ALTERNATE_DET_ONE_MATRICES.values():
            self.assertEqual(det3(matrix), 1)

        with tempfile.TemporaryDirectory() as tmp:
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
            anchor = (
                "def render_lean(data: dict[str, Any], source_sha256: str) -> bytes:\n"
                "    lines = ["
            )
            self.assertEqual(source.count(anchor), 1)
            replacement = (
                "def render_lean(data: dict[str, Any], source_sha256: str) -> bytes:\n"
                "    data = dict(data)\n"
                f"    data['matrix_a'] = {ALTERNATE_DET_ONE_MATRICES['matrix_a']!r}\n"
                "    data['matrix_a_minus_i'] = "
                f"{ALTERNATE_DET_ONE_MATRICES['matrix_a_minus_i']!r}\n"
                "    data['sphere_columns'] = "
                f"{ALTERNATE_DET_ONE_MATRICES['sphere_columns']!r}\n"
                "    lines = ["
            )
            mutant_generator.write_text(
                source.replace(anchor, replacement), encoding="utf-8", newline=""
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
            task2_check = self.run_script(
                mutant_checker,
                "--certificate",
                mutant_certificate,
                "--generated",
                mutant_output,
                cwd=mutant_repo,
            )
            self.assertEqual(
                task2_check.returncode, 0, task2_check.stdout + task2_check.stderr
            )
            self.assertIn("data-only syntax gate: PASS", task2_check.stdout)
            self.assertIn("generated-data gate: PASS", task2_check.stdout)

            attacked_exit, attacked_message = self.exact_data_gate(mutant_output)

        self.assertNotEqual(attacked_exit, 0)
        self.assertIn("exact-data gate: FAIL", attacked_message)

    def test_task3_evidence_tree_and_upload_records(self) -> None:
        expected_files = {
            f"{group}.{suffix}"
            for group in TASK3_GROUPS
            for suffix in (
                "audit.log",
                "stdout.log",
                "stderr.log",
                "exit",
                "receipt.json",
            )
        }
        expected_files.add("TASK3_RUN_MANIFEST.sha256")
        actual_files = {path.name for path in self.task3_evidence.glob("*")}
        self.assertEqual(actual_files, expected_files)

        upload_receipt_path = self.task3_root / "AUDIT_UPLOAD_RECEIPT.json"
        self.assertTrue(upload_receipt_path.is_file(), f"missing {upload_receipt_path}")
        upload_receipt = json.loads(upload_receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(upload_receipt["authorized_upload_count"], 1)
        self.assertEqual(upload_receipt["uploaded_file"], "AuditArithmetic.lean")
        self.assertEqual(
            upload_receipt["preupload_sha256"],
            "85E1A7CBD1EEA56CCF24AA6136E5F90503FA1089E18AA48BCBE6FA3438768D37",
        )
        self.assertEqual(
            upload_receipt["remote_verified_sha256"],
            upload_receipt["preupload_sha256"],
        )
        self.assertEqual(
            upload_receipt["main_certificate_sha256_after"],
            upload_receipt["main_certificate_sha256_before"],
        )
        self.assertEqual(
            upload_receipt["task3_run_manifest_sha256"],
            EXPECTED_TASK3_MANIFEST_SHA256,
        )

        transfer_path = self.task3_root / "TASK3_TRANSFER_RECEIPT.json"
        transfer = json.loads(transfer_path.read_text(encoding="utf-8"))
        transferred = {row["path"]: row for row in transfer["files"]}
        for group, (source_path, _, _) in TASK3_GROUPS.items():
            if group in ("positive", "exact_data_sync_mutant"):
                continue
            row = transferred[source_path]
            source = self.repo / source_path
            self.assertEqual(source.stat().st_size, row["bytes"])
            self.assertEqual(
                hashlib.sha256(source.read_bytes()).hexdigest().upper(),
                row["sha256"],
            )

        manifest = self.task3_evidence / "TASK3_RUN_MANIFEST.sha256"
        self.assertEqual(
            hashlib.sha256(manifest.read_bytes()).hexdigest().upper(),
            EXPECTED_TASK3_MANIFEST_SHA256,
        )
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1)
            artifact = self.task3_root / relative
            self.assertTrue(artifact.is_file(), f"missing manifest artifact {artifact}")
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), digest)

    def test_task3_locked_receipts_and_raw_diagnostics(self) -> None:
        evidence = self.task3_evidence
        self.assertTrue(evidence.is_dir(), f"missing {evidence}")
        for group, (source_path, theorems, expected_exit) in TASK3_GROUPS.items():
            with self.subTest(group=group):
                receipt = json.loads(
                    (evidence / f"{group}.receipt.json").read_text(encoding="utf-8")
                )
                stdout = (evidence / f"{group}.stdout.log").read_text(
                    encoding="utf-8"
                )
                stderr_path = evidence / f"{group}.stderr.log"
                exit_path = evidence / f"{group}.exit"
                audit_path = evidence / f"{group}.audit.log"
                stderr = stderr_path.read_text(encoding="utf-8")
                exit_text = exit_path.read_text(encoding="utf-8")
                self.assertEqual(
                    receipt["schema"], "smooth4pc_t73_task3_run_receipt/v2"
                )
                self.assertEqual(receipt["exit_code"], expected_exit)
                self.assertEqual(receipt["verdict"], "PASS")
                self.assertTrue(receipt["acquire_utc"].endswith("Z"))
                self.assertTrue(receipt["release_utc"].endswith("Z"))
                self.assertIn(".locked_lake.lock", receipt["lockdir"])
                self.assertTrue(receipt["git_path"].endswith("/no-git-bin/git"))
                self.assertIn(source_path, receipt["command"])
                self.assertEqual(int(exit_text.strip()), expected_exit)
                self.assertEqual(stderr, "")
                for key, path in {
                    "stdout": evidence / f"{group}.stdout.log",
                    "stderr": stderr_path,
                    "exit": exit_path,
                    "audit": audit_path,
                }.items():
                    self.assertEqual(
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                        receipt["evidence_sha256"][key],
                    )

                if theorems is None:
                    self.assertEqual(stdout, "")
                    self.assertEqual(receipt["expected"], "exit 0")
                    continue

                self.assertEqual(receipt["theorems"], list(theorems))
                self.assertEqual(receipt["unsolved_proposition"], "False")
                self.assertEqual(receipt["false_red_scan"], "PASS")
                self.assertEqual(stdout.count("error: unsolved goals"), len(theorems))
                self.assertEqual(stdout.count("⊢ False"), len(theorems))
                for diagnostic_line in receipt["diagnostic_lines"]:
                    self.assertRegex(
                        stdout,
                        re.compile(
                            rf"(?m)^{re.escape(source_path)}:{diagnostic_line}:\d+: "
                            r"error: unsolved goals$"
                        ),
                    )
                self.assertNotRegex(
                    stdout.lower(),
                    r"unknown module|no such file|not found|parse error|unexpected token",
                )
                if group == "exact_data_sync_mutant":
                    attack = receipt["isolated_attack"]
                    self.assertEqual(attack["determinants"], [1, 1, 1])
                    self.assertEqual(attack["matrix_a_entry_0_1"], 269)
                    self.assertEqual(
                        attack["main_certificate_sha256_after"],
                        attack["main_certificate_sha256_before"],
                    )
                    self.assertEqual(
                        attack["audit_sha256"],
                        "85e1a7cbd1eea56ccf24aa6136e5f90503fa1089e18aa48bcbe6fa3438768d37",
                    )

    def test_mutant_fixture_set_and_named_failure_theorems(self) -> None:
        expected = {
            "transpose_mutant.lean": "transposeMutant_rowMajorEntry_should_fail",
            "entry_mutant.lean": "entryMutant_det_should_fail",
            "det_implementation_mutant.lean": "detImplementationMutant_should_fail",
            "value_mutant.lean": "valueMutant_h3_should_fail",
            "degree_mutant.lean": "degreeMutant_494_should_fail",
        }
        actual = {path.name for path in self.fixture_dir.glob("*.lean")}
        self.assertEqual(actual, set(expected))
        for filename, theorem in expected.items():
            text = (self.fixture_dir / filename).read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^theorem {re.escape(theorem)}\b")
            self.assertNotIn("Task5", text)
            self.assertNotIn("sync mutant", text.lower())

    def test_mutants_change_the_intended_axis(self) -> None:
        transpose = (self.fixture_dir / "transpose_mutant.lean").read_text(
            encoding="utf-8"
        )
        entry = (self.fixture_dir / "entry_mutant.lean").read_text(encoding="utf-8")
        determinant = (
            self.fixture_dir / "det_implementation_mutant.lean"
        ).read_text(encoding="utf-8")
        value = (self.fixture_dir / "value_mutant.lean").read_text(encoding="utf-8")
        degree = (self.fixture_dir / "degree_mutant.lean").read_text(encoding="utf-8")
        self.assertIn("[[0, 0, 1], [269, 41, 0], [1240, 189, 32]]", transpose)
        self.assertIn("[[0, 269, 1241]", entry)
        self.assertIn("+ b * (d * i - f * g)", determinant)
        self.assertIn("-59071", value)
        self.assertIn("[0, 493]", degree)


if __name__ == "__main__":
    unittest.main()
