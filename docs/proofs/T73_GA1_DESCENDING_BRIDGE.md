# T73 actual-Gompf to DIAGRAM bridge

**Status:** `HISTORICAL PD ROUTE SUPERSEDED BY T73_COMPACT_AR_PRESENTATION.md`

The argument below has not been independently instantiated from the public
repository. Its load-bearing PD diagram, builder, cut/framing records and
move data are referenced only by historical local paths and hashes. See
[`../GEOMETRIC_INSTANTIATION_AUDIT.md`](../GEOMETRIC_INSTANTIATION_AUDIT.md).

This note proves that the curves used by the TH1, TH2 and THXY calculations
are a framed Kirby presentation of the actual reduced
Cappell--Shaneson/Gompf handlebody.

The claim is existential and deliberately narrow:

> There is a legitimate product choice for the cancellations
> (t,h_CS) and (x,m_1) such that the resulting whole labeled framed Gompf link
> is Kirby-equivalent to the frozen Christoffel DIAGRAM link, with every
> owner/cocore label transported through the equivalence.

It does not assert that every diagram with the same relator words is actual.
The actual-side input comes from Aitchison--Rubinstein's product-ribbon handle
construction; the global-descending certificate is used only on the DIAGRAM
side.

## 1. Frozen finite input

The source objects and their SHA-256 identities are:

- [`cs_presentation.py`](../../evidence/public_geometry/cs_presentation.py)
  B20BDFF6FBF2A0E629083E2E62DD1DDF9172A4E8893311CE122FFC4FEB388DFA
- [`t73_eps0.erkmo.json`](../../evidence/public_geometry/t73_eps0.erkmo.json)
  6DF4D7906ADB18BA2D3237D4B49F8985A5B18D8C39FF522AD6498F2369803FCB
- [`CUT_OBJECT.json`](../../evidence/public_geometry/CUT_OBJECT.json)
  4E1C4564ED98F30EAEB0A1AEAAD95ACAB5AD7B226C79B7D5BF3F259E8B56F541
- [`BASE_INTERACTION_SUPPORT.json`](../../evidence/public_geometry/BASE_INTERACTION_SUPPORT.json)
  2D9E4760F836D9E04E6E0024CAE03A3DBB49A74FF5D129756F25450B30F10F7C
- [`NORMAL_FIELD_MOVIE_CERT.json`](../../evidence/public_geometry/NORMAL_FIELD_MOVIE_CERT.json)
  B2E97EB0981036768B8F1C1D5EF16F8817EC1A7B951B6B32DBA2F9211FFD725A
- [`t73_reduced_billiard.pd.json`](../../evidence/public_geometry/t73_reduced_billiard.pd.json)
  E6912A64457557469E5C691B4D57ABDBBF4C45ADB05492777C574223D0C06F8A

The PD traversal is recomputed in linear time by
`scripts/verify_t73_global_descending.py`; its pinned output is
`T73_EVIDENCE_GLOBAL_DESCENDING.json`. It does not trust the summary counts
or status fields. It also identifies actual y/z gate endpoints, computes the
forbidden cyclic-base intervals from every self crossing, and selects a
gate-aligned descending basepoint. The allowed gate-basepoint counts are
3, 6, 3 and 3 for r_xy, r_yz, m_2 and m_3 respectively.

Delete the non-scientific meridian spectators.  Cut the reduced genus-two
one-handlebody along the complete y/z disk system.  The result is a 3-ball
with exact marked endpoints.  For every passage the records freeze

    (owner, letter index, entry/exit)

and the cyclic successor pairing

    exit(i)  <->  entry(i+1).

The exhaustive traversal gives the following self-crossing counts:

| component | self crossings |
|---|---:|
| r_xy | 9 |
| r_yz | 3 |
| m_2 | 64631 |
| m_3 | 1445582 |
| r_zx | 0 |

At every self crossing, the branch encountered first in the frozen cyclic
traversal is the over-branch.  Every mutual crossing obeys one strict component
height order

    r_xy > r_yz > m_2 > m_3,

with no reverse crossing.  In particular, all 608786 m_2--m_3 crossings have
m_2 over m_3.  The successor table includes the last-to-first return
connector, so no unexamined closing arc remains.

These are stronger facts than vanishing pairwise linking or componentwise
self-descending.  The latter two would admit pure-braid and Borromean
counterexamples.

## 2. Relative global-descending lemma

Let T be a marked tangle in a 3-ball.  Suppose:

1. its boundary endpoints and their pairing are fixed;
2. its components have a total order;
3. along each component, the earlier branch is over at every self crossing;
4. an earlier component is over a later component at every mutual crossing.

Then T is ambient-isotopic relative to the boundary to the unique
boundary-parallel trivial tangle with that marked endpoint pairing.

