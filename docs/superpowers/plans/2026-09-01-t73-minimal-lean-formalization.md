# T73 Minimal Lean Formalization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Build a zero-sorry finite algebra layer and an explicitly conditional T73 counterexample theorem without custom axioms.

**Architecture:** New isolated Lean modules compute the finite facts from primitives, then transport the nonzero detector value through abstract staged quotient maps supplied as explicit geometry parameters. A small Python gate compiles the modules and rejects hidden axioms or unconditional exports.

**Tech Stack:** Lean 4.32.1, Mathlib, Python unittest, Git.

---

## Chunk 1: Finite algebra

### Task 0: Protect the existing dirty worktree

**Files:**
- Create outside repo: D:/tmp/t73_minimal_lean/untracked_baseline.json

- [ ] Record every pre-existing untracked file path, byte count and SHA-256.
- [ ] Add a helper assertion in the test that byte-compares the baseline after
  each chunk, excluding only the exact new-file allowlist.
- [ ] Never use git add -A or git add .; stage exact paths only.
- [ ] Do not delete, move or edit any repository untracked path. Keep all new
  scratch under D:/tmp/t73_minimal_lean/.

Before every commit in this plan:

- byte-compare the complete untracked baseline;
- stage only that task's explicit allowlist;
- assert git diff --cached --name-only is exactly that allowlist;
- fail closed on any difference.

### Task 1: Add a failing finite compile and source-contract test

**Files:**
- Create: tests/test_t73_minimal_formalization.py
- Test: tests/test_t73_minimal_formalization.py

- [ ] Write only test_finite_module_exists_and_builds, requiring
  Smooth4PC/T73Finite.lean.
- [ ] Run that subtest and confirm RED because the finite module does not exist.
- [ ] Add forbidden-token checks for sorry, admit, axiom, constant, opaque,
  unsafe, extern, implemented_by and run_tac in the new files only.
- [ ] Before any implementation, add RED-first exact-body expectations for
  computedCubic, computedDegree, det3 and matrixAMinusI.
- [ ] Add RED-first mutants for a constant cubic, constant degree, constant-one
  determinant, independently literal A-I and transposed A; confirm the finite
  contract test is RED.

### Task 2: Implement the finite module

**Files:**
- Create: Smooth4PC/T73Finite.lean
- Create: T73Audit.lean

- [ ] Define det3, A, A-I, sphere columns and primitive cubic/degree inputs.
- [ ] Prove determinant equalities, computedCubic=-59072,
  computedCubic!=0, computedDegree=494 and computedDegree!=0.
- [ ] Re-export the general undotted-zero and dotted-identity Frobenius row
  theorems from Smooth4PC/AugmentationCocone.lean.
- [ ] Add T73Audit finite-body output and exact-freeze the expanded bodies of
  computedCubic and computedDegree.
- [ ] Exact-freeze det3's Leibniz body and the entrywise A-I computation; make
  the already-written mutants fail for the intended reasons.
- [ ] Run test_finite_module_exists_and_builds and confirm GREEN; no later
  module is required by this subtest.
- [ ] Byte-compare the untracked baseline and assert the exact staged allowlist
  before committing.
- [ ] Commit the finite slice.

## Chunk 2: Conditional chain

### Task 3: Add external structures and a failing theorem-name check

**Files:**
- Create: Smooth4PC/T73External.lean
- Create: Smooth4PC/T73Conditional.lean
- Modify: tests/test_t73_minimal_formalization.py

- [ ] Extend the test to require the three conditional theorem names and to
  reject unconditional theorem names, hidden Prop parameters and
  final-conclusion structure fields.
- [ ] Run and confirm RED.
- [ ] Define the graded universe, staged geometry parameter and CS parameter.
- [ ] Emit and exact-freeze every external projection name/type and the
  normalized expanded types of all three conditional theorems.
- [ ] Add field-consumption checks; every projection must feed a named
  intermediate theorem and unused fields fail.
- [ ] Add mutants that remove geom, add a hidden Prop and add a
  final-not-diffeomorphic projection; confirm RED.
- [ ] Prove selectedClassNonzero from the finite cubic and staged row
  pullbacks.
- [ ] Prove conditionalNotStandard, conditionalIsHomotopySphere and
  conditionalCounterexample.
- [ ] Run and confirm GREEN.
- [ ] Byte-compare the untracked baseline and assert the exact staged allowlist
  before committing.
- [ ] Commit the conditional slice.

## Chunk 3: Axiom and type audit

### Task 4: Add the audit module and final gate

**Files:**
- Modify: T73Audit.lean
- Modify: tests/test_t73_minimal_formalization.py

- [ ] Extend the test to compile T73Audit.lean and inspect its output.
- [ ] Run and confirm RED.
- [ ] Add #check and #print axioms for every exported theorem.
- [ ] Compare Lean.collectAxioms with one exact foundational allowlist; reject
  every project/custom name, sorryAx and Lean.ofReduceBool.
- [ ] Add two audit mutants: a consumed custom axiom and an unconditional
  notStandard export; confirm both are rejected.
- [ ] Require the conditional theorem type to contain explicit geom and cs
  parameters, with no unconditional export.
- [ ] Run the new test and the existing proof-manifest test.
- [ ] Run git diff --check and inspect exact staged scope.
- [ ] Byte-compare the untracked baseline and assert the exact staged allowlist
  before committing.
- [ ] Commit the audit slice.
