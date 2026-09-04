# Attempted paper-level proof of S and P3

Date: 2026-09-04

## Outcome

S and P3 cannot presently be closed from the repository data.  There is a
valid conditional topological argument for P3, and the local rank-two
Frobenius calculation used in S is correct.  The first missing objects are an
ambient identification of the actual post-2-handle boundary and a natural
whole-source factorization of the actual MWW hemisphere maps.  The committed
JSON files do not contain either object.

This note deliberately does not treat a `PASS` string, a hash link, a word in
a free group, an Euler characteristic, or a homology matrix as an embedded
surface or a cobordism map.

## 1. What P3 would require

Let \(W_2\) be the genuine 0/1/2-handlebody obtained after the two proposed
Kirby cancellations.  Let \(S_1,S_2,S_3\subset\partial W_2\) be the genuine
attaching spheres of its three 3-handles.  P3 needs:

1. a proof that the \(S_i\) are pairwise disjoint embedded 2-spheres and are
   the actual attaching spheres;
2. a proof that simultaneous surgery on them gives a specified manifold
   \(Y\cong S^3\);
3. an orientation-compatible homeomorphism or diffeomorphism
   \(a:S^3\to Y\), defining the 4-handle attachment;
4. only then, application of MWW Proposition 3.4 to the empty boundary link.

There is a short conditional proof.  If P0 supplies a diffeomorphism from the
entire Johnson handle decomposition (including its upper handles) to the
Aitchison--Rubinstein Cappell--Shaneson decomposition, then the original three
3-handles and one 4-handle are transported with it.  Their attachment leaves
the attaching sphere of the original 4-handle, hence an \(S^3\), and the
original attaching map supplies \(a\).  Equivalently, once


\[
\partial W_2\cong \#^3(S^1\times S^2)
\]


and the complete upper handlebody are established, the
Laudenbach--Poenaru extension theorem removes ambiguity in the gluing of the
upper 3/4-handles.  This argument is sound but depends on the unproved P0/E13
ambient identification; it is not independently certified by P3.

