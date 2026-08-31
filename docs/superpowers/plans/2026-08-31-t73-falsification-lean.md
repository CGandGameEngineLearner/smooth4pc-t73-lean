# T73 Falsification Lean Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-`sorry`, axiom-audited Lean 4 kernel audit of the `X(41,189,73)` falsification chain, with a hard separation between conditional closure and an unconditional counterexample theorem.

**Architecture:** A deterministic generator imports only numeric data from the frozen global JSON. Lean proves the finite arithmetic and the deduction through narrow external interfaces. Meta/Python audits reject hidden hypotheses, project axioms, unsafe declarations, stale generated data, or an illicit unconditional theorem.

**Tech Stack:** Lean 4.32.1, Mathlib pinned local worktree, Lake, Python 3, Git worktrees, SHA-256.

**Commit rule:** The remote sandbox never runs Git. Every `Commit as ...` step
means: pull the listed files to the local authority host with `scp`, verify the
transfer manifest and every SHA, place them in the local worktree, then commit
in the local authority repository.

---

## Chunk 1: Local authority and isolated remote build

### Task 1: Local repository, worktree and server sandbox

**Files:**
- Create local repository: `D:\toffee_code_in_Cursor\smooth4pc-t73-lean`
- Create local worktree: `D:\toffee_code_in_Cursor\smooth4pc-t73-lean\.worktrees\formalize-t73`
- Create remote non-Git sandbox: `/root/autodl-tmp/smooth4pc_t73_lean_build_20260831`
- Copy: `docs/superpowers/specs/2026-08-31-t73-falsification-design.md`
- Copy: `docs/superpowers/plans/2026-08-31-t73-falsification-lean.md`
- Create: `ENVIRONMENT.json`

- [ ] Resolve the local parent/repo/worktree and remote sandbox/dependency paths; reject symlinks or any resolved path outside the two authorized roots.
- [ ] Create the local Git repository, ignore `.worktrees/`, commit only design/plan/environment, and add branch `formalize/t73-falsification` as the local worktree.
- [ ] Record `lean-toolchain`, `/root/.elan/bin/lean --version`, Mathlib commit, dirty state/tree hash, and certificate SHA in `ENVIRONMENT.json`.
- [ ] Create the remote sandbox without `.git`, acquire a single-writer lock, and configure a read-only pinned Mathlib copy; do not run `lake update`.
- [ ] Create `lean-toolchain` with `leanprover/lean4:v4.32.1` and a minimal `lakefile.toml`.
- [ ] Upload a manifest-listed snapshot from the local host with `scp`, verify every remote SHA, add a one-line `Smoke.lean`, run `lake env lean Smoke.lean`, and require exit 0.
- [ ] Commit baseline as `chore: initialize isolated Lean audit`.

## Chunk 2: Deterministic certificate boundary

### Task 2: Certificate generator and byte audit

**Files:**
- Create: `data/GLOBAL_FALSIFICATION_CHAIN_CERT.json`
- Create: `scripts/generate_certificate_data.py`
- Create: `scripts/check_certificate_sha.py`
- Create: `scripts/check_generated_data.py`
- Create: `Smooth4PC/CertificateData.lean`
- Test: `tests/test_certificate_generation.py`

- [ ] Write failing tests for the exact expected JSON SHA `8B4A0B39ABABD7CFA284E67189A8AF4E60473F88CADC8722A1ABA8321B72EB86`, deterministic generation, and stale-comment mutation.
- [ ] Copy the frozen JSON and verify its SHA before generating anything.
- [ ] Implement a generator that accepts numeric/list/string data only and rejects JSON keys or values intended to encode propositions or proof text.
- [ ] Generate `CertificateData.lean` with concrete integers, matrices, degree, and six sphere scalars; include the full source SHA in a constant data string.
- [ ] Regenerate to a temporary file and byte-compare it during every audit.
- [ ] Run the tests; each mutant must fail at its named gate.
- [ ] Commit as `feat: bind Lean data to frozen certificate`.

## Chunk 3: Kernel arithmetic

### Task 3: Prove every finite gate

**Files:**
- Create: `Smooth4PC/Arithmetic.lean`
- Create: `AuditArithmetic.lean`
- Test: `tests/test_arithmetic_mutants.py`

- [ ] Add failing Lean checks for matrix orientation, `det A`, `det(A-I)`, `det D`, cubic value, six zeros, and degree 494.
- [ ] Define an explicit `3x3` integer determinant function and row-major matrices from generated data.
- [ ] Prove using `norm_num`/`ring_nf` only:
  `det A = 1`, `det(A-I)=1`, `det D=1`, `(-8)*7384=-59072`, `-59072 != 0`, all sphere scalars `=0`, and `498-4=494 != 0`.
- [ ] Add transpose and determinant-code mutants and assert the arithmetic gate, not SHA, rejects them.
- [ ] Scan source and environment to reject `native_decide` and `Lean.ofReduceBool`.
- [ ] Commit as `feat: prove finite falsification arithmetic`.

## Chunk 4: Narrow theorem interfaces

### Task 4: Interface types and manifest audit

**Files:**
- Create: `Smooth4PC/Interfaces.lean`
- Create: `audit/interface_manifest.json`
- Create: `AuditType.lean`
- Create: `scripts/audit_theorem_type.py`
- Create: `scripts/audit_declarations.py`
- Test: `tests/test_interface_audit.py`

- [ ] Define staged degree-494 rational vector spaces, linear quotient maps, a named one-handle element and local functionals.
- [ ] Freeze the one-handle interface as separate fields for class typing,
  actual cap map, cubic value equation, trace-anomaly order equation, and the
  ordinary-HH0 quotient universal property.
