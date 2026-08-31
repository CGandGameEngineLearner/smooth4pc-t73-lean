from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "smooth4pc_t73_proof_dependency_manifest/v1"
EXPECTED_OVERALL_STATUS = "CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW"
DESIGN_SOURCE = [
    "docs/superpowers/specs/2026-08-31-t73-counterexample-proof-consolidation-design.md#proof-normal-form"
]
ENTRY_FIELDS = {"status", "lean_role", "source_paths", "claim", "consumers"}
CONSUMER_PATTERN = re.compile(r"proof_section:[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def dependency(
    status: str,
    lean_role: str,
    source_paths: list[str],
    claim: str,
    consumer: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "lean_role": lean_role,
        "source_paths": source_paths,
        "claim": claim,
        "consumers": [consumer],
    }


EXPECTED_ENTRIES = {
    "balanced_hattori_equivalence": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "The balanced Hattori cut identifies the coefficient space with the two-sided boundary Hom-space and 227 separate Frobenius-algebra circle factors.",
        "proof_section:balanced-hattori-coefficient",
    ),
    "actual_diagonal_class": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "The inverse balanced equivalence sends the identity on BT with 227 separate X labels to the typed class v_T in M_R(T,T).",
        "proof_section:actual-diagonal-class",
    ),
    "nu0_binding": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "On the fixed one-handle source, the mandatory endpoint defect is relative nu zero; dotted maps preserve that head and undotted maps raise it.",
        "proof_section:relative-nu-ledger",
    ),
    "point_push_cubic": dependency(
        "finite_verified",
        "derived_theorem",
        [
            "data/GLOBAL_FALSIFICATION_CHAIN_CERT.json",
            "Smooth4PC/CertificateData.lean",
            "AuditArithmetic.lean",
        ],
        "The exact point-push calculation evaluates the cubic row on the transported cup vector as -59072, which is nonzero.",
        "proof_section:point-push-cubic",
    ),
    "beta_psi_cocone": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "The Reynolds-counit row annihilates the beta and undotted psi relations and agrees across every dotted psi relation on the whole source.",
        "proof_section:beta-psi-cocone",
    ),
    "fixed_y_hj_basis": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "A single fixed partial W2 contains a pairwise-disjoint determinant-one HJ sphere basis with the required framed owner-point identifications.",
        "proof_section:fixed-y-hj-basis",
    ),
    "direct_q_sphere_cocone": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "Vertex-potential direct-Q equivalences conjugate every signed sphere edge to the canonical split tree, giving the undotted-zero and dotted-identity cocone equations on the whole source.",
        "proof_section:direct-q-sphere-cocone",
    ),
    "phi_w_naturality": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "The changing-endpoint Phi comparison and W conjugation squares commute for every source vector and induce the corresponding cubic K square.",
        "proof_section:changing-endpoint-naturality",
    ),
    "bpw_vertical_horizontal_trace": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "The BPW vertical-to-horizontal trace with 227 counits carries the balanced diagonal class to the actual cup vector in the fixed one-handle source.",
        "proof_section:vertical-horizontal-trace",
    ),
    "bhpw_strict_functoriality": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "Strict BHPW functoriality identifies the required composed cobordism maps without an unresolved projective sign or scalar.",
        "proof_section:strict-functoriality",
    ),
    "mww_handle_core_formulas": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "The MWW handle formulas and core-attachment diagram give the complete beta, psi, and three-handle relation sources and their quotient universal properties.",
        "proof_section:mww-quotient",
    ),
    "four_handle_isomorphism": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "The MWW four-handle map is an absolute-bigrading-preserving isomorphism and transports the surviving degree-494 class.",
        "proof_section:four-handle-comparison",
    ),
    "s4_bigraded_control": dependency(
        "external_theorem",
        "explicit_parameter",
        DESIGN_SOURCE,
        "The standard four-sphere module over the rationals is one-dimensional in bidegree (0,0) and vanishes in every nonzero quantum degree.",
        "proof_section:standard-s4-control",
    ),
}
EXPECTED_INVARIANTS = {
    "input": "v_T, not xi",
    "balanced_coefficient": "M_R(T,T') = Hom(BT,BT') tensor A^(tensor 227)",
    "source": "M_1(88)",
    "relative_nu": 0,
    "cubic_value": -59072,
    "final_q": 494,
    "edge_braid_model": "vertex_potential_conjugation",
}


def markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            slug = re.sub(r"[^\w\s-]", "", match.group(1).lower())
            anchors.add(re.sub(r"\s+", "-", slug.strip()))
    return anchors


def validate_source_reference(repo: Path, reference: str) -> None:
    relative, separator, anchor = reference.partition("#")
    if "://" in relative or Path(relative).is_absolute():
        raise ValueError(f"source path is not repo-local: {reference}")
    resolved_repo = repo.resolve()
    resolved = (resolved_repo / relative).resolve()
    if not resolved.is_relative_to(resolved_repo) or not resolved.is_file():
        raise ValueError(f"source path does not exist: {reference}")
    if separator and (not anchor or anchor not in markdown_anchors(resolved)):
        raise ValueError(f"source anchor does not exist: {reference}")


