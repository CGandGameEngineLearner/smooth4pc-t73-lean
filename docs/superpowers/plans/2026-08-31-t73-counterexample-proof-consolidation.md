# T73 Counterexample Proof Consolidation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one source-indexed candidate proof of a nonzero degree-494 class for the `X(41,189,73)` sphere, formalize the finite algebra honestly in Lean, and subject the complete chain to independent hostile review.

**Architecture:** The written proof is the authoritative mathematical narrative. Lean checks only finite arithmetic and abstract algebraic lemmas; geometric Hattori, HJ, MWW, and BHPW inputs remain visible theorem parameters until formally constructed. A machine-readable dependency manifest prevents a compiled conditional theorem from being reported as a fully formalized counterexample.

**Tech Stack:** Markdown, Lean 4.32.1, Mathlib, Python 3 `unittest`, JSON, Git.

---

## Chunk 1: Mathematical proof and source ledger

### Task 1: Freeze the proof dependency table

**Files:**
- Create: `audit/t73_proof_dependency_manifest.json`
- Create: `tests/test_t73_proof_manifest.py`
- Read: `docs/superpowers/specs/2026-08-31-t73-counterexample-proof-consolidation-design.md`

- [ ] **Step 1: Write a failing manifest test**

Require exact entries for:

```text
balanced_hattori_equivalence
actual_diagonal_class
nu0_binding
point_push_cubic
beta_psi_cocone
fixed_y_hj_basis
direct_q_sphere_cocone
phi_w_naturality
bpw_vertical_horizontal_trace
bhpw_strict_functoriality
mww_handle_core_formulas
four_handle_isomorphism
s4_bigraded_control
```

The test must reject the one-sided coefficient model, `xi` as the input,
`M_0(88)`, scalar `-28864`, a path-dependent edge braid, and any status
claiming full formal verification.

- [ ] **Step 2: Run the test and confirm RED**

Run:

```powershell
python tests\test_t73_proof_manifest.py
```

Expected: failure because the manifest does not exist.

- [ ] **Step 3: Create the minimal manifest**

Each entry must contain:

```json
{
  "status": "proved_in_document|finite_verified|external_theorem",
  "lean_role": "none|explicit_parameter|derived_theorem",
  "source_paths": [],
  "claim": "",
  "consumers": []
}
```

Pin these invariants literally:

```text
input = v_T, not xi
M_R(T,T') = Hom(BT,BT') tensor A^(tensor 227)
source = M_1(88)
relative_nu = 0
cubic_value = -59072
final_q = 494
```

- [ ] **Step 4: Run the test and confirm GREEN**

Run the same command. Expected: all manifest tests pass.

- [ ] **Step 5: Commit only the manifest and its test**

```powershell
git add audit/t73_proof_dependency_manifest.json tests/test_t73_proof_manifest.py
git commit -m "test: freeze t73 proof dependencies"
```

### Task 2: Write the unified mathematical proof

**Files:**
- Create: `docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md`
- Test: `tests/test_t73_proof_manifest.py`

- [ ] **Step 1: Write the theorem statement and scope**

State the draft as `CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW`, not internal
closure, external acceptance, or full formal verification.  Only Task 6 may
promote it to `CANDIDATE_PROOF_INTERNALLY_CLOSED`. Define the balanced coefficient
equivalence

```text
H_(T,T') : M_R(T,T') ~= Hom(BT,BT') tensor A^(tensor 227)
```

and

```text
T = inverse(B) o U_(0,5)
v_T = inverse(H_(T,T))(Id_(BT) tensor X^(tensor 227)).
```

- [ ] **Step 2: Write the input, grading, and scalar sections**

Derive `BT=U_(0,5)`, the strict shadow `u=e_0-e_5+O(h)`, the raw/shifted
degree ledger `183+315-4=494`, and

```text
[h^3] ell (rho_h(W)-I) u = -59072.
```

Give a separate boxed retraction: `xi` is not the input and its relative cubic
is zero.

