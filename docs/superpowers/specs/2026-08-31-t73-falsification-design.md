# T73 Lean Falsification Audit Design

## Goal

Build a Lean 4 project that checks the complete logical and finite-arithmetic
content of the current `X(41,189,73)` falsification chain, while making every
unformalized geometric or functorial theorem impossible to hide.

The project has two distinct deliverables:

1. a zero-`sorry` **conditional kernel audit** whose external mathematical
   interfaces are explicit hypotheses; and
2. an **axiom-elimination ledger** showing exactly which interfaces must still
   receive Lean proofs before the result can be called an unconditional
   counterexample.

An unconditional theorem may be reported only if the final axiom audit contains
no project-specific axiom or hypothesis.

## Non-goals

- Do not encode the conclusion as a definition.
- Do not introduce `axiom`, `constant`, project `opaque`, `unsafe`, `extern`,
  `implemented_by`, `run_tac`, `admit`, `sorry`, or an opaque proof-producing
  executable. `by_contra` itself is permitted; the audit targets unproved
  contradictions rather than legitimate classical proof syntax.
- Do not call a theorem unconditional when it takes MWW, BHPW, HJ, geometry, or
  certificate-correctness hypotheses.
- Do not formalize the full MWW/BHPW/HJ papers in the first implementation
  batch; instead expose that work as the remaining proof surface.

## Authoritative workspace and build sandbox

The sole authoritative Git repository is local:

```text
D:\toffee_code_in_Cursor\smooth4pc-t73-lean
```

The server has no Git repository. It contains only a disposable build sandbox:

```text
/root/autodl-tmp/smooth4pc_t73_lean_build_20260831
```

The local host uploads a manifest-listed snapshot with `scp`; after compilation
the local host pulls source, logs and audit outputs back with `scp`, verifies
every SHA, and only then commits to the local Git repository. The server never
writes a Windows path.

Use Lean `v4.32.1` and the existing remote Mathlib checkout. Do not modify any
existing Lean project. Keep a byte copy of the final JSON certificate and its
SHA beside the generated Lean constants.

Before writing, resolve and verify both authorized roots, require that targets
do not exist, and reject every symlink or resolved path escaping its authorized
root. Record the Lean toolchain, Mathlib commit, dirty state and tree hash both
before and after the build. Use a dedicated read-only Mathlib copy and a
project-local build cache; never run `lake update`. Record certificate SHA
before and after every transfer and the final project-tree hash. Only one
implementer may hold the remote writer lock; reviewers are read-only.

## Architecture

### `Smooth4PC/Arithmetic.lean`

Kernel-proved finite facts:

- the Cappell--Shaneson matrix `A`;
- `det A = 1` and `det (A-I) = 1`;
- the chosen sphere matrix `D` and `det D = 1`;
- `(-8) * 7384 = -59072` and nonvanishing;
- all six sphere scalars are zero;
- `498 - 4 = 494` and `494 != 0`.

Use concrete integer matrices and `norm_num`, `ring_nf`, or ordinary `decide`
only. Do not use `native_decide`; the audit explicitly rejects
`Lean.ofReduceBool`. No hardcoded proposition proofs.

### `Smooth4PC/CertificateData.lean`

Generated constants copied from the SHA-pinned global certificate. The module
contains data only. A generator script must fail closed on a certificate SHA
mismatch. At audit time it regenerates a temporary Lean file from the frozen
JSON and byte-compares it with `CertificateData.lean`; a SHA comment is not
sufficient. `CertificateData.lean` may contain no `Prop`, theorem, proof, or
interface value.

### `Smooth4PC/Interfaces.lean`

Define narrow propositions/structures for the currently external mathematics:

- branchwise Hattori coefficient typing and actual cap functoriality;
- all-level beta/psi cubic descent;
- TH1/TH2/THXY embedded chosen-sphere and surface-to-map statements;
- the HJ attaching-system replacement;
- MWW three-handle coequalizer and four-handle graded isomorphism;
- the standard `S4` lasagna-module computation;
- diffeomorphism invariance of the bigraded module.
- the local Cappell--Shaneson implication from the proved matrix conditions to
  “the candidate is a homotopy 4-sphere.”

These are theorem parameters, not axioms. Their names and exact use sites must
remain visible in the final theorem type.

