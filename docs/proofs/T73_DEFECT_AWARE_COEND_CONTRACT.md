# T73 defect-aware canopolis/coend contract

Date: 2026-09-05

## Result of the finite typing audit

The selected coefficient is a four-variable profunctor, not a one-variable
Hom space:

\[
 P:\mathcal C_{44}^{\mathrm{op}}\times
   \mathcal C_{271}^{\mathrm{op}}\times
   \mathcal C_{44}\times\mathcal C_{271}
   \longrightarrow \operatorname{Ch}_{\mathbb Q},
 \qquad
 P(T,Z;T',Z').
\]

Its `Z` reduction is the balanced trace

\[
 M_R^z(T,T')=\int^{Z\in\mathcal C_{271}}P(T,Z;T',Z),
\]

with the two \(\mathcal C_{44}\) actions still present.  This is the exact
product-category type used by MWW's one-handle formula.

`geometry/t73_c_defect_coend_typing_graph.json` contains a slim but complete
copy of the source incidence:

- 1260 distinct endpoint nodes on the four typed ports;
- 630 distinct oriented interval edges;
- 176 endpoints on the two \(\mathcal C_{44}\)/Y ports;
- 168 cross-side active edges and eight same-side active edges;
- all 454 residual Z--Z edges;
- both variance labels and both residual \(\mathcal C_{44}\) actions.

Thus no step below may replace 176 Y endpoints by the 174 endpoints of a
\(P_{86}\to P_{88}\) diagram.  Pivotal retyping and any rematching both keep
176 physical Y endpoints.  The difference of two is supplied only by the
separate external cup \(E_{86}\to E_{88}\).

## Correction to the first four-pair audit

The earlier `audit/t73_defect_aware_currying.json` paired the four
\(Y_-\!-​Z_-\) edges with the four \(Y_+\!-​Z_+\) edges in lexicographic
order.  Its first two proposed rows connect `entry-entry` and `exit-exit`, so
those rows are not oriented tangle matchings.  Rows two and three have one
entry and one exit per new arc (row two is merely listed backwards).

There is a unique candidate pairing which simultaneously preserves the
owner and the orientation class.  The new graph records it as

| obligation | old intervals |
|---|---|
| `band:m_2:Y_to_Z` | `m_2:negative:interval:0`, `m_2:positive:interval:310` |
| `band:m_2:Z_to_Y` | `m_2:negative:interval:310`, `m_2:positive:interval:309` |
| `band:r_xy:Y_to_Z` | `r_xy:positive:interval:1`, `r_xy:positive:interval:3` |
| `band:r_xy:Z_to_Y` | `r_xy:negative:interval:1`, `r_xy:negative:interval:3` |

Every proposed new arc is recorded in the order `exit -> entry` and has
cross-side type.  This proves only the boundary combinatorics.  All four
rows remain `UNREALIZED`: no embedded band, foam movie, Blanchet sign,
bidegree, inverse, or homotopy inverse has been supplied.

## Pivotal mate is not a reconnection

In a rigid category, evaluation and coevaluation give Hom adjunctions such
as moving an object across a Hom and replacing it by its dual.  This changes
variance labels but leaves the underlying physical endpoint matching
unchanged.  It is invertible at the categorical retyping level.

A band saddle instead changes which boundary endpoints are connected.  A
single saddle map is generally not invertible.  Even if four explicit bands
changed the source matching to the abstract split matching, their composite
would be a cobordism map, not automatically an isomorphism.  It could be used
in C-H1 only after an inverse or a chain homotopy inverse, all naturality
squares, signs, and degrees were proved.  Hence “four candidate bands” is not
itself a representability proof.

## What a non-literal co-Yoneda route would require

The eight edges refute a *geometric split-sphere proof* of representability.
They do not logically refute an algebraic representability or excision
theorem.  One sufficient replacement would be a homogeneous four-variable
natural chain equivalence