Proof.  Put the first component in a thin top layer.  Traverse it from its
marked initial endpoint.  At each crossing, the already traversed segment is
above every untraversed segment, so it can be pushed into a boundary collar
without crossing the rest.  This produces a bridge disk disjoint from the
remaining tangle.  Remove that component and repeat in the next layer.
Induction gives pairwise disjoint bridge disks for all components and hence a
relative ambient isotopy to the marked trivial tangle.  The fixed cyclic
successor pairing supplies the return connector when the cut disks are glued
back.  QED.

Applying the lemma to the data in Section 1 puts the DIAGRAM cut tangle into a
reference marked trivial tangle with all component labels tracked. It does not
assert a pointwise-fixed isotopy of the r_xy/r_yz/r_zx components.

## 3. Actual product-ribbon source

Use Aitchison--Rubinstein, Fibered knots and involutions on homotopy spheres,
Contemporary Mathematics 35 (1984), pages 1--74. The scanned source is

    D:/tmp/t73_g1_literature/four_manifold_theory_1984.pdf
    SHA-256 6F7E95B8266876774667AD40EA3DE964B165680D6789A34E49BF598C3AE04DF0.

Their pages 5--7 construct the actual mapping-torus two-handles. For each
coordinate spine circle C_i, the attaching circle H^2_ii is the union of

- the bottom C_i piece;
- the top rho(C_i) piece;
- two arcs lambda_i and mu_i across the base one-handle.

The four pieces form the core circle of the displayed annular neighborhood.
The corresponding bottom/top strips and lambda/mu rectangles form the
annular framing neighborhood. Thus, with the orientation convention used by
the frozen builder, the complete attaching word is

    m_i = t phi_A(x_i) t^-1 x_i^-1,

and the product annulus, not a blackboard integer, defines its framing.
The three components are constructed simultaneously from disjoint product
disks and cones.

Their pages 8--9 use the coordinate spine C_i parallel to the x_i-axis and
write the linear action as phi_A(v)=Av. This is the same column convention as
the frozen builder. Page 17 gives a second, direct description valid for the
linear mapping-torus diagrams: in R^3, push the three coordinate axes in the
(1,1,1) direction to form product strips. Linearity of A makes the two image
boundaries of each strip parallel. After projection to T^3 these are the
actual product annuli and determine the fiber-band framings.

There is a necessary distinction between the original straightened linear
map phi_0 and the handlebody-preserving representative phi_1 used in the
page-6 diagram. Reparametrize the Aitchison--Rubinstein isotopy as rho_u,
u in [-1,1], from phi_0 to phi_1, relative to the fixed section neighborhood.
Choose the reparametrization stationary near both endpoints. This global
isotopy is not silently discarded. Put

    g_u = rho_u phi_0^-1.

Thus g_-1 is the identity and g_1 phi_0=phi_1. With their mapping-torus
convention (x,-1)~(phi(x),1), the formula

    F([x,u]_phi_0) = [g_u(x),u]_phi_1

defines a diffeomorphism of mapping tori: at the identified ends, the equality
phi_1 g_-1=g_1 phi_0 is exactly the well-definedness condition. It fixes the
bottom fiber; stationarity near the ends makes F and its displayed inverse
smooth across the quotient seam. Both rho_u and phi_0 are the identity on the
fixed section ball, so g_u is the identity there and the base handle/section
are fixed pointwise. Pull the page-6 handle decomposition back by F. The bottom
C_i pieces and the standard one-handlebody are unchanged, while each top
piece satisfies

    g_1^-1(phi_1(C_i)) = phi_0(C_i).

The lambda/mu rectangles and the full framing annuli pull back with it.
Consequently this is a legitimate actual handle decomposition of the original
linear mapping torus whose top cores are the linear phi_0(C_i), not an
unsupported claim that the global Heegaard-feeding isotopy left those cores
pointwise fixed.

The pulled-back lambda/mu traces need not be trivial relative to the frozen
cut disks; they may carry a pure motion braid. No such triviality is used.
The suspension construction restricts on the 0+1 subhandlebody to an actual
orientation-preserving boundary diffeomorphism H. With the source and target
0+1 subhandlebodies identified with the standard

    W1 = boundary-connected-sum of four copies of S1 x B3,

H carries the complete labeled framed attaching link: the gates, h_CS, all
three r-components, all three m-components, their orientations, owner/cocore
labels and the product framings. This is not inferred from a common relator.
It is the restriction of the displayed suspension diffeomorphism applied to
the entire AR handle decomposition.

By the Laudenbach--Poenaru extension theorem, every orientation-preserving
self-diffeomorphism of

    boundary(W1) = connected-sum of four copies of S1 x S2

extends over W1. Therefore attaching the two-handles along the actual
pulled-back link or along its H-transport gives diffeomorphic W2
handlebodies, with owner/core labels and framings transported. A nontrivial
pure braid in the lambda/mu track is presentation gauge under this
whole-boundary equivalence; it need not be proved zero. This is the reason the
claim is whole-link Kirby equivalence rather than isotopy relative to frozen
cut disks or commutator components.

