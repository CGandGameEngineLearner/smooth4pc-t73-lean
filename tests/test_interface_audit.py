from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPECTED_INTERFACE_FIELDS = {
    "AuditUniverse": (
        "Manifold",
        "G",
        "candidate",
        "S4",
        "IsHomotopySphere",
        "Diffeomorphic",
        "SphereDatum",
        "IsEmbedded",
        "PairwiseDisjoint",
        "IsClassCoordinate",
        "IsActualHH0",
        "IsActualCapAtOrder",
        "IsActualBetaRelation",
        "IsActualPsiRelation",
        "IsActualSphereMap",
        "IsHJReplacement",
        "IsActualMWWCoequalizer",
        "IsActualMWWTransport",
        "IsActualFourHandle",
    ),
    "OneHandleInterface": (
        "HHRaw",
        "hh0Relation",
        "hh0Quotient",
        "hh0Binding",
        "hh0Kernel",
        "hh0Lift",
        "hh0LiftCommutes",
        "hh0LiftUnique",
        "chosenRaw",
        "chosenClass",
        "chosenBinding",
        "traceAnomalyOrder",
        "traceAnomalyOrderEq",
        "rawCap",
        "rawCapBinding",
        "rawCapKillsHH0",
        "rawCapChosen",
    ),
    "BetaPsiInterface": (
        "Level",
        "betaSource",
        "betaRelation",
        "betaRelationBinding",
        "betaRelationEquation",
        "psi0Source",
        "psi0Relation",
        "psi0Binding",
        "psi0Equation",
        "psi1Source",
        "psi1Relation",
        "psi1Binding",
        "psi1Equation",
        "R01GeneratorSet",
        "R01GeneratorSet_eq",
        "R01",
        "R01_eq_span",
        "q01",
        "q01Kernel",
        "quotientLift",
        "quotientLiftCommutes",
        "quotientLiftUnique",
    ),
    "SphereLocalInterface": (
        "Source",
        "sphere",
        "embedded",
        "classCoordinate",
        "classBinding",
        "sigma0",
        "sigma0Binding",
        "sigma0Equation",
        "sigma1MinusId",
        "sigma1MinusIdBinding",
        "sigma1MinusIdEquation",
    ),
    "SphereMWWFamily": (
        "th1",
        "th2",
        "thxy",
        "pairwiseDisjoint",
        "hjBinding",
        "R12GeneratorSet",
        "R12GeneratorSet_eq",
        "R12",
        "R12_eq_span",
        "q12",
        "q12Kernel",
        "quotientLift",
        "quotientLiftCommutes",
        "quotientLiftUnique",
        "mwwCoequalizerBinding",
        "mwwTransport",
        "transportBinding",
    ),
    "FourHandleInterface": ("fourIso", "fourHandleBinding"),
    "S4ControlInterface": ("degreeSupport",),
    "DiffeomorphismInvarianceInterface": ("preservesGradedObject",),
    "NotStandardInterfaces": (
        "oneHandle",
        "betaPsi",
        "sphereMWW",
        "fourHandle",
        "s4Control",
        "diffeomorphismInvariance",
    ),
    "CappellShanesonInterface": ("matrixConditionsToHomotopySphere",),
}

EXPECTED_SIGNATURES = (
    "Smooth4PC.conditionalNotStandardSignature",
    "Smooth4PC.conditionalIsHomotopySphereSignature",
    "Smooth4PC.conditionalCounterexampleSignature",
)


class InterfaceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.interfaces = cls.repo / "Smooth4PC" / "Interfaces.lean"
        cls.audit_type = cls.repo / "AuditType.lean"
        cls.manifest = cls.repo / "audit" / "interface_manifest.json"
        cls.type_dump = cls.repo / "audit" / "lean_type_dump.txt"
        cls.type_auditor = cls.repo / "scripts" / "audit_theorem_type.py"
        cls.declaration_auditor = cls.repo / "scripts" / "audit_declarations.py"
        cls.receipt_verifier = cls.repo / "scripts" / "verify_task4_receipt.py"
        cls.receipt = cls.repo / "evidence" / "task4" / "TASK4_REMOTE_RECEIPT.json"
        cls.remote_audit_log = cls.repo / "evidence" / "task4" / "LOCKED_LAKE_AUDIT.log"
        cls.gitattributes = cls.repo / ".gitattributes"

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

    def load_manifest(self) -> dict[str, object]:
        self.assertTrue(self.manifest.is_file(), f"missing {self.manifest}")
        return json.loads(self.manifest.read_text(encoding="utf-8"))

    @staticmethod
    def dump_from_manifest(manifest: dict[str, object]) -> str:
        declarations = manifest["declarations"]
        assert isinstance(declarations, list)
        lines = []
        for entry in declarations:
            lines.append(f"AUDIT_TYPE|{entry['declaration']}|{entry['normalized_type']}")
            if "normalized_body" in entry:
                lines.append(f"AUDIT_BODY|{entry['declaration']}|{entry['normalized_body']}")
        for interface_name, fields in manifest["interfaces"].items():
            for entry in fields:
                lines.append(
                    f"AUDIT_FIELD|Smooth4PC.{interface_name}.{entry['name']}|{entry['normalized_type']}"
                )
        return "\n".join(lines) + "\n"

    def test_required_task4_files_exist(self) -> None:
        for path in (
            self.interfaces,
            self.audit_type,
            self.manifest,
            self.type_auditor,
            self.declaration_auditor,
            self.receipt_verifier,
            self.receipt,
            self.remote_audit_log,
            self.gitattributes,
        ):
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_task4_evidence_line_endings_are_pinned_to_lf(self) -> None:
        attributes = self.gitattributes.read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attributes)
        self.assertIn("data/GLOBAL_FALSIFICATION_CHAIN_CERT.json binary", attributes)
        self.assertIn("evidence/task3/** binary", attributes)
        self.assertIn("audit/lean_type_dump.txt text eol=lf", attributes)
        self.assertIn("audit/interface_manifest.json text eol=lf", attributes)
        self.assertIn("evidence/task4/*.json text eol=lf", attributes)
        self.assertIn("evidence/task4/*.log text eol=lf", attributes)
        for path in (
            self.type_dump,
            self.manifest,
            self.interfaces,
            self.audit_type,
            self.type_auditor,
            self.declaration_auditor,
            self.receipt_verifier,
            self.receipt,
            self.remote_audit_log,
            Path(__file__),
        ):
            self.assertNotIn(b"\r\n", path.read_bytes(), str(path))
        self.assertIn('newline="\\n"', self.type_auditor.read_text(encoding="utf-8"))

    def test_task4_receipt_binds_sources_auditors_and_remote_dump(self) -> None:
        result = self.run_script(
            self.receipt_verifier,
            "--root",
            self.repo,
            "--receipt",
            self.receipt,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("task4 receipt gate: PASS", result.stdout)
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(receipt["epistemic_status"], "INTERFACE_SURFACE_FROZEN_ONLY")
        required = {
            ".gitattributes",
            "Smooth4PC/CertificateData.lean",
            "Smooth4PC/Arithmetic.lean",
            "data/GLOBAL_FALSIFICATION_CHAIN_CERT.json",
            "evidence/task4/LOCKED_LAKE_AUDIT.log",
            "Smooth4PC/Interfaces.lean",
            "AuditType.lean",
            "audit/interface_manifest.json",
            "audit/lean_type_dump.txt",
            "scripts/audit_declarations.py",
            "scripts/audit_theorem_type.py",
            "scripts/verify_task4_receipt.py",
            "tests/test_interface_audit.py",
            "lakefile.toml",
            "lean-toolchain",
            "scripts/locked_lake.sh",
        }
        self.assertEqual(set(receipt["files"]), required)
        self.assertEqual(receipt["remote_runs"]["interfaces_exit"], 0)
        self.assertEqual(receipt["remote_runs"]["audit_type_exit"], 0)

    def test_task4_receipt_gate_rejects_tampered_hash(self) -> None:
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        receipt["files"]["Smooth4PC/Interfaces.lean"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp:
            mutant = Path(tmp) / "TASK4_REMOTE_RECEIPT.json"
            mutant.write_text(
                json.dumps(receipt, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            result = self.run_script(
                self.receipt_verifier,
                "--root",
                self.repo,
                "--receipt",
                mutant,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("task4 receipt gate: FAIL", result.stderr)

    def test_manifest_freezes_exact_remote_lean_projection_surface(self) -> None:
        manifest = self.load_manifest()
        self.assertEqual(manifest["format"], 3)
        self.assertIn("interfaces", manifest)
        self.assertIn("declarations", manifest)
        self.assertIn("signature_bodies", manifest)
        self.assertEqual(
            set(manifest["signature_bodies"]),
            {entry["declaration"] for entry in manifest["declarations"]},
        )
        self.assertEqual(set(manifest["interfaces"]), set(EXPECTED_INTERFACE_FIELDS))
        for interface_name, expected_fields in EXPECTED_INTERFACE_FIELDS.items():
            self.assertEqual(
                tuple(entry["name"] for entry in manifest["interfaces"][interface_name]),
                expected_fields,
            )
        self.assertTrue(self.type_dump.is_file())
        self.assertEqual(
            hashlib.sha256(self.type_dump.read_bytes()).hexdigest().upper(),
            manifest["lean_dump_sha256"],
        )
        for entry in manifest["declarations"]:
            self.assertIn("normalized_type", entry)
            self.assertIn("normalized_body", entry)

    def test_manifest_freezes_three_standalone_signatures_and_cs_separation(self) -> None:
        manifest = self.load_manifest()
        signatures = manifest["signature_bodies"]
        self.assertEqual(tuple(signatures), EXPECTED_SIGNATURES)
        not_standard = signatures["Smooth4PC.conditionalNotStandardSignature"]
        self.assertNotIn("CappellShanesonInterface", not_standard)
        self.assertIn("NotStandardInterfaces", not_standard)
        self.assertIn("-> ¬ u.Diffeomorphic u.candidate u.S4", not_standard)
        self.assertIn(
            "CappellShanesonInterface",
            signatures["Smooth4PC.conditionalIsHomotopySphereSignature"],
        )
        self.assertIn(
            "CappellShanesonInterface",
            signatures["Smooth4PC.conditionalCounterexampleSignature"],
        )
        declarations = manifest["declarations"]
        self.assertTrue(all("normalized_body" in entry for entry in declarations))
        body = {
            entry["declaration"]: entry["normalized_body"]
            for entry in declarations
        }
        reviewed_body = {
            entry["declaration"]: entry["reviewed_body"]
            for entry in declarations
        }
        self.assertEqual(
            reviewed_body["Smooth4PC.conditionalNotStandardSignature"],
            "Smooth4PC.NotStandardInterfaces u W0 W1 W2 W3 -> ¬ u.Diffeomorphic u.candidate u.S4",
        )
        self.assertIn(
            "Smooth4PC.NotStandardInterfaces",
            body["Smooth4PC.conditionalNotStandardSignature"],
        )
        self.assertIn(
            "Smooth4PC.AuditUniverse.Diffeomorphic",
            body["Smooth4PC.conditionalNotStandardSignature"],
        )
        self.assertNotIn(
            "CappellShanesonInterface",
            body["Smooth4PC.conditionalNotStandardSignature"],
        )

    def test_type_auditor_accepts_exact_manifest_dump(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "type_dump.txt"
            dump.write_bytes(self.type_dump.read_bytes())
            before = self.manifest.read_bytes()
            result = self.run_script(
                self.type_auditor,
                "--manifest",
                self.manifest,
                "--dump",
                dump,
            )
            after = self.manifest.read_bytes()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("theorem-type gate: PASS", result.stdout)
        self.assertEqual(after, before)

    def test_type_auditor_rejects_frozen_dump_sha_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "lean_type_dump.txt"
            dump.write_bytes(self.type_dump.read_bytes() + b"\n")
            result = self.run_script(
                self.type_auditor,
                "--manifest",
                self.manifest,
                "--dump",
                dump,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dump SHA-256 mismatch", result.stderr)

    def test_default_type_dump_never_overwrites_frozen_evidence(self) -> None:
        source = self.type_auditor.read_text(encoding="utf-8")
        self.assertNotIn('args.root / "audit" / "lean_type_dump.txt"', source)
        self.assertIn('args.root / ".lake" / "build" / "audit"', source)

    def test_type_auditor_rejects_hidden_and_signature_parameter_mutants(self) -> None:
        manifest = self.load_manifest()
        exact_dump = self.dump_from_manifest(manifest)
        target = "Smooth4PC.conditionalNotStandardSignature"
        exact_type = next(
            entry["normalized_type"]
            for entry in manifest["declarations"]
            if entry["declaration"] == target
        )
        exact_body = next(
            entry["normalized_body"]
            for entry in manifest["declarations"]
            if entry["declaration"] == target
        )
        mutants = {
            "implicit": exact_type + " -> {hidden : Prop}",
            "typeclass": exact_type + " -> [Nonempty u.Manifold]",
            "extra_parameter": exact_type + " -> (extra : Prop)",
            "missing_parameter": exact_type.replace(
                "(W0 W1 W2 W3 : Smooth4PC.QMod)",
                "(W0 W1 W2 : Smooth4PC.QMod)",
                1,
            ),
            "body_true": ("body", "True"),
        }
        for mutant_name, mutant in mutants.items():
            with self.subTest(mutant=mutant_name), tempfile.TemporaryDirectory() as tmp:
                dump = Path(tmp) / "type_dump.txt"
                if isinstance(mutant, tuple):
                    _, mutant_body = mutant
                    mutated = exact_dump.replace(
                        f"AUDIT_BODY|{target}|{exact_body}",
                        f"AUDIT_BODY|{target}|{mutant_body}",
                    )
                else:
                    mutated = exact_dump.replace(
                        f"AUDIT_TYPE|{target}|{exact_type}",
                        f"AUDIT_TYPE|{target}|{mutant}",
                    )
                self.assertNotEqual(mutated, exact_dump)
                dump.write_text(mutated, encoding="utf-8", newline="\n")
                mutant_manifest = json.loads(json.dumps(manifest))
                mutant_manifest["lean_dump_sha256"] = hashlib.sha256(
                    dump.read_bytes()
                ).hexdigest().upper()
                mutant_manifest_path = Path(tmp) / "interface_manifest.json"
                mutant_manifest_path.write_text(
                    json.dumps(mutant_manifest, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                result = self.run_script(
                    self.type_auditor,
                    "--manifest",
                    mutant_manifest_path,
                    "--dump",
                    dump,
                )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("theorem-type gate: FAIL", result.stderr)
            self.assertNotIn("dump SHA-256 mismatch", result.stderr)

    def test_declaration_auditor_accepts_task4_sources(self) -> None:
        result = self.run_script(
            self.declaration_auditor,
            "--root",
            self.repo,
            "--source",
            self.interfaces.relative_to(self.repo),
            "--source",
            self.audit_type.relative_to(self.repo),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("declaration gate: PASS", result.stdout)
        self.assertIn("interface-field gate: PASS", result.stdout)

    def test_declaration_auditor_rejects_imported_axiom_mutant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ImportedShortcut.lean").write_text(
                "namespace Hostile\naxiom importedShortcut : False\nend Hostile\n",
                encoding="utf-8",
            )
            result = self.run_script(self.declaration_auditor, "--root", root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("declaration gate: FAIL", result.stderr)
        self.assertIn("axiom", result.stderr)

    def test_declaration_auditor_rejects_alias_false_mutant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AliasFalse.lean").write_text(
                "abbrev HiddenConclusion := False\n"
                "structure Hostile where\n"
                "  broad : HiddenConclusion\n",
                encoding="utf-8",
            )
            result = self.run_script(self.declaration_auditor, "--root", root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("interface-field gate: FAIL", result.stderr)

    def test_declaration_auditor_rejects_broad_conclusion_field_mutant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "BroadConclusion.lean").write_text(
                "structure BroadConclusion where\n"
                "  broadConclusion : False\n",
                encoding="utf-8",
            )
            result = self.run_script(self.declaration_auditor, "--root", root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("interface-field gate: FAIL", result.stderr)

    def test_declaration_auditor_rejects_multiline_and_specialized_conclusion_fields(self) -> None:
        mutants = {
            "multiline_false": (
                "structure BroadConclusion where\n"
                "  broadConclusion :\n"
                "    False\n"
            ),
            "specialized_diffeomorphic": (
                "structure Shortcut (Diffeomorphic : Nat -> Nat -> Prop) where\n"
                "  shortcut : Diffeomorphic 0 1 -> 0 = 1\n"
            ),
        }
        for name, source in mutants.items():
            with self.subTest(mutant=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "BroadConclusion.lean").write_text(source, encoding="utf-8")
                result = self.run_script(self.declaration_auditor, "--root", root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("interface-field gate: FAIL", result.stderr)

    def test_declaration_auditor_rejects_all_forbidden_forms(self) -> None:
        forms = {
            "constant": "constant illicit : Nat",
            "opaque": "opaque illicit : Nat := 0",
            "unsafe": "unsafe def illicit : Nat := 0",
            "extern": "@[extern \"illicit\"] opaque illicit : Nat",
            "implemented_by": "@[implemented_by illicit] def target : Nat := 0",
            "run_tac": "example : True := by run_tac pure ()",
            "sorry": "example : True := by sorry",
            "sorryAx": "#check sorryAx",
            "admit": "example : True := by admit",
            "native_decide": "example : True := by native_decide",
            "ofReduceBool": "#check Lean.ofReduceBool",
        }
        for form_name, source in forms.items():
            with self.subTest(form=form_name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "Hostile.lean").write_text(source + "\n", encoding="utf-8")
                result = self.run_script(self.declaration_auditor, "--root", root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("declaration gate: FAIL", result.stderr)

    def test_audit_type_uses_lean_meta_and_lists_every_manifest_declaration(self) -> None:
        manifest = self.load_manifest()
        source = self.audit_type.read_text(encoding="utf-8")
        self.assertIn("getConstInfo", source)
        self.assertIn("ppExpr", source)
        self.assertIn("AUDIT_TYPE|", source)
        self.assertIn("AUDIT_BODY|", source)
        self.assertIn("AUDIT_FIELD|", source)
        self.assertIn("Smooth4PC.AuditUniverse", source)
        for entry in manifest["declarations"]:
            self.assertIn(entry["declaration"], source)
        self.assertNotIn("unused field", source.lower())

    def test_interfaces_keep_real_geometric_obligations_narrow_and_nontrivial(self) -> None:
        source = self.interfaces.read_text(encoding="utf-8")
        self.assertIn("G : Manifold → ℤ → QMod", source)
        self.assertIn("inductive PsiRelationKind where", source)
        self.assertIn("| psi0", source)
        self.assertIn("| psi1", source)
        self.assertIn("inductive SphereMapKind where", source)
        self.assertIn("| sigma0", source)
        self.assertIn("| sigma1MinusId", source)
        self.assertIn("IsActualHH0", source)
        self.assertIn("IsActualCapAtOrder", source)
        self.assertIn("PairwiseDisjoint : SphereDatum → SphereDatum → SphereDatum → Prop", source)
        self.assertIn("IsHJReplacement : SphereDatum → SphereDatum → SphereDatum → Prop", source)
        self.assertIn("rawCap : HHRaw →ₗ[ℚ] ℚ", source)
        self.assertIn("rawCapBinding : u.IsActualCapAtOrder traceAnomalyOrder rawCap", source)
        self.assertIn("rawCapKillsHH0", source)
        self.assertIn("rawCapChosen : rawCap chosenRaw = (2624 : ℚ)", source)
        self.assertIn("traceAnomalyOrderEq : traceAnomalyOrder = 3", source)
        self.assertIn("IsActualBetaRelation : ∀ {Level : Type} {Source W0 : QMod}, Level → (Source →ₗ[ℚ] W0) → Prop", source)
        self.assertIn("IsActualPsiRelation : ∀ {Source W0 : QMod}, PsiRelationKind → (Source →ₗ[ℚ] W0) → Prop", source)
        self.assertIn("IsActualSphereMap : ∀ {Source W1 : QMod}, SphereMapKind → SphereDatum → (Source →ₗ[ℚ] W1) → Prop", source)
        self.assertIn("IsActualMWWTransport : ∀ {W2 W3 : QMod}, (W2 ≃ₗ[ℚ] W3) → Prop", source)
        self.assertIn("IsActualFourHandle : ∀ {W3 : QMod}, (W3 ≃ₗ[ℚ] G candidate 494) → Prop", source)
        self.assertIn("structure BetaPsiInterface (u : AuditUniverse) (W0 W1 : QMod) (ell0 : W0 →ₗ[ℚ] ℚ)", source)
        self.assertNotIn("R01_le_ker", source)
        self.assertNotIn("R12_le_ker", source)
        self.assertIn("R01GeneratorSet_eq", source)
        self.assertIn("R01_eq_span : R01 = Submodule.span ℚ R01GeneratorSet", source)
        self.assertIn("Set.iUnion fun level : Level", source)
        self.assertIn("betaRelationBinding : ∀ level : Level, u.IsActualBetaRelation level (betaRelation level)", source)
        self.assertIn("ell0.comp (betaRelation level) = 0", source)
        self.assertIn("psi0Binding : u.IsActualPsiRelation PsiRelationKind.psi0 psi0Relation", source)
        self.assertIn("psi1Binding : u.IsActualPsiRelation PsiRelationKind.psi1 psi1Relation", source)
        self.assertIn("ell0.comp psi0Relation = 0", source)
        self.assertIn("ell0.comp psi1Relation = 0", source)
        self.assertIn("q01 : W0 →ₗ[ℚ] W1", source)
        self.assertIn("ell0.comp oneHandle.hh0Quotient = oneHandle.rawCap", source)
        self.assertIn("BetaPsiInterface u W0 W1 ell0", source)
        self.assertIn("sphereMWW : ∀ ell0 : W0 →ₗ[ℚ] ℚ,", source)
        self.assertIn("(h0 : ell0.comp oneHandle.hh0Quotient = oneHandle.rawCap)", source)
        self.assertIn("ell1.comp (betaPsi ell0 h0).q01 = ell0", source)
        self.assertIn("structure SphereLocalInterface (u : AuditUniverse) (W1 : QMod) (ell1 : W1 →ₗ[ℚ] ℚ)", source)
        self.assertIn("sigma0 : Source →ₗ[ℚ] W1", source)
        self.assertIn("sigma1MinusId : Source →ₗ[ℚ] W1", source)
        self.assertIn("sigma0Binding : u.IsActualSphereMap SphereMapKind.sigma0 sphere sigma0", source)
        self.assertIn("sigma1MinusIdBinding : u.IsActualSphereMap SphereMapKind.sigma1MinusId sphere sigma1MinusId", source)
        self.assertIn("sigma0Equation : ell1.comp sigma0 = 0", source)
        self.assertIn("sigma1MinusIdEquation : ell1.comp sigma1MinusId = 0", source)
        self.assertIn("R12GeneratorSet_eq", source)
        self.assertIn("R12_eq_span : R12 = Submodule.span ℚ R12GeneratorSet", source)
        self.assertIn("q12 : W1 →ₗ[ℚ] W2", source)
        self.assertIn("pairwiseDisjoint : u.PairwiseDisjoint th1.sphere th2.sphere thxy.sphere", source)
        self.assertIn("hjBinding : u.IsHJReplacement th1.sphere th2.sphere thxy.sphere", source)
        self.assertIn("mwwCoequalizerBinding : u.IsActualMWWCoequalizer th1.sphere th2.sphere thxy.sphere q12", source)
        self.assertIn("mwwTransport : W2 ≃ₗ[ℚ] W3", source)
        self.assertIn("transportBinding : u.IsActualMWWTransport mwwTransport", source)
        self.assertIn("fourIso : W3 ≃ₗ[ℚ] u.G u.candidate 494", source)
        self.assertIn("fourHandleBinding : u.IsActualFourHandle fourIso", source)
        self.assertNotIn("∈ LinearMap.range betaAllLevel", source)
        self.assertNotIn("∈ Set.range psi0", source)
        self.assertNotIn("localMap chosenClass ∈ LinearMap.range localMap", source)
        self.assertNotIn("mwwTransport (q12 x) ∈ LinearMap.range", source)
        self.assertIn("u.Diffeomorphic u.candidate u.S4", source)
        self.assertIn("matrixConditionsToHomotopySphere :", source)
        self.assertNotIn("matrixDetOne :", source)
        self.assertNotIn("c3Nonzero", source)
        self.assertNotIn("valueAtW3", source)
        self.assertIn("q ≠ 0 → ∀ x : u.G u.S4 q, x = 0", source)
        self.assertIn("u.Diffeomorphic left right →", source)
        self.assertIn("u.G left q ≃ₗ[ℚ] u.G right q", source)
        self.assertIn("W0 W1 W2 W3 : QMod", source)
        self.assertIn("def conditionalNotStandardSignature", source)
        self.assertIn("NotStandardInterfaces u W0 W1 W2 W3 →", source)


if __name__ == "__main__":
    unittest.main()
