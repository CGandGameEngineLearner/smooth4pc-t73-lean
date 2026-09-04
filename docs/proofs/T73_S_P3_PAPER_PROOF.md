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