- [ ] **Step 3: Write the complete quotient argument**

Define `V_s_actual`, `V_s_canonical`, `Q_s`, `lambda_s`, and relative `nu`.
Prove the beta, psi0, psi1, three undotted-sphere, and three dotted-sphere
cocone equations on the entire source. Include both lattice directions and
the quotient universal properties.

- [ ] **Step 4: Write the changing-endpoint and final comparison sections**

State the exact `Phi` and `W/K` squares, the four-handle grading-preserving
isomorphism, and the external computation

```text
Sz_0^2(S4;Q) ~= Q in bidegree (0,0).
```

Conclude only after deriving a nonzero homogeneous degree-494 class.

- [ ] **Step 5: Add primary-source and local-evidence anchors**

Every external theorem gets a source file and line/section anchor. Every
finite number gets its recomputation path. No certificate status is allowed
as the sole support for a mathematical implication.

- [ ] **Step 6: Run the manifest test**

Expected: GREEN and every manifest consumer points to a named proof section.

- [ ] **Step 7: Commit the proof draft**

```powershell
git add docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md
git commit -m "docs: consolidate t73 candidate proof"
```

---

## Chunk 2: Lean algebra and negative controls

### Task 3: Formalize the Frobenius augmentation cocone

**Files:**
- Create: `Smooth4PC/AugmentationCocone.lean`
- Create: `tests/test_augmentation_cocone.py`
- Modify: `Smooth4PC.lean`

- [ ] **Step 1: Write a failing Lean-import test**

The test invokes:

```powershell
& 'C:\Users\LENOVO\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe' env lean Smooth4PC\AugmentationCocone.lean
```

Expected: fail because the module does not exist.

- [ ] **Step 2: Define the rank-two Frobenius algebra and tensor words**

Encode `one`, `X`, `Delta`, and `epsilon`. Do not write `X^227`; use lists or
finitely indexed tensor words.

- [ ] **Step 3: Prove the iterated split formulas**

Prove for every positive `b`:

```text
epsilon^b (Delta^(b-1)(1)) = 0
epsilon^b (Delta^(b-1)(X)) = 1
```

without project axioms or `sorry`.

- [ ] **Step 4: Prove the abstract direct-Q cocone lemma**

Take explicit linear equivalences `Q_s,Q_t` and show that conjugated
undotted/dotted maps satisfy

```text
Lambda_t o C_e^0 = 0
Lambda_t o C_e^1 = Lambda_s
```

on the whole source.

- [ ] **Step 5: Prove Reynolds telescope and cubic flatness**

Prove physical-copy orbit ratios telescope along every finite state path.
Under explicit vertex potentials `Q_s`, prove
`K_t C_e_0 = C_e_0 K_s`; reject an edge-local pure braid that is not a
vertex coboundary.

- [ ] **Step 6: Run Lean and the Python test**

Expected: both pass.

- [ ] **Step 7: Commit**

```powershell
git add Smooth4PC/AugmentationCocone.lean Smooth4PC.lean tests/test_augmentation_cocone.py
git commit -m "feat: prove augmentation cocone algebra"
```

### Task 4: Formalize balanced-input typing and degree arithmetic

**Files:**
- Create: `Smooth4PC/HattoriBalancedInput.lean`
- Create: `tests/test_hattori_balanced_input.py`
- Modify: `Smooth4PC.lean`

- [ ] **Step 1: Write negative tests**

Fixtures must fail if they use:

```text
Hom(T,BT) instead of Hom(BT,BT')
X^227 instead of a tensor power
xi instead of v_T
M_0 instead of M_1
-28864 instead of -59072
```

- [ ] **Step 2: Define the narrow geometric interface**

Expose the balanced Hattori equivalence as a theorem parameter. Encode only
its typed consequence for the diagonal class; do not assume the final
counterexample or a surviving closed class.