- [ ] Freeze beta/psi as separate beta action equations, psi0 equation, psi1
  equation, relation submodule, and quotient universal property.
- [ ] Freeze three chosen sphere relation maps and six scalar equations;
  embedded/disjoint/class data; local HJ replacement; the MWW three-handle
  coequalizer universal property and transport; four-handle graded
  isomorphism; S4 degree support; diffeomorphism invariance; and the local
  Cappell--Shaneson implication from the proved matrix conditions to
  `IsHomotopySphere candidate`.
- [ ] Prohibit any interface field mentioning the final theorem, `Diffeomorphic`, a final surviving class, or `False`.
- [ ] Emit a normalized manifest of every explicit/implicit/typeclass final-theorem parameter.
- [ ] Implement a Lean meta dump plus Python exact comparison after abbreviation reduction.
- [ ] Implement declaration scanning for `axiom`, `constant`, project `opaque`, `unsafe`, `extern`, `implemented_by`, `run_tac`, `sorry`, and `admit`.
- [ ] Freeze standalone signatures for `conditionalNotStandard`,
  `conditionalIsHomotopySphere`, and `conditionalCounterexample`, then generate
  their normalized manifests before the final theorems exist. The
  `conditionalNotStandard` signature must not contain the Cappell--Shaneson
  homotopy-sphere premise.
- [ ] Add hostile fixtures for hidden implicit/typeclass hypotheses, imported axioms, and a broad conclusion-carrying field. Defer the unused-field consumption fixture until Task 5 defines the consuming theorem chain.
- [ ] Commit as `feat: freeze narrow mathematical interfaces`.

## Chunk 5: Conditional proof and axiom hygiene

### Task 5: Prove the conditional chain

**Files:**
- Create: `Smooth4PC/ConditionalChain.lean`
- Create: `Smooth4PC/Unconditional.lean`
- Create: `Audit.lean`
- Create: `scripts/audit_axioms.py`
- Test: `tests/test_unconditional_gate.py`

- [ ] Define the one-handle type, cap map/value and cubic descent as separate local premises; define beta/psi relation maps and quotient universal property separately.
- [ ] Define beta/psi and sphere relation submodules and use quotient universal properties to descend the nonzero functional from stage to stage.
- [ ] Define and consume the MWW three-handle coequalizer/transport premise explicitly; do not replace it with a final-survival premise.
- [ ] Prove every interface field is consumed by a named intermediate theorem.
- [ ] Prove `Smooth4PC.conditionalNotStandard` with all external premises visible in its fully expanded type.
- [ ] Prove `Smooth4PC.conditionalIsHomotopySphere` from only the matrix facts
  and the narrow Cappell--Shaneson implication.
- [ ] Prove `Smooth4PC.conditionalCounterexample : IsHomotopySphere candidate
  ∧ ¬ Diffeomorphic candidate S4` by combining the preceding two theorems.
- [ ] Normalize and byte-compare the complete types of all three conditional
  declarations against their Task 4 signature manifests; reject any extra,
  missing, implicit or instance parameter.
- [ ] Run the unused-interface-field fixture now that every named intermediate
  theorem exists; require every field to be consumed by the counterexample
  chain, while forbidding the CS premise from entering `conditionalNotStandard`.
- [ ] Keep `Smooth4PC.notStandard` absent while any interface is unresolved.
- [ ] Run and freeze separate transitive `#print axioms` results for
  `conditionalNotStandard`, `conditionalIsHomotopySphere`, and
  `conditionalCounterexample`; verify that the counterexample closure covers
  both branches. Use an exact Lean-4.32.1 allowlist and always reject
  `sorryAx`, `Lean.ofReduceBool`, and project axioms.
- [ ] Add mutants for an axiom in an imported module, a hidden final parameter, an illicit unconditional theorem, and synchronized generated-data/theorem tampering.
- [ ] Commit as `feat: prove axiom-audited conditional chain`.

## Chunk 6: Integrated hostile verification

### Task 6: Final verification and handoff

**Files:**
- Create: `FINAL_LEAN_AUDIT.md`
- Create: `audit_results.json`
- Create: `PROJECT_TREE_SHA256.txt`

- [ ] Run `lake build` and `lake env lean Audit.lean`.
- [ ] Run every Python audit and hostile fixture; require all positive tests pass and every mutant fail at its specified gate.
- [ ] Recompute the transferred JSON SHA and generated-file byte identity.
- [ ] Record `#print axioms`, expanded theorem parameters, declaration scan, Mathlib pin/dirty state, and project tree SHA.
- [ ] Classify exactly one status:
  `CONDITIONAL_KERNEL_CLOSED`, `UNCONDITIONAL_KERNEL_CLOSED`, or `FAILED`.
- [ ] Dispatch independent specification and proof-hygiene reviews; fix and re-run until both approve.
- [ ] Commit as `test: complete hostile Lean kernel audit`.
- [ ] Have the local host pull final source/logs/audits from the server with `scp`; verify each pre/post-transfer SHA, update the local worktree, and commit only after byte identity passes.
- [ ] Stop the remote instance only after transfer and process verification.

## Promotion rule

The project may say “Lean proves the counterexample” only in state
`UNCONDITIONAL_KERNEL_CLOSED`. Promotion additionally requires an
external-hypothesis-free theorem that the candidate is a homotopy 4-sphere and
an external-hypothesis-free `notStandard` theorem; both exact theorem types and
both transitive axiom lists must pass the allowlist. A zero-`sorry` conditional
theorem, even with an empty axiom list, remains conditional when its type
contains external theorem arguments.