The source is Laudenbach--Poenaru, A note on 4-dimensional handlebodies,
Bulletin de la Societe Mathematique de France 100 (1972), 337--344. A modern
statement using exactly this extension appears at
Horvat--Jablonowski, [arXiv:2510.20282](https://arxiv.org/abs/2510.20282).

For

    A = [[0,269,1240],[0,41,189],[1,0,32]],

the frozen C11 path p+s A e_i is a simultaneous ambient translate, followed
by arbitrarily small distinct normal offsets, of the top centerlines of those
actual annuli. Its exact hyperplane-crossing sequence is the C11 word. An
exact rational check gives no intersection of any centerline with the fixed
point 0. Compactness gives positive distance from 0, so the strips and the
support ball for the minimal straightening can be chosen disjoint. Neither
the centerline embeddings nor their product normals change.

## 4. The two product cancellations

First cancel the base one-handle t with h_CS. Aitchison--Rubinstein page 7
identifies this as a complementary geometric one/two-handle pair. For
epsilon=0, choose the product cancellation, so no twist is deposited. Give
every other component an event-labelled parallel strip at a distinct normal
level. This deletes t and t^-1 from every m_i and transports the entire
product framing.

The first column of A is e_3. Therefore, after the first cancellation,

    m_1 = z x^-1.

It geometrically traverses the x one-handle once and is a complementary pair.
Choose its product cancellation. The parallel rerouting strips implement
x->z simultaneously on every surviving component, without intersections.
Consequently

    r_xy -> [z,y],
    r_yz -> [y,z],
    r_zx -> [z,z].

The last word is z z z^-1 z^-1. Two nested product bigons remove the inner
and outer inverse pairs. They give an actual disk disjoint from the remaining
link, and the transported product normal gives zero relative framing.
Thus r_zx becomes the required split zero-framed unknot by geometry, not by
the empty word alone.

The same two cancellations give the full frozen reduced words:

- m_2 has length 311 and net (y,z)=(40,269);
- m_3 has length 1460 and net (y,z)=(189,1271).

## 5. Identification with the frozen DIAGRAM

Use the whole-boundary equivalence of Section 3 to work in the transported
product representative, carrying all labels and framings with it. Perform the
two cancellations of Section 4 inside that representative. Only now cut the
reduced y/z one-handlebody along its complete disk system. The transported
product link and the frozen DIAGRAM have the same marked endpoints, cyclic
successor pairing, component order and full relator traversal.

On the transported product side, the disjoint Aitchison--Rubinstein
neighborhood disks and cone attaching tubes, together with the chosen product
rectangles, are pairwise-disjoint bridge rectangles. The two cancellations
extend them in private product lanes. Hence they directly give a marked
boundary-parallel tangle. On the DIAGRAM side, Sections 1--2 prove that the
exhaustive global-descending conditions put the cut tangle into the same
marked boundary-parallel reference tangle.
Therefore the whole links are component-preservingly ambient-isotopic after
regluing. This conclusion uses product geometry on one side and the
global-descending theorem on the other; it is not inferred from word equality.
It does not claim that the commutator components are pointwise fixed.

Extend the isotopy over tubular neighborhoods. Equip the DIAGRAM with the
push-forward of the actual product-annulus framings. This proves a framed
Kirby equivalence of the whole handlebody while retaining the owner/core
labels under the component-preserving isotopy.

The earlier two-completion result for Omega remains correct: the frozen
emitter records alone cannot recover a blackboard winding. It is irrelevant
to this proof because the framing is now supplied in the forward direction by
the actual Aitchison--Rubinstein annulus. A scan of the carrying proof,
one-cup quotient and three chosen-sphere arguments finds no consumption of a
numeric m_2/m_3 blackboard framing, the writhes 267/1270 or Omega.

## 6. Independent algebraic backup

The finite verifier

    D:/tmp/g1_road_c/kirby_slide_lift.py

has SHA-256

    94CA0240D0424F90DDF36D2B0483EE52BD3D4369DAE17DB8BBD4DBE002B1E519.

It verifies the AR matrix/basis convention by an exact integral conjugacy and
also constructs a 125002-step post-cancellation commutator-slide stream from
the billiard words to the collected words. This stream is an independent
same-handlebody check only. It is not load-bearing, because using it as the
main bridge would require transporting the chosen-sphere H_2 coordinates.

## 7. Consequence and boundary

The Christoffel DIAGRAM calculations are calculations in a genuine reduced
framed handle presentation of X(41,189,73). The three hardened chosen spheres
therefore lie in the actual W2 used by the proof, and their determinant-one
class matrix is an actual H_2-sphere basis.

What is not claimed:

- canonicality for every possible cancellation choice;
- recovery of a particular historical cancellation movie;
- certification of the emitter's declared numeric m_i framing;
- equality with the independent blackboard writhes 267 and 1270;
- formal or external acceptance of the full counterexample proof.