Add a positive typed fixture with source `M_1(88)`.  Define relative `nu` by
subtracting the mandatory endpoint defect: the canonical base vector and
`e_0-e_5` are `nu=0`; dotted maps preserve `nu`; undotted maps raise it by
one; the row is zero on every `nu>=1` component.  The test must inspect the
theorem type and fail if `M_0` appears anywhere.

- [ ] **Step 3: Prove the finite degree and scalar consequences**

Kernel-check:

```text
183 + 315 - 4 = 494
(-8) * 7384 = -59072
-59072 != 0
```

- [ ] **Step 4: Run Lean and negative tests**

Expected: canonical module passes and all five mutants fail at their named
gate.

- [ ] **Step 5: Commit**

```powershell
git add Smooth4PC/HattoriBalancedInput.lean Smooth4PC.lean tests/test_hattori_balanced_input.py
git commit -m "feat: type balanced Hattori input"
```

### Task 5: Integrate without hiding hypotheses

**Files:**
- Modify: `Smooth4PC/Interfaces.lean`
- Modify: `Smooth4PC/ConditionalChain.lean`
- Modify: `Audit.lean`
- Modify: `AuditType.lean`
- Create: `audit/t73_interface_manifest.json`
- Create: `audit/t73_field_role_manifest.json`
- Create: `audit/t73_lean_type_dump.txt`
- Create: `audit/t73_axiom_type_dump.txt`
- Create: `audit/t73_kernel_manifest.json`
- Create: `audit/t73_verification_receipt.json`
- Create: `scripts/write_t73_verification_receipt.py`
- Create: `tests/test_t73_verification_receipt.py`
- Test: `tests/test_interface_audit.py`
- Test: `tests/test_unconditional_gate.py`

- [ ] **Step 1: Add narrowly typed local interfaces**

Export only primitive external inputs: balanced Hattori geometry, BPW trace,
fixed-Y/HJ geometry, direct-Q state equivalences and edge conjugacy, MWW
handle/core-attachment formulas, BPW/BHPW strict functoriality, and graded
four-handle/standard-sphere controls.  Add separately named and consumed
fields for `Phi` core-attachment naturality and `W` conjugation.  Do not
export cubic `K` naturality or the complete cocone equations as interfaces;
derive them as named Lean theorems from vertex-potential conjugation in Task
3. No field may state the final conclusion.

- [ ] **Step 2: Make each field feed a named intermediate theorem**

Reject unused fields and any field consumed only by the final theorem.

- [ ] **Step 3: Rebuild the conditional chain**

Use `v_T`, never `xi`. Keep every external geometric theorem visible in the
expanded final theorem type.

- [ ] **Step 4: Run all interface and unconditional-gate tests**

Expected: conditional theorem compiles; unconditional theorem remains absent.
Regenerate the new `t73_*` type dumps/manifests from `AuditType.lean` and
`Audit.lean`.  Existing Task4/Task5 manifests and remote receipts remain
historical immutable evidence and must not be overwritten or cited as a
receipt for the new interface.

Generate `t73_verification_receipt.json` from the exact current bytes.  It
must bind SHA-256 values for every touched Lean source, every verification
script used in Task 7 (`audit_axioms.py`, `audit_declarations.py`,
`audit_theorem_type.py`, `audit_field_consumption.py`, both certificate/data
checkers, and the receipt generator/test), both captured dumps, all manifests,
and the Lean/Mathlib versions.  Its test must recompute every hash and reject
a stale receipt.

- [ ] **Step 5: Commit**

```powershell
git add Smooth4PC/Interfaces.lean Smooth4PC/ConditionalChain.lean Audit.lean AuditType.lean audit/t73_interface_manifest.json audit/t73_field_role_manifest.json audit/t73_lean_type_dump.txt audit/t73_axiom_type_dump.txt audit/t73_kernel_manifest.json audit/t73_verification_receipt.json scripts/write_t73_verification_receipt.py tests/test_t73_verification_receipt.py tests/test_interface_audit.py tests/test_unconditional_gate.py
git commit -m "refactor: expose t73 proof interfaces"
```

---

## Chunk 3: Independent audit and final verification

