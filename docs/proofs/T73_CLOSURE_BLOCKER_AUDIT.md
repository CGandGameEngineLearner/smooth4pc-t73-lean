# Final closure blocker audit

**Status:** `SUPERSEDED -- THEOREMS C AND S SUBSEQUENTLY DERIVED`

The blockers recorded below were resolved by
`T73_THEOREM_C_DERIVATION.md` and `T73_THEOREM_S_DERIVATION.md`.  This file is
retained as the negative audit that forced the completed functorial-cabling
and whole-sphere arguments.

This audit follows the constructive attempts to replace every unavailable
large artifact by compact public data.  It records what is now proved and the
two theorems that still cannot be obtained from the repository or the cited
literature.

## Publicly discharged finite and geometric layers

The following statements now have executable public evidence:

1. six affine sweeps generate all 252 collar factors and the pinned
   44-strand pure braid;
2. the compact AR product-ribbon generator gives the registered reduced
   `m2/m3` words and product framing ledger;
3. the selected balanced cable has `p_y=44`, `p_z=271`, 88 oriented open
   endpoints and 227 closed circle factors;
4. the local normalized weight-one R-matrix is the exact unreduced Burau
   block after the displayed basis change;
5. `rho(W)-I` has no coefficients below order three on any of the 88 basis
   vectors or 7,744 matrix entries;
6. the five-owner cellular boundary has a unimodular `m2/m3` minor and gives
   unique sphere lifts supported on `rxy,ryz,rzx`;
7. a 32-step Nielsen program constructs the required integral sphere basis;
8. Lean proves the Frobenius split/counit identities and that `Id+O(h)`
   source/target corrections are invisible at cubic order.

All corresponding mutation tests pass.  These facts do not depend on the
historical full PD or TH certificate bytes.

## Missing theorem C: coefficient trace comparison

The required arrow is a natural, grading-preserving map

\[
\mathsf C:
q\operatorname{Tr}(\mathcal C_{\mathrm{MWW}};M_R)
\widehat\otimes_{q=1+h}\mathbb Q[[h]]
\longrightarrow
V^{\otimes88}(86)\widehat\otimes\mathbb Q[[h]]
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
`HH0` of a tangle subcategory.  None of these sources states or proves the
displayed composite for the MWW coefficient bimodule, nor its compatibility
with the MWW cable quotient.  The local R-matrix equality proves only item 4.

## Missing theorem S: signed three-handle movie comparison

For each of the three lifted sphere classes one needs actual source and target
maps satisfying, in the same coordinates as theorem C,

\[
Q_t\sigma^0Q_s^{-1}=Id_{old}\otimes U+O(h),
\qquad
Q_t\sigma^1Q_s^{-1}=Id_{old}\otimes D+O(h).
\]

The owner lifts and stable-copy ledger determine counts and labels but not:

- pivotal adapters for the two orientation reversals;
- signs for the seven negative sphere slides;
- foam maps for the 49 expanded signed slide bands;
- the actual degree-zero endpoint permutation in qHH0 coordinates;
- simultaneous transport of `W`, the cup vector and the cap covector.

The HJ theorem identifies embedded sphere systems up to slides, but it does
not compute these link-homology maps.  MWW gives the coequalizer once the maps
are known, but does not calculate them for this handlebody.

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
2. explicit chain/foam maps for the compact Hattori coefficient and the 32
   signed sphere moves, from which C and S can be checked directly.

Until both C and S are proved, `ExternalGeometry` has no legitimate
candidate-specific inhabitant and the paper must remain conditional.
