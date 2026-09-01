# T73 Minimal Lean Formalization Design

## Goal

Formalize the strongest honest slice that the current Lean/Mathlib environment
can check now:

1. a zero-sorry, zero-project-axiom finite algebra layer; and
2. a zero-sorry conditional counterexample theorem whose external geometry is
   visible as theorem parameters.

This work does not claim that AR, Laudenbach--Poenaru, HJ, MWW or the
candidate-specific smooth handle constructions have been formalized in Lean.

## Chosen approach

Create an isolated namespace and new tracked files. Do not modify or consume
the pre-existing untracked Lean experiments. Do not reuse the old interface
fields that directly assume the final scalar or six final cocone equations.

Two rejected alternatives:

- extending the old interface surface: shorter, but it registers
  rawCapChosen=-59072 and the sphere equations as inputs;
- formalizing smooth four-manifold handle theory from first principles:
  genuinely unconditional, but far beyond the available library and this
  first deliverable.

## Files

- Smooth4PC/T73Finite.lean
  - primitive matrix, sphere-column, cubic and degree data;
  - determinant, cubic, degree and Frobenius/counit proofs;
  - no manifold or actual-geometry language.
- Smooth4PC/T73External.lean
  - abstract graded invariant universe;
  - staged W0/W1/W2/W3 maps and detector transport;
  - explicit external geometry and CS structures, with no inhabitant or axiom.
- Smooth4PC/T73Conditional.lean
  - conditionalNotStandard;
  - conditionalIsHomotopySphere;
  - conditionalCounterexample.
- T73Audit.lean
  - exact theorem types and #print axioms output.
- tests/test_t73_minimal_formalization.py
  - build, forbidden-source, theorem-type and axiom-output gates.

## Finite layer

The input is restricted to primitives:

- A and the three sphere columns;
- cubic base coefficient 7384 and substitution coefficient -2;
- degree contributions -44, 227, 315 and -4;
- the rank-two Frobenius operations already proved in
  Smooth4PC/AugmentationCocone.lean.

The value -59072 must be computed as (-2)^3 * 7384. The value 494 must be
computed from the four degree contributions. The finite layer must not import
Smooth4PC/CertificateData.lean, which registers those answers directly.
The audit must print and exact-freeze the expanded bodies of computedCubic and
computedDegree. Mutants replacing either body by the final constant must fail.
It must also exact-freeze the Leibniz 3-by-3 body of det3 and prove that
matrixAMinusI is computed entrywise from matrixA and the identity matrix,
rather than independently registered. Determinant-implementation,
matrix-minus-identity and transpose mutants must fail.

The only permitted imports for the finite module are tracked Mathlib modules
and the tracked Smooth4PC/AugmentationCocone.lean. It must not import any
untracked experiment.

## Conditional layer

The external geometry parameter supplies staged modules and maps:

    x0 --q01--> x1 --q12--> x2 --transport--> x3 --fourIso--> candidate q=494

Rows ell0, ell1 and ell2 satisfy pullback equations, and ell0(x0) is bound to
the finite computed cubic value. Therefore the selected class is nonzero
without an external field asserting nonzero.

The same parameter supplies:

- standard-S4 vanishing at q=494; and
- graded diffeomorphism invariance.

The CS parameter supplies only the implication from the two determinant
equalities to IsHomotopySphere(candidate). It cannot state the conclusion
directly without consuming those finite equalities.

## Audit contract

- Every new theorem compiles with zero sorry/admit.
- No project axiom, constant, opaque theorem, unsafe declaration, extern,
  implemented_by or run_tac.
- Lean.collectAxioms is compared with an exact foundational allowlist; any
  extra name, sorryAx or Lean.ofReduceBool fails.
- Lean Meta exact-freezes the expanded theorem types and every projection of
  the two external structures. Hidden Props, final-conclusion fields and
  unused fields fail.
- The final theorem type visibly contains both external parameters and every
  projection is consumed by a named intermediate theorem.
- No unconditional notStandard or counterexample theorem is exported.
- Before implementation, every pre-existing untracked path is recorded outside
  the repository with a content SHA. Every chunk byte-compares that snapshot;
  staging uses an exact allowlist and never git add -A or git add ..
- No repository untracked file may be deleted, moved or edited during this
  implementation. Scratch is confined to D:/tmp/t73_minimal_lean/.
- Negative fixtures must prove that a consumed custom axiom and an
  unconditional notStandard export are both rejected.

## Honest completion language

Allowed:

    FINITE_ALGEBRA_PASS
    CONDITIONAL_CHAIN_PASS
    EXTERNAL_GEOMETRY_UNFORMALIZED

Forbidden:

    FORMALLY_VERIFIED_COUNTEREXAMPLE
    UNCONDITIONAL_COUNTEREXAMPLE
