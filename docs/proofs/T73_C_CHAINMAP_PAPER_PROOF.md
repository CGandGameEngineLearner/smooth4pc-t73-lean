# C coefficient comparison: maximal valid construction and present blockers

Date: 2026-09-04

## Verdict

The cited BPW/BHPW results do permit a precise *conditional* construction

\[
q\operatorname{Tr}(\mathcal C;M_R)
\longrightarrow
\operatorname{Hom}(E_{86},E_{88}),
\]

but only after an actual homogeneous dg coefficient-bimodule comparison has
been constructed.  The repository does not presently contain that comparison.
It also does not contain the statewise comparisons needed for all MWW cable
states.  Therefore C-H1 and the whole-source beta/psi descent remain open.

The endpoint pivotal coefficients and the comparison grading cannot be derived
from the current files either.  A fail-closed schema and checker now record the
primitive data needed before either the pivotal chart or absolute degree 494
may be certified.

## The conditional chain-level construction

Work over \(R_q=\mathbb Q[q,q^{-1}]\).  Use one strict Blanchet--Khovanov
foam model throughout.  Let \(\mathbf F_2^{dg}\) be its dg 2-category and let
\(\mathcal C\) be the relevant pregraded enriched morphism category of tangle
complexes.  At the selected cable state the actual MWW one-handle source is a
coend for a product of 3-ball tangle categories, with coefficient bimodule

\[
M_R(T,T')=\operatorname{KhR}_2(R\cup T'\cup\overline T).
\]

It is not enough to rename this product category as the category of tangles
\(P_{86}\to P_{88}\).  One needs a dg functor \(F\) and homogeneous chain
equivalences, natural in both variables,

