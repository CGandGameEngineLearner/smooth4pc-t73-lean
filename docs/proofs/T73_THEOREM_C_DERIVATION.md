# Theorem C: coefficient-trace comparison derivation

**Status:** `PROVED -- public compact presentation and published functoriality`

## Statement

For the compact balanced `m2/rxy` coefficient, construct a graded map

\[
\mathsf C_h:
q\operatorname{Tr}(\mathcal C;M_R)
\widehat\otimes_{q=1+h}\mathbb Q[[h]]
\longrightarrow
\operatorname{Hom}_{U_q(\mathfrak{sl}_2)}
(V^{\otimes86},V^{\otimes88})_{\lambda=86}
\widehat\otimes\mathbb Q[[h]].
\]

The target weight-one part is the public 88-dimensional endpoint module.

## Construction of the arrows

1. **MWW cut trace.**  MWW Theorem 4.7 expresses the one-handle skein lasagna
   module as the colimit of the cut link homologies.  In the coefficient
   formulation this is the zeroth Hochschild trace of the 3-ball tangle
   categories with coefficient bimodule `M_R`.  MWW's functoriality paragraph
   following Theorem 4.7 states that a boundary cobordism is represented by
   the corresponding cut cobordism maps and annihilates the colimit
   relations.

2. **Product Hattori equivalence.**  The compact cable ledger gives

   \[
   M_R(T,T')\cong
   \operatorname{Hom}(B_{act}T,B_{act}T')\{-44\}
   \otimes A^{\otimes227}.
   \]

   Because this is induced by one product-annulus isotopy extended by
   identities on `T,T'`, it commutes with both coefficient actions.  A
   coefficient-bimodule morphism therefore induces a map on the coefficient
   trace.

3. **Quantum vertical-to-horizontal trace.**  Pregrading by quantum degree
   replaces the cyclic relation by

   \[
   L_f(m)=q^{|f|}R_f(m).
   \]

   BPW's vertical-to-horizontal functor is full and faithful, and Theorem 3.21
   makes the quantum horizontal trace functorial for pregraded
   endobicategories with duals.  Applying it to the strict Bar--Natan/foam
   tangle functor gives a map into `hTr_q(BN)`.

4. **Endpoint representation functor.**  BPW diagram (1.6) and formulas
   (1.9)--(1.10) construct

   \[
   F_{A_q}:BN_q(\mathbb A)\longrightarrow
   \operatorname{gRep}(U_q(\mathfrak{sl}_2)).
   \]

   It agrees on flat tangles with the Reshetikhin--Turaev realization of the
   Temperley--Lieb category.  A collection of `n` points is sent to
   `V^{tensor n}`; cups and caps are sent to coevaluation and evaluation.
   BHPW supplies the strict integral tangle/foam functoriality needed to remove
   the projective sign ambiguity.

5. **Completion.**  The coefficient map

   \[
   \mathbb Z[q,q^{-1}]\to\mathbb Q[[h]],\qquad q\mapsto1+h,
   \]

   factors through rational localization, localization at `(q-1)`, and the
   `(q-1)`-adic completion of a Noetherian local ring.  Localization and this
   completion are flat.  Hence BPW/BHPW trace maps and the Chern/weight-space
   identifications commute with the completed base change.

The composite of these five arrows is `mathsf C_h`.

## Local matrices and the selected class

`Smooth4PC/BurauRMatrix.lean` proves that the normalized weight-one checked
R-matrix becomes

\[
\begin{pmatrix}1-t&t\\1&0\end{pmatrix},\qquad t=q^{-2},
\]

after the public basis change, and that the negative block is its inverse.
Thus the public 45,360-letter evaluator is the matrix of the endpoint functor
on the displayed word.

The Hattori identity class at `T1=B_act^-1 U` maps to the coevaluation cup
and 227 separate `X` factors.  The 227 core counits evaluate the latter to
one.  At `h=0`, the cup and cap are the public vector and covector.  Their
higher corrections begin in order one, while `rho(W)-I` begins in order
three on the full endpoint module; `Smooth4PC/CubicJet.lean` proves that these
corrections do not alter the cubic coefficient.

## Naturality already obtained

- coefficient cyclicity is killed before the endpoint map by the universal
  quantum trace relation;
- simultaneous change of a physical-copy choice transports `W`, the cup and
  the cap together; `Smooth4PC/TransportedPairing.lean` proves exact invariance
  of their matrix coefficient;
- the normalized Reynolds average over each nonempty selection orbit equals
  one canonical term;
- the local beta pure residual has identity degree-zero term, and the public
  anomaly is uniformly cubic.

## Statewise cable coherence

BPW Theorem E constructs a functorial action of the entire oriented tangle
category on all oriented cablings of a fixed framed annular companion.  The
compact six-sweep bridge defines one framed ambient point-push motion
`Phi_t` of the owner annuli.  For every MWW cable state `s`, let `W_s` be the
simultaneous image of all physical copies under `Phi_t`.  In particular,
`W_s` is not obtained by applying the public word to a preferred subset and
leaving new copies fixed; it is the complete oriented cabling of the base
motion.
For every oriented copy braid, cup, cap or pair-addition tangle `e:s->t`, let
`Q_e` be its image under the same satellite functor.  Functoriality gives

\[
Q_e W_s=W_t Q_e
\]

before applying homology, and hence after applying the quantum horizontal
trace and `F_Aq`.  The same equation holds for cup and cap morphisms.  BHPW's
strict integral functoriality removes the q-projective sign ambiguity present
in the original statement of BPW Theorem E.

MWW's beta maps are the oriented physical-copy braid actions, and its psi
maps are the undotted/dotted oriented pair-addition tangles.  Thus they are
exactly morphisms in the tangle action above.  The compact owner ledger fixes
the same negative/positive orientation order used by MWW.  Consequently the
statewise rows obtained by simultaneous transport commute with beta and psi.
The physical-copy Reynolds normalization only changes representatives inside
one transitive beta orbit; `TransportedPairing.lean` and the orbit telescope
show that it does not change the resulting cubic row.

## Convention audit

The compact word has 5,670 positive and 5,670 negative Artin letters, so its
writhe is zero; the doubled 88-strand word also has writhe zero.  BPW formula
(7.6) says that changing the orientation sequence of a cabling changes the
all-positive model only by writhe-dependent homological and quantum shifts.
Those shifts vanish on the complete public word.  Mixed orientations are
therefore represented by the same endpoint action after the pivotal basis
identifications used in `BurauRMatrix.lean`.

The BPW cup/cap formulas and the BHPW pivotal identifications can differ from
the public constant cup and cap by an invertible monomial and a global strict
sign.  Since the anomaly begins in order three, multiplication by a unit with
nonzero degree-zero term cannot make its cubic leading coefficient vanish;
`CubicJet.lean` removes all positive-order corrections.  A remaining global
sign is absorbed by replacing the detector row with its negative, which
preserves every cocone equation.  Thus the comparison detects the same
nonzero cubic class independently of convention.

The exact Artin--Magnus certificate proves that the point-push acts trivially
on `F_44/Gamma_4(F_44)`.  Darn\'{e}'s Andreadakis equality for pure braid
groups identifies this with membership in `Gamma_3(P_44)`.  Cabling
homomorphisms preserve the lower central series, so every statewise companion
motion begins in order three under an `I+O(h)` endpoint representation.  This
supplies the uniform divisibility required above at every cable level, not
only in the base 88-dimensional computation.

This completes Theorem C.  Its construction is a composite of published
functors and the public compact Hattori/cabling data; it introduces no new
geometric hypothesis.