### Task 6: Run two independent proof reviews

**Files:**
- Create: `audit/T73_SOURCE_TYPE_REVIEW.md`
- Create: `audit/T73_FULL_CHAIN_HOSTILE_REVIEW.md`

- [ ] **Step 1: Source/type review**

Reconstruct the balanced coefficient from primary definitions and check every
domain/codomain and grading shift. Explicitly try the one-sided coefficient,
mate, `xi`, and `M_0` countermodels.

- [ ] **Step 2: Full-chain hostile review**

Try to construct a relation-source vector on which the claimed scalar cocone
fails. Check all beta/psi/sphere directions, pure-braid holonomy, and the
absolute grading comparison.

- [ ] **Step 3: Repair and re-review until both say APPROVED**

Do not self-certify. Any unresolved mathematical premise returns the status to
conditional/open.

- [ ] **Step 4: Commit the reviews**

```powershell
git add audit/T73_SOURCE_TYPE_REVIEW.md audit/T73_FULL_CHAIN_HOSTILE_REVIEW.md
git commit -m "audit: review t73 candidate proof"
```

### Task 7: Full repository verification

**Files:**
- Verify all files from Tasks 1–6

- [ ] **Step 1: Run Python tests**

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all tests pass.

- [ ] **Step 2: Run Lean modules and axiom audits**

```powershell
$lake='C:\Users\LENOVO\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe'
& $lake env lean Smooth4PC\AugmentationCocone.lean
& $lake env lean Smooth4PC\HattoriBalancedInput.lean
& $lake env lean Smooth4PC.lean
$typeOut = & $lake env lean AuditType.lean 2>&1; $typeCode=$LASTEXITCODE
$typeOut | Set-Content -Encoding utf8 audit\t73_lean_type_dump.txt
if ($typeCode -ne 0) { exit $typeCode }
$axiomOut = & $lake env lean Audit.lean 2>&1; $axiomCode=$LASTEXITCODE
$axiomOut | Set-Content -Encoding utf8 audit\t73_axiom_type_dump.txt
if ($axiomCode -ne 0) { exit $axiomCode }
python scripts\audit_axioms.py --root . --source Audit.lean --dump audit/t73_axiom_type_dump.txt --kernel-manifest audit/t73_kernel_manifest.json
python scripts\audit_declarations.py --root Smooth4PC
python scripts\audit_declarations.py --root . --source Smooth4PC.lean
python scripts\audit_declarations.py --root . --source AuditArithmetic.lean
python scripts\audit_declarations.py --root . --source AuditType.lean
python scripts\audit_declarations.py --root . --source Audit.lean
python scripts\audit_theorem_type.py --manifest audit/t73_interface_manifest.json --dump audit/t73_lean_type_dump.txt --root .
python scripts\audit_field_consumption.py --root . --interfaces Smooth4PC/Interfaces.lean --consumer Smooth4PC/ConditionalChain.lean --manifest audit/t73_field_role_manifest.json --interface-manifest audit/t73_interface_manifest.json
python scripts\check_certificate_sha.py
python scripts\check_generated_data.py
python scripts\write_t73_verification_receipt.py --root . --write audit/t73_verification_receipt.json
python tests\test_t73_verification_receipt.py
```

Expected: every explicitly named Lean module compiles, zero `sorry`, no
project axiom, and exact theorem-type/manifest agreement.  `lake build` is not
used because this repository has `defaultTargets = []`.

- [ ] **Step 3: Check worktree and commit scope**

```powershell
git status --short
git log --oneline -8
```

Do not commit `deps/`, `lake-manifest.json`, or unrelated pre-existing
untracked files.

- [ ] **Step 4: Assign the honest final status**

Use only after both Task 6 reviews say `APPROVED`:

```text
CANDIDATE_PROOF_INTERNALLY_CLOSED
```

unless the complete geometric chain has become hypothesis-free in Lean. Never
write `FORMALLY_VERIFIED_COUNTEREXAMPLE` merely because the algebraic modules
compile.