\[
 \alpha_{T,T';Z,Z'}:
 \widehat P(T,Z;T',Z')\simeq
 \operatorname{RHom}_{\mathcal C_{271}}(K T,Z')
 \otimes_{\mathbb Q}^{\mathbb L}
 \operatorname{RHom}_{\mathcal C_{271}}(Z,K T')\{-227\}.
 \tag{R1}
\]

No separating sphere is logically required once (R1), its inverse and its
four naturality homotopies have independently been established.  The
enriched/derived co-Yoneda map then composes the two representables.  What is
not allowed is to infer (R1) merely from canopolis gluing or endpoint counts.

There is a weaker, more direct sufficient contract.  Preserve the connected
source matching and give a homogeneous natural chain equivalence

\[
 \Theta_{T,T'}:
 B_\bullet(\mathcal C_{271};P(T,-;T',-))
 \simeq
 \operatorname{RHom}_{\mathcal C_{44}}(BT,BT')
 \otimes A^{\otimes227}.
 \tag{R2}
\]

Here the left side is a complete bar/arc-algebra model of the derived
\(z\)-coend.  Route (R2) is a connected-kernel trace computation; it is not
an application of co-Yoneda unless a representability theorem is also
provided.  It needs only the two residual \(\mathcal C_{44}\) naturality
homotopies, but it must prove that its finite presentation really models all
\(\mathcal C_{271}\) balanced relations.

Cutting a tangle and assigning Chen--Khovanov bimodules can provide a relative
tensor presentation

\[
 CKh(X_L)\otimes^{\mathbb L}_{H_n} CKh(X_R)
 \simeq CKh(X_L\circ X_R).
\]

Sweetness/projectivity can remove the derived replacement in this gluing
calculation.  It proves that the pieces compose to the original connected
tangle complex.  It does **not** prove that the result is equivalent to the
split Hom complex on the right of (R1) or (R2).  That extra equivalence is the
actual missing mathematical input.

This distinction agrees with the primary sources.  MWW Definition 4.5 and
Theorem 4.7 construct the 3-ball category, its gluing actions, and a
coinvariant/zeroth-Hochschild quotient; they do not state that an arbitrary
connected coefficient bimodule is representable
([author manuscript](https://web.stanford.edu/~cm5/skein.pdf)).  Khovanov's
original tangle construction defines sweet bimodules and composition by
relative tensor, where sweet means projective on each side
([published paper](https://www2.math.ethz.ch/EMIS/journals/UW/agt/ftp/main/2002/agt-2-30.pdf)).
BPW's trace formalism applies to the resulting bicategorical data, but a
trace functor does not manufacture the missing equivalence
([arXiv:1605.03523](https://arxiv.org/abs/1605.03523)).

## Grading contract

Define the comparison in (R2) as a map from the normalized domain
\(\widehat M_R^z\) to
\(\operatorname{RHom}_{\mathcal C_{44}}(BT,BT')\otimes A^{\otimes227}\),
and let its quantum degree be \(\delta_\Theta\).  The all-\(X\) target vector
has degree 227, so its inverse image has degree

\[
 227-\delta_\Theta.
\]

After the already recorded cable shift \(-4\), the actual degree is

\[
 q_C=223-\delta_\Theta.
\]

The literal split calculation corresponds conditionally to
\(\delta_\Theta=0\) and gives 223, but its premise fails for the saved
matching.  No value of \(\delta_\Theta\), and hence no actual value of
\(q_C\), is currently proved.  The historical value 494 is not recovered by
this ledger.

## Executable acceptance gate

`data/T73_C_DEFECT_COEND_FINITE_PRESENTATION.schema.json`,
`data/T73_C_DEFECT_COEND_WITNESS.schema.json`, and
`scripts/verify_t73_c_defect_coend_witness.py` implement a fail-closed
contract.  A future witness must contain:

1. exact ordered bijections to all 1260 endpoints and 630 intervals;
2. a content-hashed complete bar or arc-algebra presentation;
3. either the unchanged connected matching or four explicit oriented band
   movie certificates (never an implicit pivotal rematching);
4. rational source and target chain complexes with \(d^2=0\);
5. homogeneous chain maps \(\Theta,\Theta^{-1}\) and checked homotopies for
   both inverse equations;
6. generator-wise homotopy naturality for both residual
   \(\mathcal C_{44}\) actions;
7. the checked formula \(q_C=223-\delta_\Theta\);
8. a hash-bound Lean module and no-placeholder axiom report for completeness,
   z-balancing, equivalence, naturality, and homogeneity.

The current command reports `OPEN` because no such witness exists.  Passing
the finite typing-graph check is deliberately not treated as passing C-H1.