\[
H_{T,T'}:C_R(T,T')\simeq
\underline{\operatorname{Hom}}_{\mathbf F_2^{dg}}(FT,FT')\{-44\}
\otimes A^{\otimes227},
\qquad A=\mathbb Q[X]/(X^2),
\tag{C.1}
\]

such that for every homogeneous \(f:S\to T\), \(g:T'\to U\), and coefficient
chain \(m\), the following are equal as chain maps, not merely on dimensions:

\[
H_{S,T'}(f\cdot m)=(Ff)^*H_{T,T'}(m),\qquad
H_{T,U}(m\cdot g)=(Fg)_*H_{T,T'}(m).
\tag{C.2}
\]

Given (C.1)--(C.2), apply the 227 homogeneous circle counits and then the
inverse transport by \(F\).  This is a dg coefficient-bimodule morphism from
\(C_R\) to the regular coefficient.  It sends
\(L_f(m)-q^{|f|}R_f(m)\) to the corresponding quantum cyclic relation, hence
induces a map on the coefficient quantum trace.

The regular trace of the morphism category is the quantum vertical trace of
the foam bicategory.  BPW Section 3.4 (in particular Proposition 3.12) gives
the canonical fully faithful functor from vertical to horizontal trace.  On a
diagonal coefficient it sends the trace class of a 2-morphism
\(\alpha:T\Rightarrow T\) to the horizontal square \([T,\alpha]\), a morphism
from the horizontal-trace identity at \(P_{86}\) to that at \(P_{88}\).

Apply the BHPW strict foam/tangle 2-functor and its quantum Hochschild shadow.
For the weight \(86\) block, BHPW Corollary E identifies the two endpoint
self-coefficient groups by the Chern character with

\[
E_{86}=(V^{\otimes86})_{86},\qquad
E_{88}=(V^{\otimes88})_{86}.
\]

The first has rank one and the second rank 88.  Thus the composite really has
the claimed target \(\operatorname{Hom}_{R_q}(E_{86},E_{88})\).  BPW
Propositions 3.20--3.21 explain the universal quantum preshadow and its
functoriality; BHPW Theorem 4.6 removes the projective sign after the source
movies have actually been placed in its strict model.  None of these results
constructs (C.1) or proves (C.2).

This is the maximal rigorous paper proof currently available: it proves the
comparison from the explicitly stated dg-bimodule input, not from the existing
`PASS` fields.

## Why the current artifacts do not supply (C.1)--(C.2)

`scripts/certify_t73_c1_cut_link.py` reconstructs 44 endpoint paths and 227
circle locations at the selected \(m_2+r_{xy}\) state.  Its `H` movie stores
only the hashes of a start polyline and an end polyline.  It does not store a
foam movie, chain complexes, differentials, chain maps, homotopies, or signs.

`scripts/certify_t73_c2_comparison.py` explicitly says that its output is not
a chain-level Blanchet--Khovanov complex of the actual cut.  Its two “action
squares” are boxes placed to the left and right of the detector ball.  They do
not define the maps in (C.2) for arbitrary \(f,g,m\), and they do not compare
the full product of MWW 3-ball categories with the \(P_{86}\to P_{88}\)
morphism category.

The all-cable claim has an additional data gap.  The stored 44 product
rectangles cover only the selected owners \(m_2\) and \(r_{xy}\).  At general
cable states the word counts also require 189 \(y\)-passages for \(m_3\) and
two for \(r_{yz}\), together with their \(z\)-partners and residual circles.
No corresponding simultaneous framed isotopy or dg map is supplied.  Merely
putting the counts

\[
n_y=(42,189,2,2,0),\qquad n_z=(269,1271,2,2,0)
\]

in a certificate does not construct these missing maps.

Consequently the Reynolds argument is only an abstract leading-order model.
`Smooth4PC/ReynoldsCableCocone.lean` proves that the average of values already
assumed constant is that constant.  It does not prove that an actual MWW beta
movie has constant cubic value.  Likewise the abstract defect-head model
postulates the dotted/undotted maps; it does not identify them with every
actual MWW \(\psi_i^{[d]}\).  The two independent core counits live after
two-handle attachment and cannot be used as a raw retraction between W1 cable
summands without first proving the very quotient compatibility in question.

## Pivotal coefficients and the number 2624

The current builder assigns

```text
pivotal_sign = 1
q_power = 0
```

for every physical endpoint and separately inserts the signs in the displayed
cup and cap.  Orientation alone does not determine these values.  BPW (A.4)
uses a basis-dependent identification \(V^*\cong V\), including a
\(q^{-1}\) coefficient on one dual basis vector; BPW (A.6) then gives ordered
evaluation and coevaluation terms with coefficients \(q,1,1,q^{-1}\).
Blanchet red-facet detachment can introduce signs fixed by a local normal.
The repository does not record the ordered sequence of these duality moves,
the nesting data, or the sign-producing local normals.

There is one useful robustness check.  In the standard BPW constant term,
both cup terms and both cap terms have positive sign.  Re-evaluating the
committed Burau word with

\[
u=e_2+e_{87},\qquad \ell=e_{87}^*+e_2^*
\]

still gives \([\varepsilon^3]\ell(\rho(W)-I)u=-328\), hence \(2624\) after
\(\varepsilon=(1+h)^{-2}-1\).  The numerical cubic is therefore robust under
this particular correction.  This does not identify it with the MWW
functional until (C.1), the actual duality chart, and the all-state cocone are
proved.

## Absolute grading

Inside the intrinsic framed \(\operatorname{KhR}_2\) convention, the formal
ledger has sourced contributions

\[
-44+227+(44+271)-4=494.
\]

Here \(-44\) removes the MWW 3-ball Hom normalization, the 227 labels \(X\)
have degree \(+1\), Theorem 4.7 contributes the one-handle gluing shift 315,
and MWW Definition 3.1 contributes the selected cable shift \(-4\).

What is not established is that the comparison to the BHPW endpoint model is
homogeneous with no additional conversion shift.  The Manolescu--Neithalath
erratum corrects the rational conversion to
\(\{-(N-1)w\}\).  The detector braid has writhe zero, but that alone does not
give the writhe and framing convention for the coefficient closure, Hattori
target closure, cup, cap, and every statewise beta/psi comparison.

The new command

```text
python3 scripts/check_t73_c_pivotal_grading_inputs.py
```

therefore exits 2 and reports `OPEN`.  Its schema requires 88 ordered
\(V/V^*\) duality charts, the BPW (A.6) cup/cap terms, all Blanchet local
normals, and a diagram-by-diagram writhe ledger using the corrected
\(-(N-1)w\) formula.  It will not certify degree 494 merely because the four
integers add to 494 or because the detector word has writhe zero.

## All-owner primitive product prefix (resolved in the normalized collar)

`geometry/t73_all_owner_product_primitives.json`, rebuilt by
`scripts/build_t73_all_owner_product_primitives.py`, now binds every surviving
post-cancellation event to the Johnson spine, the AR link, and the registered
zero-twist cancellation bands.  In owner order
\((m_2,m_3,r_{xy},r_{yz},r_{zx})\), it verifies

\[
n_y=(42,189,2,2,0),\qquad n_z=(269,1271,2,2,0).
\]

Every surviving z source occurs exactly once, either as the successor of a y
source in one of 235 primitive product rectangles or as one of 1309 residual
z circles.  The \(m_3\) free reduction retains the exact cancelled pair
`c2:letter:1460` and `m_3:C_i`; the two \(r_{zx}\) product bigons are likewise
retained.  The selected Johnson \(m_3\) representative has the same signed
letter multiset and length as the compact word but a different order, so the
artifact uses the explicit Johnson order rather than silently substituting the
compact word.

There is one necessary orientation correction.  The actual cut traverses each
dual-cell boundary opposite to the stored disk-boundary order, whereas the
x-cancellation ledger records slide orientations in the stored forward order.
Thus a dual-cell x-to-z replacement has orientation equal to the negative of
the stored slide orientation.  With this correction the exact oriented words
are

\[
r_{xy}=zyZY,\qquad r_{yz}=yzYZ,\qquad r_{zx}=1.
\]

For arbitrary cable multiplicity \(r_i\), choose inside each primitive product
neighborhood of width \(w_i\) the levels

\[
\delta_{i,j}=w_i\frac{2j-r_i+1}{2(r_i+1)},
\qquad 0\leq j<r_i.
\]

They lie strictly between \(-w_i/2\) and \(w_i/2\), and consecutive levels
differ by \(w_i/(r_i+1)>0\).  Hence the parallel copies are disjoint and retain
relative twist zero.  Their counts are

\[
\sum_i r_i n_{y,i},\qquad
\sum_i r_i(n_{z,i}-n_{y,i})
\]

for rectangles and residual circles respectively.  This proves the
all-multiplicity statement inside the normalized Johnson product collar.
It remains conditional on an explicit P0 ambient inclusion of that collar and
does not construct the dg foam maps in (C.1)--(C.2).

## Point-push gauge and naturality

Let (A=ho_h(W)).  A genuine change of endpoint coordinates by an
invertible (P) transports operator, cup, and cap simultaneously:

\[
A\mapsto PAP^{-1},\qquad u\mapsto Pu,\qquad
\ell\mapsto\ell P^{-1}.
\]

BPW/BHPW naturality therefore gives the exact identity

\[
(\ell P^{-1})(PAP^{-1}-I)(Pu)=\ell(A-I)u.
\tag{C.3}
\]

Thus naturality does not force the cubic to vanish; it makes it invariant
under simultaneous conjugation.

Changing the chosen point-push *loop* is different.  Precomposing it by a
returned pure loop (P), with the fixed cup and cap unchanged, replaces (A)
by (ho_h(P)A).  If (P,W\in\Gamma_3), then

\[
\rho_h(P)=I+h^3K_P+O(h^4),\quad
\rho_h(W)=I+h^3K_W+O(h^4),
\]

so

\[
K_{PW}=K_P+K_W,\qquad
D_3(PW)-D_3(W)=\ell K_Pu.
\tag{C.4}
\]

Taking the equally supported inverse loop (P=W^{-1}) gives a concrete
counterexample: (W^{-1}W=1), its endpoints and first-order normals return
and its writhe is still zero, but the cubic changes from 2624 to zero.  This
is replayed by `scripts/audit_t73_point_push_gauge.py` and recorded in
`audit/t73_point_push_gauge.json`.

This does not contradict BPW: a chosen point-push surface may act
nontrivially, and a noncanonical linear detector may still prove a class is
nonzero if its quotient descent is independently established.  It does show
that the current P0 recipe---normalize the points, choose the six-sweep loop
by isotopy extension, and return them---does not make 2624 a
presentation-independent consequence of the static AR collar.  A repair must
either declare (W) to be an auxiliary chosen endpoint self-cobordism, which
cannot discharge P0 or (C.1), or construct a relative cobordism class selected
by the embedded AR geometry and prove that every permitted presentation
change is only the conjugation (C.3), never the multiplication (C.4).

## Minimum data required to close C

1. The precise MWW product source category at every cable state, including
   its endpoint partitions and the coefficient complex \(C_{R_r}\).
2. A finite strict foam movie defining every \(H^r_{T,T'}\), with chain maps,
   shifts, inverse/homotopy data, and the two equations (C.2).
3. The all-owner primitive rectangles are now constructed in the normalized
   Johnson collar.  What remains is their explicit P0 ambient inclusion and
   promotion to the strict dg maps of item 2.
4. For every owner and cable state, a commuting square identifying the MWW
   beta and both psi maps with the endpoint/common-target maps used by the
   proposed Reynolds row.
5. The primitive pivotal/duality input required by the fail-closed schema.
6. The complete grading-convention ledger required by the same checker.

Until these data are supplied, the correct statement is conditional: the
finite Burau computation produces 2624 in the chosen endpoint model, while C
does not yet turn that number into a functional on the genuine two-handle
skein-lasagna quotient.