def validate_manifest(manifest: dict[str, Any], repo: Path) -> None:
    expected_root_fields = {"schema", "overall_status", "invariants", "dependencies"}
    if set(manifest) != expected_root_fields:
        raise ValueError("manifest root fields do not match the frozen schema")
    if manifest["schema"] != EXPECTED_SCHEMA:
        raise ValueError("unexpected manifest schema")
    if manifest["overall_status"] != EXPECTED_OVERALL_STATUS:
        raise ValueError("the dependency ledger cannot claim formal or external acceptance")
    if manifest["invariants"] != EXPECTED_INVARIANTS:
        raise ValueError("a frozen T73 invariant was changed")

    entries = manifest["dependencies"]
    if not isinstance(entries, dict) or set(entries) != set(EXPECTED_ENTRIES):
        raise ValueError("dependency names do not match the frozen proof ledger")
    for name, entry in entries.items():
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
            raise ValueError(f"{name}: entry fields do not match the frozen schema")
        if not isinstance(entry["source_paths"], list) or not entry["source_paths"]:
            raise ValueError(f"{name}: source_paths must be a nonempty array")
        for source in entry["source_paths"]:
            if not isinstance(source, str) or not source:
                raise ValueError(f"{name}: source path must be a nonempty string")
            validate_source_reference(repo, source)
        consumers = entry["consumers"]
        if not isinstance(consumers, list) or not consumers:
            raise ValueError(f"{name}: consumers must be a nonempty array")
        if not all(isinstance(value, str) and CONSUMER_PATTERN.fullmatch(value) for value in consumers):
            raise ValueError(f"{name}: consumer must be a logical proof_section ID")
        if entry != EXPECTED_ENTRIES[name]:
            raise ValueError(f"{name}: entry mapping differs from the frozen contract")


class T73ProofDependencyManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.manifest_path = cls.repo / "audit" / "t73_proof_dependency_manifest.json"

    def load_manifest(self) -> dict[str, Any]:
        self.assertTrue(self.manifest_path.is_file(), f"missing {self.manifest_path}")
        loaded = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertIsInstance(loaded, dict)
        return loaded

    def test_manifest_matches_exact_dependency_contract(self) -> None:
        validate_manifest(self.load_manifest(), self.repo)

    def test_semantic_entry_mutants_are_rejected(self) -> None:
        manifest = self.load_manifest()
        mutations = {
            "status": ("balanced_hattori_equivalence", "status", "finite_verified"),
            "lean_role": ("balanced_hattori_equivalence", "lean_role", "none"),
            "claim": ("point_push_cubic", "claim", "A weakened cubic claim."),
            "source": ("point_push_cubic", "source_paths", ["README.md"]),
            "consumer": (
                "point_push_cubic",
                "consumers",
                ["proof_section:wrong-but-valid"],
            ),
        }
        for label, (name, field, value) in mutations.items():
            with self.subTest(mutant=label):
                mutant = copy.deepcopy(manifest)
                mutant["dependencies"][name][field] = value
                with self.assertRaisesRegex(ValueError, "entry mapping"):
                    validate_manifest(mutant, self.repo)

    def test_invalid_source_path_and_anchor_are_rejected(self) -> None:
        manifest = self.load_manifest()
        for source, message in (
            ("docs/missing.md", "source path does not exist"),
            (f"{DESIGN_SOURCE[0].split('#')[0]}#missing-anchor", "source anchor does not exist"),
        ):
            with self.subTest(source=source):
                mutant = copy.deepcopy(manifest)
                mutant["dependencies"]["balanced_hattori_equivalence"]["source_paths"] = [source]
                with self.assertRaisesRegex(ValueError, message):
                    validate_manifest(mutant, self.repo)

    def test_file_path_consumer_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.load_manifest())
        mutant["dependencies"]["actual_diagonal_class"]["consumers"] = [
            "docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md#actual-diagonal-class"
        ]
        with self.assertRaisesRegex(ValueError, "logical proof_section ID"):
            validate_manifest(mutant, self.repo)

    def test_forbidden_invariant_substitutions_are_rejected(self) -> None:
        manifest = self.load_manifest()
        mutations = {
            "one_sided_hom": ("balanced_coefficient", "M_R(T,T') = Hom(T,BT) tensor A^(tensor 227)"),
            "wrong_input": ("input", "xi"),
            "wrong_source": ("source", "M_0(88)"),
            "retired_cubic": ("cubic_value", -28864),
            "path_dependent_braid": ("edge_braid_model", "path-dependent edge braid"),
        }
        for label, (field, value) in mutations.items():
            with self.subTest(mutant=label):
                mutant = copy.deepcopy(manifest)
                mutant["invariants"][field] = value
                with self.assertRaisesRegex(ValueError, "frozen T73 invariant"):
                    validate_manifest(mutant, self.repo)

    def test_formal_or_external_acceptance_status_is_rejected(self) -> None:
        manifest = self.load_manifest()
        for status in ("FORMALLY_VERIFIED_COUNTEREXAMPLE", "EXTERNALLY_ACCEPTED"):
            with self.subTest(status=status):
                mutant = copy.deepcopy(manifest)
                mutant["overall_status"] = status
                with self.assertRaisesRegex(ValueError, "formal or external acceptance"):
                    validate_manifest(mutant, self.repo)


if __name__ == "__main__":
    unittest.main()
