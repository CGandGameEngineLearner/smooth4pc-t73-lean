# Final closure blocker audit

**Status:** `CURRENT -- P0 AND C OPEN; S FOLLOWS CONDITIONALLY`

The proposed derivations in `T73_THEOREM_C_DERIVATION.md` and
`T73_THEOREM_S_DERIVATION.md` did not resolve the candidate-level joins.  The
ordinary representable-coefficient reduction inside C has since been proved.
The relative standard-sphere theorem removes S as an independent input, but
the actual product bimodule equivalence remains open.

This audit follows the constructive attempts to replace every unavailable
large artifact by compact public data.  It records what is now proved and the
two theorems that still cannot be obtained from the repository or the cited
literature.

## Publicly discharged finite and algebraic layers

The following statements now have executable public evidence:

1. six affine sweeps generate all 252 collar factors and the pinned
   44-strand pure braid;
2. the compact generator gives the registered reduced `m2/m3` words and a
   product-framing-name ledger, but not the whole embedded framed link;
3. the selected balanced cable has `p_y=44`, `p_z=271`, 88 oriented open
   endpoints and 227 closed circle factors;
4. the local normalized weight-one R-matrix is the exact unreduced Burau
   block after the displayed basis change;
5. `rho(W)-I` has no coefficients below order three on any of the 88 basis
   vectors or 7,744 matrix entries;
6. the five-owner cellular boundary has a unimodular `m2/m3` minor and gives
   unique sphere lifts supported on `rxy,ryz,rzx`;
7. a 32-step Nielsen program constructs the required integral sphere basis;
8. Lean proves the Frobenius split/counit identities, that `Id+O(h)`
   source/target corrections are invisible at cubic order, and that a
   representable coefficient `(T,T') -> Hom(BT,BT')` has ordinary coefficient
   `HH0` equivalent to the regular trace.

All corresponding mutation tests pass.  These facts do not depend on the
historical full PD or TH certificate bytes.

## Missing theorem C: coefficient trace comparison

The required arrow is a natural, grading-preserving map

\[
\mathsf C:
q\operatorname{Tr}(\mathcal C_{\mathrm{MWW}};M_R)
\widehat\otimes_{q=1+h}\mathbb Q[[h]]
\longrightarrow
\operatorname{Hom}_{\mathbb Q[[h]]}
\bigl((V^{\otimes86})_{86},(V^{\otimes88})_{86}\bigr)
\]

with all of the following properties:

1. both coefficient actions commute with the compact Hattori equivalence;
2. the selected trace class maps to the actual cup vector, including its
   higher `h` corrections;
3. every beta and psi map is natural for the statewise extensions of
   `mathsf C`;
4. the endpoint braid acts by the public Burau matrix in the same coordinates;
5. the cap row and all grading shifts commute with completion and
   specialization.

BPW constructs quantum traces and quantum annular homology.  BHPW constructs
strict Chen--Khovanov tangle functoriality and identifies quantum `HH0` of the
full algebras with their Chern/weight-space targets under flatness
hypotheses.  MWW identifies the one-handle skein lasagna module with ordinary
`HH0` of a tangle subcategory.  None of these sources identifies the actual
trace-73 coefficient bimodule with the representable model, nor proves its
compatibility with the MWW cable quotient.  The local R-matrix equality proves
only item 4.  Once a genuine two-sided product Hattori equivalence is supplied,
the ordinary representable reduction is no longer a blocker; its
quantum/completed lift still is.

## Theorem S is conditional on P0 and monoidal C

HJ Theorem 5.3 and its relative complete-system lemma allow the three
attaching spheres to be replaced by the standard system in
`#3(S1 x S2)` outside the detector ball supplied by P0.  MWW's intrinsic
module-action formula then imposes `A0=1` for the one-dotted sphere and
`A1=0` for the undotted sphere.  Symmetric monoidality of C gives these two
identities on the whole source.

Thus no signed slide-band, pivotal-adapter or endpoint-permutation certificate
is independently required for S.  Candidate-level S remains partial only
because P0 and the full monoidal C comparison are not instantiated.

## Negative controls

Two tempting shortcuts are demonstrably invalid:

1. changing only endpoint coordinates without simultaneously transporting
   `W,u,ell` can create a spurious anomaly;
2. Reynolds averaging all 44 even and 44 odd endpoint passages makes every
   coefficient of the public pairing zero.  It cannot replace BPW
   coefficient-trace cyclicity or the owner-copy beta quotient.

## Minimal condition for resumption

The proof can resume if either of the following is supplied:

1. a published theorem constructing C and proving its five compatibility
   properties for MWW coefficient modules; or
2. explicit chain/foam maps for the compact Hattori coefficient proving the
   full monoidal C comparison.

Until P0 and C are proved, `ExternalGeometry` has no legitimate
candidate-specific inhabitant and the paper must remain conditional.