Correct terminology is important.  In an upside-down *boundary presentation*,
the attaching sphere of a 3-handle appears as the belt sphere of a dual
1-handle, and surgery on all such belt spheres changes
\(\#^3(S^1\times S^2)\) to \(S^3\).  This is not cancellation of an actual
index-1 handle with an index-3 handle in one 4-dimensional handle
decomposition.  The phrases “1--3 cancellation” and “extra 1--3 pair” should
not be used.

## 2. What the current P3 and sphere artifacts actually contain

`geometry/t73_actual_W2_boundary.json` has no triangulation of
\(\partial W_2\), no attaching maps for the five 2-handles, and no
homeomorphism to \(\#^3(S^1\times S^2)\).  It records the desired boundary
type and identification as prose and booleans.

`scripts/build_t73_actual_sphere_system.py` makes the logical gap explicit:

- lines 96--99 assign `embedded_s2_in_reversed_model`,
  `embedded_s2_on_actual_W2`, and `disjoint_from_detector` to `True`;
- lines 107--109 assign pairwise disjointness to `True`;
- lines 124--128 declare the reversed belt spheres to be the actual attaching
  spheres and declare the partial-\(W_2\) identification;
- lines 136--146 declare connected complement and surgery-to-\(S^3\).

The “surfaces” placed at coordinates near
\((64,4441,45401)\), \((80,4441,45401)\), and
\((96,4441,45401)\) are boundaries of three ordinary coordinate cubes in an
abstract chart.  No simplicial embedding of that chart in the actual
\(\partial W_2\) is supplied.

The lower transport file does not repair this.  In
`scripts/build_t73_three_handle_surface_transport.py`, the boundary words,
owner counts, and hashes of 93 factors and 1519 bands are recorded, but lines
103--106 simply assign embeddedness, framing transport, and the relative
surface map.  The verifier at
`scripts/verify_t73_three_handle_surface_transport.py:27--45` checks list
lengths, counts, Euler arithmetic, and the literal string `PASS`; it does not
construct or test an ambient surface map.  Thus the first missing geometric
datum is:

> **G-S1.** A common triangulated model of \(\partial W_2\), together with
> explicit simplicial embeddings of three pairwise-disjoint 2-spheres and the
> detector ball, and a checked ambient map from the pre-cancellation AR
> boundary through every genuine Kirby move to this model.

Alternatively, a conventional Kirby proof identifying the entire lower and
upper handle decompositions would discharge G-S1 without a giant
triangulation.  No such proof is currently present.

Horvat--Jablonowski Theorem 5.3 cannot manufacture G-S1.  It says that, under
its rank hypothesis, a *given geometric basis* of disjoint embedded spherical
classes is equivalent to the actual attaching system.  A unimodular integer
matrix proves only that proposed homology classes form an algebraic basis; it
does not embed the proposed spheres in the actual boundary.  Once G-S1 exists,
that theorem can justify replacement of the attaching system for purposes
invariant under the resulting relative cobordism.  It does not by itself give
an isotopy fixed on the detector ball.

## 3. The local Frobenius computation in S

Let \(A=\mathbb Q[X]/(X^2)\), with


\[
\epsilon(1)=0,\qquad \epsilon(X)=1,\qquad
\Delta(X)=X\otimes X,\qquad
\Delta(1)=1\otimes X+X\otimes1.
\]


For every \(b>0\), induction gives


\[
\epsilon^{\otimes b}\Delta^{b-1}(X)=1,
\qquad
\epsilon^{\otimes b}\Delta^{b-1}(1)=0.
\]


Indeed the first iterated coproduct is \(X^{\otimes b}\), while every summand
of the second contains a tensor factor \(1\).  Therefore the scalar function
in `epsilon_iterated_delta` is correct.  The conclusion remains correct for
\(b=0\) when interpreted as the single counit in the local standard-sphere
model.

This proves only a local 2-dimensional TQFT evaluation.  It does not prove
that either MWW hemisphere map for the actual sphere is
\(\operatorname{Id}\otimes\Delta^{b-1}\), or that restoring all core disks is
\(\operatorname{Id}\otimes\epsilon^{\otimes b}\) on the entire cabled source.

## 4. The first missing categorical theorem for S

`scripts/verify_t73_hemisphere_movies.py` constructs no Khovanov complex and
no MWW map.  It splits the twelve triangles of each abstract cube boundary
into two disks, computes the above two scalar values, then assigns:

- `detector_factorization = PASS_ACTUAL_C_COCONE`;
- identical `endpoint_map_plus` and `endpoint_map_minus` dictionaries;
- `A0_detector_action = identity` and `A1_detector_action = zero`;
- `actual_w2_lasagna_map = True`.

The verifier checks these literal assigned values.  In particular, mutation
testing proves only that changing a stored word is detected.

The missing statement is:

> **C-S1.** For each actual sphere \(S_j\subset\partial W_2\), construct the
> two MWW hemisphere maps on every summand of the cabled one-handle module and
> prove, after the genuine C comparison, a natural commuting diagram in which
> the nontrivial hemisphere is the old-source map tensor the punctured-sphere
> Frobenius map.  The diagram must commute with every beta and psi relation,
> all pivotal/orientation maps, and the passage to the two-handle quotient.

Disjointness of the detector surface and sphere surface is insufficient for
C-S1.  It separates their Morse critical points, but a movie also contains
mixed Reidemeister, braid, pivotal, and reordering maps.  Strict functoriality
removes projective sign ambiguity after both sides have been placed in one
functorial theory; it does not itself identify the global map with a tensor
product or prove compatibility with the MWW quotient.

MWW Theorem 3.7 and Example 3.8 identify the abstract coequalizer and local
essential-sphere relations.  MWW Theorem 3.10 describes the punctured
attaching surface and restored 2-handle cores.  None of these results supplies
C-S1 for the paper's new detector.  Consequently the whole-source equations


\[
\ell(vA_0)=\ell(v),\qquad \ell(vA_1)=0
\]


remain unproved.  This is independent of the geometric gap G-S1 and depends
also on the unresolved C comparison.

## 5. P3 after the sphere surgery

Assuming G-S1 and assuming its three spheres are the transported original
3-handle attaching system, the post-surgery boundary is \(S^3\) by the
original full AR handle decomposition.  Otherwise one needs a checked
3-manifold recognition of the surgered triangulation.  Homology, connected
complement, or an identity pairing with three dual loops does not alone
recognize \(S^3\).

The current `four_ball()` routine in
`scripts/certify_t73_p3_four_handle.py:77--112` correctly constructs an
abstract cubical \(I^4\).  It does not give the attaching map
\(\partial I^4\to\partial W_3\).  The first missing P3 datum after G-S1 is:

> **G-P3.** A concrete orientation-compatible PL homeomorphism from the
> boundary of the supplied 4-ball to the recognized \(S^3\) component of
> \(\partial W_3\), or a transported original AR 4-handle attaching map.

Once G-P3 exists, MWW Proposition 3.4 applies directly because the boundary
link is empty.  Laudenbach--Poenaru also shows that the choice of upper gluing
does not change the closed diffeomorphism type under its hypotheses.  Neither
theorem proves G-S1 or recognizes the boundary from the present metadata.

## 6. Grading and the Manolescu--Neithalath erratum

The published Manolescu--Neithalath paper has an author-posted erratum.  It
corrects the rational normalization by a writhe shift


\[
\operatorname{KhR}_N(L)\otimes\mathbb Q
\cong \operatorname{KhR}^{\mathrm{other}}_N(L)
\{-(N-1)w(L)\},
\]


and, at \(N=2\), corrects equation (6) accordingly.  The erratum says the
rest of that paper is unaffected because it is formulated in the
\(\operatorname{KhR}_2\) convention, but any conversion to an ordinary
Khovanov convention must include this writhe term.

The manuscript's ledger


\[
-44+227+315-4=494
\]


does not cite or discuss this erratum.  A statement that the 11,340-letter
detector braid has total writhe zero is not enough: one must specify the
oriented link diagram and writhe for every actual closure/cable summand used
in the source, target, cup/cap maps, and hemisphere maps.  Thus the grading
cannot yet be reconciled.  The missing datum is:

> **Q-S1.** A convention-by-convention grading table including the corrected
> \(-(N-1)w\) term for every link complex and every cobordism map entering C
> and S, with a proof that the maps in C-S1 have degree zero in the absolute
> lasagna grading.

If all relevant writhe corrections cancel, 494 may remain correct.  The
current repository establishes neither that premise nor an alternative
calculation in a single unconverted \(\operatorname{KhR}_2\) convention.

## 7. Exact status and minimal route to closure

The local Frobenius identity is proved.  Conditional on the entire P0/AR
handle identification, the upper-handle topology and MWW four-handle step are
standard.  An unconditional paper-level S/P3 proof requires, in order:

1. G-S1 (or a complete conventional Kirby proof replacing it);
2. the genuine C comparison, followed by C-S1 on every cabled summand and
   quotient relation;
3. a surgered-boundary recognition or transported original upper handle;
4. G-P3;
5. Q-S1.

The earliest unavailable input is G-S1.  Even granting it, C-S1 is an
independent categorical obstruction.  Therefore no honest modification of
`main.tex` can currently change S or P3 from hypotheses to discharged
theorems.

## 8. Fail-closed G-S1/G-P3 gate

The follow-up audit added the schema
`audit/t73_gs1_gp3_schema.json`, verifier
`scripts/verify_t73_gs1_gp3.py`, and tests
`tests/test_t73_gs1_gp3_gate.py`.

The gate requires an explicit closed tetrahedral complex for
\(\partial W_2\); three triangular sphere subcomplexes; a detector-ball
tetrahedron subcomplex with a checked one-face shelling; an explicit
cut-and-cap surgery trace; the resulting closed triangulation with a
simplicial recognition as the boundary of a 4-simplex; a one-pentachoron
4-ball; and a vertex bijection identifying its derived boundary with the
surgery result. It derives manifold incidence, sphere Euler characteristic
and connectedness, pairwise disjointness, detector disjointness, the
four-ball boundary, and both simplicial isomorphisms from the lists.

The current `geometry/t73_actual_W2_boundary.json` fails at the first gate:
it is metadata, not a `t73_gs1_gp3_witness/v1`, and has no vertices or
tetrahedra. Existing lower-handle data do not determine such a triangulation
mechanically: attaching words and railroad curves omit a triangulated
3-dimensional attaching-region complement and face gluings after each
2-handle. A new handle-triangulation construction would be required.

The explicit normal-sphere cut-and-cap replay primitive is now implemented.
For each sphere it derives a canonical staircase triangulation of a supplied
product neighborhood \(S^2\times I\), checks that this is an actual
tetrahedron subcomplex whose boundary is exactly two sphere copies, removes
it, cones the two copies with distinct new vertices, and compares the exact
closed result. It also checks that these product neighborhoods miss the
detector and the other spheres. A synthetic \(S^2\times S^1\) example and
two mutations exercise this primitive.

This removes one verifier implementation gap but supplies no candidate data.
The current T73 artifact still has no ambient tetrahedra, embedded product
neighborhoods, or step results, so it continues to return `OPEN`.

## 9. Transporting the full AR decomposition

There is a conceptual route that removes the need for a W2 triangulation from
the closed-manifold identification.

### Transport theorem

Let \(\psi:T^3\to T^3\) be a genuine splitting-preserving diffeomorphism,
isotopic to \(f_A\) relative to a neighborhood of the section point. Apply
the Aitchison--Rubinstein construction to obtain the complete framed handle
decomposition \(\mathcal H(\psi)\) of \(\Sigma_A^0\), including its three
3-handles and 4-handle. Suppose the proposed two 1/2 cancellations are
genuine framed Kirby moves and let
\[
F:\mathcal H(\psi)\longrightarrow\mathcal H_J
\]
denote the resulting composition of handle slides and cancellations.
Transport every still-unattached upper-handle attaching map by the induced
boundary diffeomorphisms at each stage. Then the complete resulting handle
decomposition \(\mathcal H_J\) presents a manifold diffeomorphic to
\(\Sigma_A^0\).

This is standard handle calculus: a handle slide changes the attaching map
inside the same manifold, and deletion of a genuine complementary
\(k/(k+1)\) pair is realized by a diffeomorphism. Transporting all remaining
attaching maps along those diffeomorphisms preserves the complete manifold.
No recognition of the intermediate \(\partial W_2\) is required.

If \(X_J\) is *defined* to be the closed manifold of this transported full
decomposition, then \(X_J\cong\Sigma_A^0\) and P3 are immediate. The
post-three-handle boundary is the transported attaching boundary of the
original AR 4-handle, hence \(S^3\), and the transported original 4-handle
supplies its attaching map. Laudenbach--Poenaru is unnecessary when the
actual upper maps are retained. It becomes relevant only if those maps are
discarded and one wishes to replace the upper handlebody by an arbitrary
one after independently proving the required
\(\#^3(S^1\times S^2)\) boundary.

### What this route does not prove

The route is not presently an unconditional proof because its first two
premises are exactly the unresolved P0 content: a genuine global Johnson
diffeomorphism relative to the section and genuine framed cancellation
movies carrying the whole attaching data. Calling hashes or word
substitutions \(F\) would be circular.

More importantly, this route identifies the closed manifold but does not
close S. MWW's three-handle map depends on the embedded attaching spheres in
the actual \(\partial W_2\). Transporting the full AR decomposition gives
well-defined actual spheres and therefore well-defined MWW maps, but the
paper has not computed those maps under its detector.

One may replace the transported sphere system by another complete geometric
basis using relative handle calculus, Horvat--Jab\l{}onowski, or
Laudenbach--Poenaru, once all hypotheses are proved. Naturality then
postcomposes the total quotient map with an isomorphism, so its kernel is
unchanged. This can avoid explicitly drawing the original upper spheres.
It still does not imply
\[
\ell(vA_0)=\ell(v),\qquad \ell(vA_1)=0.
\]
Those identities require the independent whole-source comparison C-S1:
compatibility of the detector with the two actual hemisphere maps, all
mixed braid/pivotal maps, and the beta/psi quotient. Diffeomorphism
invariance and equality of kernels do not manufacture that comparison.

Thus redefining \(X_J\) as the transported full AR decomposition is a
legitimate simplification of E13/P3, not a solution of the obstruction
argument. If the manuscript keeps the independently specified
standard-sphere/P3 object as its definition of \(X_J\), then asserting it is
the transported object without constructing the relative upper-handle
equivalence merely renames the missing identification.

## 10. Retyping the detector as auxiliary data

One can weaken P0 by treating the 44-strand ball and chosen cobordism/class as
auxiliary data rather than as part of the handle presentation. This removes
the need for the unlabelled AR diffeomorphism to preserve a previously fixed
detector ball. It does not, by itself, prove S.

### A valid separated-support lemma

Let \(\mathcal C\) be a strict symmetric-monoidal category of the relevant
tangles and cobordisms, and let \(Z:\mathcal C\to\mathrm{grVect}\) be a
strict symmetric-monoidal functor. Suppose:

1. a source object has a literal ordered tensor decomposition
   \(T=T_B\otimes T_U\);
2. the detector is \(d=d_B\otimes d_U\);
3. the two hemisphere cobordisms have the literal separated form
   \(\operatorname{id}_{T_B}\otimes H^\pm:T_B\otimes T_U\to
   T_B\otimes T'_U\);
4. the comparison from the MWW coefficient object to \(Z(T)\) is monoidal
   and natural for these two cobordisms.

Then
\[
d\,Z(\operatorname{id}_{T_B}\otimes H^\pm)
=d_B\otimes\bigl(d_U Z(H^\pm)\bigr).
\]
Consequently, when \(H^\pm\) is the punctured standard-sphere movie followed
by its \(b\) core caps, its local factor is
\(\epsilon^{\otimes b}\Delta^{b-1}\), giving zero on \(1\) and one on \(X\).
This proves the desired dotted/undotted identities on the whole source.

The proof is exactly strict monoidality and naturality. No transversality
theorem alone gives conclusion (4).

### What can be separated geometrically

Given a finite embedded sphere system in a 3-manifold boundary, a sufficiently
small 3-ball may be chosen in its complement. Thus, if the detector tangle is
freely chosen local data, its abstract 44-strand braid can be placed in such a
ball. Collar uniqueness then places the sphere-attachment movies and the ball
in disjoint boundary collars. This elementary observation does not require a
relative sphere-system uniqueness theorem.

However, the public detector is not merely an abstract local braid. Its 44
lanes are selected passages of the same 2-handle attaching components whose
cocores puncture the transported attaching spheres. After using the MWW
handle formula, the punctured-sphere source has
\(b_j=12578,1824,409\) boundary copies on those components. These endpoints
and the detector endpoints occupy the same cable objects. They need not admit
a literal tensor decomposition \(T_B\otimes T_U\), even if their geometric
arcs lie at different normal levels.

### Exact transversality limitation

Ordinary relative transversality makes two surfaces in a 4-manifold
transverse; because \(2+2=4\), their intersection is generically a finite set
of points, not empty. Removing those points would require additional
intersection-number, fundamental-group, Whitney-disk, and framing data. No
such theorem or data appear here. Likewise, disjoint supports in the
3-dimensional boundary do not imply that the pulled-back core-restoration
surfaces are disjoint in the 4-dimensional 2-handlebody.

At the movie level, interleaved cable endpoints produce mixed braid and
pivotal maps. Strict functoriality controls signs and composition; it does not
turn a linked or braided cobordism into a disjoint tensor product. If an
independent comparison proves that every mixed map is
\(P(I+O(h))\), with the same permutation \(P\) conjugating the detector, then
the \(h^3\) leading coefficient is unchanged. But that is precisely the
unproved naturality/comparison statement C-S1, not a consequence of moving an
auxiliary ball.

### Conclusion

Retyping the ball is useful only at the boundary-geometric level:

- it permits choosing a local braid ball disjoint from the actual upper
  sphere system;
- it does not show that the braid represents the candidate-specific
  two-handle class used by the computation;
- it does not split the shared cable endpoints or core-restoration surfaces;
- it does not supply the monoidal natural comparison needed by the
  separated-support lemma.

If one instead chooses a completely local class whose entire MWW source and
all sphere actions satisfy the four hypotheses above, S follows formally, but
the Burau value 2624 and its descent through the candidate's beta/psi
relations must then be recomputed for that new class. Reusing the old value
would be circular.

## 11. Statewise shadow theorem for the actual MWW surface map

MWW's proof of Theorem 3.10 makes the relevant map more precise than the
informal hemisphere language. For an attaching sphere \(S\), remove a small
disk \(\Delta_+\) and the 2-handle core disks. The remainder is a surface
\(\Sigma_-\subset I\times\partial W_1\) with boundary \(J\) and signed
parallel copies of the attaching circles \(K_i\). MWW's diagram (their
equation (12)) proves that, under the two-handle isomorphism \(\Phi\), the
nontrivial hemisphere map is exactly the map induced on the cabled skein
lasagna module by \(\Sigma_-\). Their equations (14)--(15) say that the
three-handle relations are
\[
\overline\Psi_{\Sigma(n\bullet)}(v)=0\quad(0\leq n\leq N-2),
\qquad
\overline\Psi_{\Sigma((N-1)\bullet)}(v)=v.
\]
Thus MWW already proves compatibility of the actual surface maps with the
beta/psi quotient. What MWW does not prove is compatibility with this
paper's detector.

### Conditional leading-coefficient theorem

Fix a cable state. Suppose the following data exist.

1. A completed statewise shadow functor \(\operatorname{Sh}_h\) is defined on
   every object and every elementary cobordism in a movie for \(\Sigma_-\),
   including births, deaths, saddles, Reidemeister maps, pivotal maps, and
   endpoint braids.
2. \(\operatorname{Sh}_h\) is symmetric-monoidal after reduction modulo \(h\),
   and is natural for all movie moves and for every MWW beta/psi map.
3. The all-owner product-neighborhood data lift to a typed movie in which the
   only interactions between the old detector factor and the punctured-sphere
   factor are invertible braid/pivotal maps
   \[
   P_\nu(I+hK_\nu).
   \]
   There are no mixed births, deaths, or saddles.
4. The family of detector rows is equivariant for the constant permutations
   \(P_\nu\), with the same pivotal convention on source and target.
5. The detector has expansion
   \(D_h=h^3D_3+O(h^4)\).

Then, on the coefficient of \(h^3\),
\[
D_3\,\operatorname{Sh}_h(\Sigma_-)
=D_3\otimes\epsilon^{\otimes b}\Delta^{b-1}.
\]
In particular, at \(N=2\), the once-dotted surface acts as the identity under
\(D_3\), and the undotted surface acts as zero.

### Proof

Choose the supplied typed movie. Strict interchange moves each invertible
mixed event past a local Frobenius critical point. Modulo \(h\), its map is
the symmetry \(P_\nu\); commutativity and cocommutativity of the rank-two
Frobenius algebra allow these symmetries to be moved to the movie's ends.
Hypothesis 4 cancels the resulting endpoint permutations against the
detector rows. Every remaining mixed factor is \(I+hK_\nu\). Since
\[
(h^3D_3+O(h^4))(I+hK_\nu)=h^3D_3+O(h^4),
\]
all such factors are invisible to the divided cubic. The connected
genus-zero punctured-sphere part has one iterated coproduct and \(b\) restored
core counits, hence gives
\(\epsilon^{\otimes b}\Delta^{b-1}\). The local calculation in Section 3
finishes the proof.

Naturality in hypothesis 2 also proves beta/psi compatibility. If
\(\beta,\psi\) is any generating two-handle relation, its square with
\(\operatorname{Sh}_h(\Sigma_-)\) commutes statewise. Applying the already
compatible detector family makes the two sides equal, so the surface identity
descends to the MWW coequalizer rather than merely holding on chosen raw
representatives.

### Exact unresolved obstruction

Interleaving is therefore not an intrinsic mathematical obstruction if the
five hypotheses are available. The repository does not provide them.
Specifically:

- the claimed all-owner decomposition records copy counts, owner words, and
  normal levels, but no typed chronological list of every mixed
  Reidemeister/pivotal/braid event in \(\Sigma_-\);
- the proposed shadow is not constructed as a functor on births, deaths, and
  saddles for the actual MWW coefficient objects;
- no naturality squares with the beta and psi generators are given;
- no proof identifies every constant mixed map with the same permutation
  convention used by the detector row.

The script instead writes the conclusion
`PASS_ACTUAL_C_COCONE` and the identity/zero actions into JSON. Hence
the conditional theorem gives a precise route to S, but the present
all-owner artifact does not satisfy its hypotheses. The first genuinely new
data are the typed \(\Sigma_-\) movie and a statewise monoidal-natural shadow
on all its elementary cobordisms.

## 12. Parameterized typed \(\Sigma_-\) certificate

The finite portion of the typed movie is now implemented in
`scripts/build_t73_sigma_minus_typed.py`.

For each transported surface, the builder reads the complete signed
owner-boundary word and independently reconstructs:

- every negative and positive boundary-copy position for
  \(r_{xy},r_{yz},r_{zx}\);
- the cable-state translations
  \((r^-,r^+)\mapsto(r^-+s^-,r^++s^+)\);
- the stable permutation from chronological endpoint order to
  owner/sign-block order, with its explicit inverse;
- a parameterized event list consisting of zero births, \(b-1\)
  coproduct saddles, one endpoint-permutation block, and \(b\) restored-core
  caps;
- the old tensor factor, the new \(J\)-Frobenius factor, and their target
  cable types.

The counts are \(b=12578,1824,409\). The verifier checks the signed profiles
against the stored all-owner profiles rather than trusting them.

At the type level, a beta generator preserves the cable multiplicities before
and after the surface translation. A psi generator adds one oppositely
oriented pair on a selected component; componentwise addition proves that
psi followed by the surface shift and the surface shift followed by psi have
identical source and target cable vectors. This closes the beta/psi *typing*
part of MWW equations (12)--(15). MWW's construction supplies the induced
surface map on their quotient.

The certificate also proves the local algebra
\[
\epsilon^{\otimes b}\Delta^{b-1}(1)=0,\qquad
\epsilon^{\otimes b}\Delta^{b-1}(X)=1.
\]
A test expands the Frobenius maps directly for \(1\leq b\leq6\), while the
general calculation follows from
\(\Delta^{b-1}(X)=X^{\otimes b}\) and the fact that every summand of
\(\Delta^{b-1}(1)\) contains a \(1\)-factor.

The certificate deliberately retains one open field for each sphere:
`StatewiseShadowNaturality_Aj`. It must supply the shadow maps for the
typed births, saddles, caps, braids, and pivotal events; prove every mixed map
is \(P(I+O(h))\); match the detector's permutation convention; and prove the
actual beta/psi naturality squares. These are maps and equalities, not type
checks, and cannot be generated from the owner word.

Therefore all consequences that follow formally from MWW and the owner
profiles are now closed, while S itself correctly remains open at the
statewise-shadow naturality interface.