Freeze an interface manifest containing every field name and its fully expanded
type. No field may mention the final theorem, `Diffeomorphic`, an already
surviving class in the closed candidate, or `False`. The intended fields are
local only: the one-handle class type, actual cap map, cubic value and
ordinary-HH0 descent as separate fields; individual beta equations, psi0
equation, psi1 equation and the beta/psi quotient universal property as
separate fields; per-sphere embeddedness, class coordinate, map binding and two
scalar equations; pairwise disjointness and the local HJ replacement
implication; the MWW three-handle coequalizer universal property and transport
map; four-handle graded isomorphism, standard-sphere degree support, and
diffeomorphism invariance as separate statements. Every field must be consumed
by a named intermediate theorem. An unused field, or one field that alone
implies the conclusion, is a build failure.

### `Smooth4PC/ConditionalChain.lean`

Prove, from the interface hypotheses and arithmetic facts, that a nonzero
degree-494 class exists in the candidate and that no such class exists for the
standard sphere. Derive the conditional conclusion that the candidate is not
diffeomorphic to `S4`.

### `Smooth4PC/Unconditional.lean`

This file may define an unconditional theorem only after every interface has a
Lean proof. During the conditional stage it contains documentation only and the
project builds normally. The audit script asserts that the declaration
`Smooth4PC.notStandard` does not exist.

### `Audit.lean`

Run:

```lean
#print axioms Smooth4PC.conditionalNotStandard
#print axioms Smooth4PC.conditionalIsHomotopySphere
#print axioms Smooth4PC.conditionalCounterexample
```

and, if it exists:

```lean
#print axioms Smooth4PC.notStandard
```

The build log and a machine-readable ledger must distinguish theorem
hypotheses from axioms. Each of the three conditional declarations receives a
separate frozen transitive axiom list; the counterexample list must include the
dependency closure of both proof branches. `conditionalNotStandard` being
axiom-free does not make it unconditional; its arguments remain part of its
type.

A Lean meta audit expands abbreviations in the final declaration type, lists
all explicit, implicit and typeclass `forall` parameters, and byte-compares the
normalized result with the frozen interface manifest. This prevents hiding
conditions in implicit arguments or instances such as
`Nonempty InterfaceBundle`.

The transitive axiom allowlist for Lean `v4.32.1` is exact and frozen. It may
contain only explicitly reviewed foundational names (`propext`, `Quot.sound`,
and `Classical.choice` if the compiled proof actually needs them). Any extra
name fails. `sorryAx`, `Lean.ofReduceBool`, and every project-namespace axiom
always fail.

## Testing and hostile controls

The project must include negative controls that fail if:

- `-59072` is changed to zero;
- any sphere scalar is changed from zero;
- the sphere determinant is changed from one;
- degree `494` is changed to zero;
- an external interface is silently replaced by a theorem with an axiom;
- `Unconditional.lean` exports a theorem while any interface is unresolved.

Additional hostile fixtures must independently fail when they: transpose the
row-major matrix; corrupt determinant code; hide a hypothesis in an implicit
or typeclass parameter; import a project axiom; introduce
`native_decide`/`Lean.ofReduceBool`; add a broad interface carrying the
conclusion; mutate generated data and its theorem statement together; retain a
stale SHA comment after changing bytes; or export an apparently unconditional
theorem with a hidden parameter. Each fixture must fail at its named gate, not
only at an earlier generic SHA check.

Run all of:

```text
lake build
grep -R "sorry\|admit" Smooth4PC Audit.lean
lake env lean Audit.lean
python3 scripts/audit_axioms.py
python3 scripts/audit_declarations.py
python3 scripts/audit_theorem_type.py
python3 scripts/check_certificate_sha.py
python3 scripts/check_generated_data.py
```

## Completion states

### `CONDITIONAL_KERNEL_CLOSED`

- zero `sorry`;
- all finite facts and deductions compile;
- external theorem interfaces remain explicit arguments;
- no project-specific Lean axioms;
- the expanded theorem type exactly matches the frozen narrow-interface
  manifest;
- the exact foundational-axiom allowlist passes;
- no unconditional disproval claim.

### `UNCONDITIONAL_KERNEL_CLOSED`

- all conditions above;
- every interface has a Lean proof from definitions or imported proved
  theorems;
- Lean proves without external hypotheses that the matrix candidate is a
  homotopy 4-sphere;
- `Smooth4PC.notStandard` has no unresolved mathematical hypothesis;
- the conjunction “homotopy 4-sphere and not diffeomorphic to `S4`” has no
  unresolved mathematical hypothesis;
- `#print axioms` contains only accepted Lean/Mathlib foundational axioms.

Only the second state licenses the statement “Lean proves the counterexample.”

## Review strategy

One implementer writes each bounded component. A separate reviewer checks
specification compliance, then another checks proof/axiom hygiene. The final
reviewer must try to produce a zero-`sorry` fake proof using an illicit axiom;
the audit must detect and reject it.
