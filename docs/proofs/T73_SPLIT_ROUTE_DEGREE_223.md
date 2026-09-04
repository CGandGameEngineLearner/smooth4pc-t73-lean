# Conditional propagation of the literal-split degree 223

Date: 2026-09-05

## Scope

This note assumes the relative split hypothesis of the conditional
two-representable theorem in T73_C_CHAINMAP_PAPER_PROOF.md.  It does not
assert that the required separating sphere or simultaneous ambient movie
exists.

Under that hypothesis, the normalized reduced coefficient is
\[
\widehat M_R^z(T,T')
\cong
\operatorname{Hom}_{\mathcal C_{44}}(BT,BT')
\otimes A^{\otimes227}.
\tag{1}
\]
Thus the diagonal identity labelled by \(X\) on all 227 circle factors has
quantum degree
\[
0+227=227.
\tag{2}
\]
At the selected cable state, \(N=2\), \(\alpha=0\), and \(|r|=2\), so MWW
Definition 3.1 gives the shift
\[
(1-N)(2|r|+|\alpha|)=-4.
\tag{3}
\]
The class in the two-handle cabled source therefore has absolute quantum
degree
\[
q_{\mathrm{split}}=227-4=223.
\tag{4}
\]

## Degree of the fixed-\(W\) detector

In MWW's convention
\[
\deg(1)=-1,\qquad \deg(X)=+1,\qquad
\epsilon(1)=0,\quad\epsilon(X)=1.
\]
Consequently \(\epsilon:A\to\mathbb Q\) is homogeneous of degree \(-1\),
and \(\epsilon^{\otimes227}\) has degree \(-227\).  The regular coefficient
trace, BPW vertical-to-horizontal map, oriented doubling, the chosen
degree-normalized cup and cap, and the fixed braid operator
\(\rho_h(W)-I\) all have degree zero in the corrected endpoint convention.
The parameter \(h\) is an external trace-deformation parameter of degree
zero, so taking its cubic coefficient does not change the MWW quantum
degree.

On the normalized one-handle coefficient the divided row therefore has
degree \(-227\).  Reinterpreting it on the cabled summand shifted by \(-4\)
changes its degree to
\[
-227-(-4)=-223.
\tag{5}
\]
Thus a nonzero evaluation
\[
\overline D_3(x_2)=2624
\]
is grading-consistent: \(x_2\) has degree \(223\), the detector has degree
\(-223\), and the scalar lies in degree zero.  More importantly, homogeneity
of \(x_2\) follows directly from (1)--(4), not merely from the detector.

## Passage through the remaining handles

Assume the fixed-\(W\) beta/psi cocone and the actual three-handle
factorization required elsewhere in the audit.

MWW Theorem 3.2 is an isomorphism of bigraded modules.  Its cable shifts are
chosen so that beta has total degree zero and the once-dotted stabilization
has raw degree \(+2\) followed by target shift \(-2\), hence total degree
zero.  The undotted stabilization has total degree \(-2\) and is set to zero.
Therefore the nonzero two-handle class remains homogeneous of degree 223.

MWW Theorem 3.7 identifies the three-handle map with a coequalizer in the
bigraded theory.  The handle attachment itself changes neither the filling
surface nor its labels and is degree zero.  The once-dotted hemisphere
relation is degree zero; the undotted column has degree \(-2\) and is killed.
If the detector satisfies the full three-handle cocone equations, its
nonzero class after the three-handles still has degree 223.

MWW Proposition 3.4 states that attaching a 4-handle with empty boundary
link induces an isomorphism.  The map is induced by inclusion of the same
filling and is absolute-bigrading preserving.  Hence the closed class remains
nonzero in quantum degree 223.

MWW Corollary 3.5 gives
\[
\mathcal S^2_0(S^4;\mathbb Z)\cong\mathbb Z
\]
in bidegree \((0,0)\).  After base change to \(\mathbb Q\), the quantum-degree
223 summand is zero.  Since diffeomorphism invariance preserves the absolute
bigrading, a genuine nonzero closed class in degree 223 would obstruct a
diffeomorphism with \(S^4\) just as a degree-494 class would.

Thus the numerical value 494 is not essential to the final logical
obstruction.  What is essential is a nonzero homogeneous class in any
nonzero absolute quantum degree.  Under the literal-split route that degree
would be 223.

## Semantic 494 inventory

If the relative split route were proved and adopted, the following active
files and generated artifacts would have to be changed or regenerated.
They must not be edited merely to make tests pass while the split hypothesis
remains open.

### Paper and public summaries

- README.md
- README.zh-CN.md
- paper/spc4-t73-candidate/README.md
- paper/spc4-t73-candidate/main.tex
- paper/spc4-t73-candidate/main-zh.tex
- paper/spc4-t73-candidate/sec-finite-details.tex
- paper/spc4-t73-candidate/sec-finite-details-zh.tex
- paper/spc4-t73-candidate/sec-appendices-extra.tex
- paper/spc4-t73-candidate/sec-appendices-extra-zh.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-00.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-00-zh.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-03.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-03-zh.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-05.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-05-zh.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-07.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-07-zh.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-09.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-09-zh.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-16.tex
- paper/spc4-t73-candidate/zh-chunks/chunk-16-zh.tex

The named paper result Proposition quantum degree
(label prop:degree-494), the degree-494 square, the final C/S/P3 statements,
and every occurrence of the ledger
\(-44+227+315-4=494\) would require replacement by the conditional split
ledger \(227-4=223\).

### Lean declarations and audit entry points

- Smooth4PC/CertificateData.lean
- Smooth4PC/HattoriBalancedInput.lean
- Smooth4PC/Interfaces.lean
- Smooth4PC/T73Finite.lean
- AuditArithmetic.lean
- T73Audit.lean

In particular, computedDegree_eq_494, degree_ledger_eq_494,
degree_subtraction_eq_494, degree_494_ne_zero, certificate_degree_eq,
IsActualFourHandle, and fourIso are hard-wired to 494.

### Executable checks and tests

- scripts/audit_t73_premises.py
- scripts/certify_t73_e12_s4.py
- scripts/certify_t73_p3_four_handle.py
- scripts/check_t73_c_pivotal_grading_inputs.py
- scripts/check_t73_claim_boundary.py
- scripts/generate_t73_c_comparison_witness.py
- tests/test_arithmetic_mutants.py
- tests/test_hattori_balanced_input.py
- tests/test_interface_audit.py
- tests/test_t73_c_pivotal_grading_inputs.py
- tests/test_t73_c_standard_pivotal_input.py
- tests/test_t73_e12_s4.py
- tests/test_t73_minimal_formalization.py
- tests/test_t73_proof_manifest.py
- tests/fixtures/arithmetic_mutants/degree_mutant.lean

The S4 calculation should be regenerated at degree 223.  Its mathematical
answer remains zero, but a test of EmptyKhQ(494) is not evidence about the
specific degree field used by the corrected interface.

### Current JSON/audit artifacts

- data/GLOBAL_FALSIFICATION_CHAIN_CERT.json
- audit/t73_c_comparison_witness.json
- audit/t73_c_pivotal_grading_report.json
- audit/t73_e12_s4_reduction.json
- audit/t73_p3_four_handle.json
- audit/t73_proof_dependency_manifest.json
- audit/interface_manifest.json
- audit/lean_type_dump.txt

These are generated or derived records and must be regenerated from corrected
sources rather than edited by hand.

### Active proof and review documents

- docs/INDEPENDENT_REVIEW.md
- docs/proofs/T73_CLOSURE_BLOCKER_AUDIT.md
- docs/proofs/T73_COUNTEREXAMPLE_MATERIALS_INDEX.md
- docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md
- docs/proofs/T73_EVIDENCE_ONE_CUP_E5_E6.md
- docs/proofs/T73_EVIDENCE_RAW_STATE_BINDING.md
- docs/proofs/T73_EVIDENCE_W2_CORE_FACTOR.md
- docs/proofs/T73_EXTERNAL_GEOMETRY_DISCHARGE.md
- docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md
- docs/proofs/T73_PROOF_STATE_LEDGER.md
- docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md
- docs/proofs/T73_S_P3_PAPER_PROOF.md
- docs/proofs/T73_THEOREM_C_DERIVATION.md
- docs/research/T73_COMPLETION_AUDIT_2026-09-02.md
- docs/research/T73_C_DISCHARGE_2026-09-02.md
- evidence/public_geometry/source_notes/AUD_B_REPORT.md
- evidence/public_geometry/source_notes/ORDINARY_SHADOW_HATTORI_CHAIN_RESULT.md
- evidence/public_geometry/source_notes/Q494_SPHERE_GRADING_LEDGER.md
- evidence/public_geometry/source_notes/RAW_STATE_BINDING_RESULT.md
- evidence/public_geometry/source_notes/W2_CORE_FACTOR_RESULT.md

The QSTAR raw receipts and historical plans/specifications also contain 494,
but they are immutable historical records.  They should be marked superseded,
not rewritten.

### Numeric 494 occurrences that are not quantum degrees

Several geometric artifacts use 494 as a letter, lane, connector, event, or
movie index.  Those occurrences must not be changed.  They include the
relevant entries in:

- geometry/t73_all_owner_product_primitives.json
- geometry/t73_johnson_spine_embedding.json
- geometry/t73_johnson_spine_binding.json
- geometry/t73_cancel_x_m1.json
- geometry/t73_belt_spheres.json
- geometry/t73_johnson_elementary_sweep.json
- data/T73_DELTA3_PUBLIC_INPUT.json
- data/T73_ENDPOINT_CONVENTION.json

Changing those indices would corrupt geometry rather than update a grading.

## Verdict

Conditional on the unproved relative split and all subsequent C/S comparison
maps, degree 223 propagates correctly to the closed manifold and still gives
the standard-sphere obstruction.  No current 494-bearing theorem or artifact
should be changed until that hypothesis is actually proved.
