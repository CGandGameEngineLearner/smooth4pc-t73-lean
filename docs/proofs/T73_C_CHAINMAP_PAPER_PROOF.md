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

## C-H1: exact source boundary and failed currying attempt

The source results make every step after representability formal, but they do
not supply representability itself.

For cable state \(r\), MWW Definition 4.5 gives one 3-ball category
\(\mathcal C_{p_i(r)}\) for each one-handle, and Theorem 4.7 uses
\[
\mathcal A_r=\prod_i\mathcal C_{p_i(r)}
\]
with a coefficient profunctor \(M_{R_r}\).  Its objects are tuples of
inserted tangles.  The theorem identifies the skein-lasagna module with the
coinvariant/coend quotient for the two actions on this profunctor.  It does
not make \(R_r\) an endo-1-morphism of a single category.

BPW Proposition 3.12 identifies a trace of one morphism category with the
corresponding vertical trace.  BPW Propositions 3.20--3.21 then give the
universal quantum preshadow and functoriality for a locally pregraded
endobicategory with duals.  They apply after a coefficient class has been
typed as a 2-morphism \(a:F_rT\Rightarrow F_rT\) in one morphism category.
They do not turn an arbitrary multi-variable MWW profunctor into such an
endofunctor.

BHPW Theorem 4.6 makes an already specified tangle/foam construction
strictly functorial.  Its Corollaries E--F apply the qHH shadow and identify
the self-coefficient endpoint groups.  There is no K0-only obstruction:
qHH acts before the Chern/K0 identification, which is used only to name the
endpoint modules.  Strictness nevertheless cannot create a missing planar
gluing functor.

The required candidate-specific datum is a canopolis operation
\[
\iota_r:\mathcal A_r\longrightarrow
\mathcal T_2(P_{a_r},P_{b_r})
\tag{C.H1a}
\]
and natural homogeneous isomorphisms
\[
\chi^r_{\mathbf T,\mathbf T'}:
M_{R_r}(\mathbf T,\mathbf T')
\xrightarrow{\cong}
\operatorname{Hom}\!\left(F_r\iota_r\mathbf T,
F_r\iota_r\mathbf T'\right)\otimes A^{\otimes\ell_r}.
\tag{C.H1b}
\]
The all-owner product rectangles suggest a planar matching on the fixed
attaching arcs, but do not specify how arbitrary inserted tangles in all
input balls are glued, which boundary points remain external, or the output
split \(P_{a_r},P_{b_r}\).  Thus they do not define (C.H1a).

There is also an explicit normalization conflict in the present formula.
Under MWW Definition 4.5, a tangle
\(T:P_{86}\to P_{88}\) has \(86+88=174=2p\) boundary points, so its morphism
category has \(p=87\) and the \(N=2\) Hom normalization is \(+87\).
The manuscript instead attaches the shift \(-44\) to
\(\operatorname{Hom}(FT,FT')\) and describes it as removal of the Hom
normalization.  The value \(44\) belongs to the selected y-handle
configuration \(p_y=44\), not to the asserted
\(P_{86}\to P_{88}\) morphism category.  No planar operation or object shift
is given that reconciles these two numbers.  A constant change of all Hom
gradings would also destroy degree-zero composition.

A possible repair would first construct the exact planar currying at its
naturally resulting endpoint count, and only afterwards postcompose its
endpoint shadow with the auxiliary cup \(U:P_{86}\to P_{88}\).  The cup
cannot be inserted into (C.H1b) merely to change the endpoint count: it is
not an invertible tangle, so doing so does not produce a coefficient-bimodule
isomorphism.

If (C.H1a)--(C.H1b) were supplied by one framed product-ribbon isotopy, no
matrix enumeration would be necessary.  Extending the same isotopy by the
identity on all insertion boxes would give
\[
\chi^r_{\mathbf S,\mathbf T'}(f\cdot m)
=(F_r\iota_r f)^*\chi^r_{\mathbf T,\mathbf T'}(m),\qquad
\chi^r_{\mathbf T,\mathbf U}(m\cdot g)
=(F_r\iota_r g)_*\chi^r_{\mathbf T,\mathbf T'}(m).
\tag{C.H1c}
\]
These are the same glued surface, so BHPW strictness fixes their sign.
Homogeneous circle counits would then carry every coefficient quantum-cyclic
relation to the regular vertical-trace relation; BPW 3.12 and 3.20--3.21
would give the statewise \(\Theta_r\).  Hence naturality and qTrace descent
are formal after (C.H1a)--(C.H1b), but the current paper does not define
those maps and its displayed endpoint/shift type is inconsistent.

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

Let \(A=\rho_h(W)\).  A genuine change of endpoint coordinates by an
invertible \(P\) transports operator, cup, and cap simultaneously:

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
returned pure loop \(P\), with the fixed cup and cap unchanged, replaces \(A\)
by \(\rho_h(P)A\).  If \(P,W\in\Gamma_3\), then

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

Taking the equally supported inverse loop \(P=W^{-1}\) gives a concrete
counterexample: \(W^{-1}W=1\), its endpoints and first-order normals return
and its writhe is still zero, but the cubic changes from 2624 to zero.  This
is replayed by `scripts/audit_t73_point_push_gauge.py` and recorded in
`audit/t73_point_push_gauge.json`.

This does not contradict BPW: a chosen point-push surface may act
nontrivially, and a noncanonical linear detector may still prove a class is
nonzero if its quotient descent is independently established.  It does show
that the current P0 recipe---normalize the points, choose the six-sweep loop
by isotopy extension, and return them---does not make 2624 a
presentation-independent consequence of the static AR collar.  A repair must
either declare \(W\) to be an auxiliary chosen endpoint self-cobordism, which
cannot discharge P0 or (C.1), or construct a relative cobordism class selected
by the embedded AR geometry and prove that every permitted presentation
change is only the conjugation (C.3), never the multiplication (C.4).

## Fixed noncanonical \(W\): sufficient in principle

Canonicity is not required to prove that a class is nonzero.  Fix the
oriented point-push tangle \(W:P_{88}\to P_{88}\), cup
\(U:P_{86}\to P_{88}\), and cap \(C:P_{88}\to P_{86}\).  The BPW
horizontal-trace action and strict BHPW foam/qHH functor assign a specified
\(W\) an endpoint operator
\[
A_W:E_{88,h}\longrightarrow E_{88,h}.
\]
Under the Chern/K0 identification this is the corresponding
\(U_q(\mathfrak{sl}_2)\) intertwiner.  Equality with the numerical Burau
matrix still requires the unresolved variance and pivotal chart.

Assuming the coefficient shadow of (C.1)--(C.2),
\[
D_h^W(x)=C_h(A_W-I)\operatorname{Sh}_h(x)
\tag{C.5}
\]
is well defined on the fixed coefficient qTrace: after the shadow kills the
cyclic relations, the remaining factors are fixed linear maps.  If
\(A_W-I=O(h^3)\), division by \(h^3\) and reduction modulo \(h\) gives an
ordinary functional.  No invariance under replacing \(W\) is needed.

The exact sufficient descent statement is:

**Fixed-\(W\) cubic cocone theorem.** For every cable state \(r\), assume a
strict statewise shadow
\(\Theta_r:C_r\widehat\otimes R_h\to E_r\).  For each placement
\(\omega\in\Omega_r\), assume typed maps placing the same fixed \(W\) on 88
old endpoints, uniformly with \(A_{W,\omega}-I=O(h^3)\).  Suppose every MWW
beta is sent to a physical-copy braid \(B\) satisfying
\[
A_{W,b\omega}=BA_{W,\omega}B^{-1},\qquad
u_{b\omega}=Bu_\omega,\qquad c_{b\omega}=c_\omega B^{-1},
\tag{C.6}
\]
and every MWW psi is sent to an old factor tensor its local Frobenius map,
with \(W\) on the old factor and \(\epsilon\otimes\epsilon\) on the new pair.
Then
\[
\lambda_{r,\omega}(x)=
[h^3]\,c_{r,\omega}(A_{W,\omega}-I)\Theta_r(x),\qquad
\lambda_r=|\Omega_r|^{-1}\sum_{\omega\in\Omega_r}\lambda_{r,\omega}
\tag{C.7}
\]
satisfies
\[
\lambda_r\beta_i(b)=\lambda_r,\qquad
\lambda_{r+e_i}\psi_i^{[0]}=0,\qquad
\lambda_{r+e_i}\psi_i^{[1]}=\lambda_r.
\tag{C.8}
\]

For beta, (C.6) gives equality after reindexing the average; a
positive-\(h\)-order standardization error multiplies \(A_W-I=O(h^3)\) and
does not affect the cubic.  For psi, \(W\) stays on the old factor and
\[
(\epsilon\otimes\epsilon)\Delta(1)=0,\qquad
(\epsilon\otimes\epsilon)\Delta(X)=1.
\]
The placement-orbit cardinalities cancel between adjacent averages.

Thus a fixed noncanonical \(W\) is sufficient in principle.  The application
remains open: there are no statewise chain maps \(\Theta_r\), actual-beta
comparison diagrams, or whole-source actual-psi factorizations.  The
all-owner artifact supplies their geometric incidence prefix only.
BPW/BHPW evaluate supplied movies; they do not construct these
candidate-specific squares.

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

## Standard pivotal convention after P0 retyping

The static P0 collar now fixes 44 vertical framed arcs but deliberately
contains no braid.  This permits a fresh standard endpoint convention rather
than trying to justify the legacy all-`+q^0` table.  Move the two selected cup
feet to tensor positions 0 and 1; keep the remaining marked endpoints in their
geometric order.  The oriented sign of a doubled point is its base-passage
orientation times its cable-copy sign.  Upward points are assigned `V` and
downward points `V*`, giving 44 of each.

`scripts/build_t73_c_pivotal_grading_input.py` writes the source/target faces,
tangents, coorientations, BPW boundary symbols, A.4 duality atoms, A.6 cup/cap
terms and standard no-binding product-foam normals.  The input is hash-bound
to `geometry/t73_p0_marked_vertical_collar.json`.  The fail-closed checker
derives positive pivotal signs with q-powers 0 or 1 and selected cup powers
-1 and +1.  It does not copy the legacy coefficients.

Because the braid operator minus the identity starts in order `h^3`, all
positive-order corrections in these pivotal maps affect only order at least
four.  Recomputing with the derived constant terms again gives epsilon cubic
-328 and h cubic 2624.  Thus C-H3 is resolved for this chosen convention.

Absolute degree remains open.  The actual MWW coefficient closure, Hattori
target closure, selected cabled state and MWW-to-BHPW comparison are exactly
the four missing grading diagrams.  Until C-H1 supplies them with one common
framing/writhe convention, the sum 494 is intrinsic framed-KhR2 arithmetic,
not a certified absolute comparison degree.

## Corrected C-H1 typing: reduce \(C_{271}\), then double \(C_{44}\)

The normalization conflict above identifies the correct order of operations.
At the selected state let
\[
\mathcal A_{s_0}=\mathcal C_{44}\boxtimes\mathcal C_{271},
\]
where \(\mathcal C_p=\mathcal S^2_0(B^3;P_p;\mathbb Q)\) is MWW's
bigraded 3-ball category.  Keep the coefficient \(M_R\) unshifted; MWW's
one-handle gluing contributes the global shift
\(\{44+271\}=\{315\}\).

First take the coefficient coend in the z variable:
\[
M_R^{z}(T,T')=
\int^{Z\in\mathcal C_{271}}
M_R\bigl((T,Z),(T',Z)\bigr).
\tag{C.H1d}
\]
This is a \(\mathcal C_{44}\)-bimodule.  Directly reordering the generators
and relations in the two coends gives the Fubini isomorphism
\[
HH_0(\mathcal C_{44}\boxtimes\mathcal C_{271};M_R)
\cong HH_0(\mathcal C_{44};M_R^z).
\tag{C.H1e}
\]
No finite-dimensionality or matrix calculation is used here.

The 44 product rectangles suggest a 44-strand tangle \(B\), while the
remaining z channels suggest 227 separate unknot factors.  The required
geometric statement is the natural reduced-coefficient isomorphism
\[
H^z_{T,T'}:
M_R^z(T,T')
\xrightarrow{\cong}
\operatorname{Hom}_{\mathcal C_{44}}(BT,BT')\{-44\}
\otimes A^{\otimes227}.
\tag{C.H1f}
\]
Now \(-44\) has the correct source: objects of \(\mathcal C_{44}\) have
88 boundary points, so MWW Definition 4.5 puts the shift \(+44\) in their
Hom spaces; the product-ribbon isotopy is an isomorphism of raw link
homologies, hence contributes the compensating \(-44\).  Labelling the 227
circles by \(X\) contributes \(+227\), and the later MWW shifts give
\[
-44+227+315-4=494.
\]
This arithmetic is homogeneous provided (C.H1f) is proved in one framed
convention.

Apply the 227 counits and remove the simultaneous \(B\)-transport.  BPW's
vertical-to-horizontal trace applied to \(\mathcal C_{44}\), followed by
oriented doubling, then has target
\[
\operatorname{Sh}^{44}_h:
q\operatorname{Tr}(\mathcal C_{44};M_R^z)
\longrightarrow \operatorname{End}(E_{88,h}),
\tag{C.H1g}
\]
where the 88-dimensional one-defect space appears only after doubling the
44 oriented wickets.  The selected cup is external:
\[
u_h:E_{86,h}\longrightarrow E_{88,h},\qquad
\ell_h:E_{88,h}\longrightarrow E_{86,h}.
\]
Thus the correctly typed detector is
\[
D_h(x)=
\ell_h\bigl(\rho_h(W)-I\bigr)
\operatorname{Sh}^{44}_h(x)\,u_h.
\tag{C.H1h}
\]
For the diagonal whose reduced regular trace is the identity,
\(\operatorname{Sh}^{44}_h(x)=\operatorname{Id}_{E_{88,h}}\), and (C.H1h)
specializes to the computed cubic.  The noninvertible cup is no longer
incorrectly placed inside a coefficient-bimodule equivalence.

Equations (C.H1d)--(C.H1h) are suitable replacements for the manuscript's
\(P_{86}\to P_{88}\) coefficient category and equation (17).  They are not
yet an unconditional proof.  To prove (C.H1f), the product tangle must give
a two-sided representable profunctor in the z variable so that the
\(\mathcal C_{271}\)-coend is evaluated by co-Yoneda.  Concretely, one needs:

1. a boundary-parametrized planar/canopolis operation
   \(J:\mathcal C_{44}\to\mathcal C_{271}\) adding the 227 standard z arcs;
2. an isotopy, relative to all insertion boxes, identifying the full
   off-diagonal coefficient link for arbitrary \(T,T',Z,Z'\) with the two
   representable z-Hom factors determined by \(J\) and \(B\);
3. the resulting composition/co-Yoneda square, including MWW's Hom shifts,
   both \(\mathcal C_{44}\) actions, and both
   \(\mathcal C_{271}\) actions.

BHPW canopolis composition and strict functoriality prove naturality once
this planar input is supplied.  The current all-owner artifact records
attaching-arc pairings and residual meridians, but not parametrizations of
the two z insertion spheres, the planar operation \(J\), or the relative
isotopy for arbitrary inserted tangles.  Therefore (C.H1f), and hence
\(\operatorname{Sh}^{44}_h\), remains the first open C-H1 map.  The corrected
typing shows how it could be closed without foam matrices; it is not implied
by the existing counts alone.

## Stress test: the 227 factors are not invariant before the z coend

There is no platform, idempotent, coloring, or owner label in MWW's
\(\mathcal C_{271}\) that distinguishes the 44 selected z channels from the
227 added channels.  Definition 4.5 allows every framed oriented tangle with
the prescribed boundary and all KhR morphisms between such objects.  In
particular, a same-orientation braid may exchange a selected strand with an
added strand.  BHPW's platforms and weight block record admissibility and
total weight; they do not supply a central idempotent marking the provenance
of individual strands.

The failure of a fixed-factor counit is already visible in the rank-two
Frobenius model.  Let
\(A=\mathbb Q[X]/(X^2)\), with
\(\epsilon(1)=0\), \(\epsilon(X)=1\), and let
\(\tau:A\otimes A\to A\otimes A\) exchange an active circle and an added
circle.  This is the constant term of an allowed same-orientation braid.
Then
\[
(\operatorname{id}\otimes\epsilon)(1\otimes X)=1,\qquad
(\operatorname{id}\otimes\epsilon)\tau(1\otimes X)
=(\operatorname{id}\otimes\epsilon)(X\otimes1)=0.
\tag{C.mix1}
\]
Thus capping the factor declared to be extra is not invariant under the full
\(\mathcal C_{271}\) action.

There is also an explicit allowed merge--split foam.  Its Frobenius map is
\[
S=\Delta\circ m:A\otimes A\longrightarrow A\otimes A.
\]
Since
\[
S(1\otimes1)=1\otimes X+X\otimes1,
\]
we have
\[
(\operatorname{id}\otimes\epsilon)S(1\otimes1)=1
\quad\text{but}\quad
(\operatorname{id}\otimes\epsilon)(1\otimes1)=0.
\tag{C.mix2}
\]
No map on the active factor can make the fixed-extra counit intertwine this
foam, because a linear map must send zero to zero.  Equations (C.mix1)--(C.mix2)
disprove any claim that
\(\operatorname{Hom}(JT,JT')\cong
\operatorname{Hom}(T,T')\otimes A^{\otimes227}\) is natural for the entire
\(\mathcal C_{271}\) action with the second tensor factor fixed.

This does not disprove the full co-Yoneda route in (C.H1d)--(C.H1f).
If the original coefficient profunctor first factors as two genuine
representables over the *full* category \(\mathcal C_{271}\), then the
coend composes all mixing morphisms and yields
\(\operatorname{Hom}_{\mathcal C_{271}}(JT,JT')\).  Only after this coend
may the split-link Kunneth isomorphism and the 227 counits be applied.  At
that stage only the remaining \(\mathcal C_{44}\) actions require naturality,
and \(J(f)=f\sqcup\operatorname{id}^{\sqcup227}\) preserves the split
circles.

Therefore the order is load-bearing:
\[
\text{full z-representability}
\ \Longrightarrow\
\text{co-Yoneda over all z morphisms}
\ \Longrightarrow\
\text{split-link Kunneth and counits}.
\tag{C.mix3}
\]
The manuscript currently uses Kunneth/counits before proving the first two
arrows and says the circle factors are disjoint from both actions.  That
statement is false for the full z action by (C.mix1)--(C.mix2).  C can still
close only if the missing relative planar diagram proves the two-sided
representable factorization needed for the first arrow of (C.mix3).  The
all-owner primitive incidence data do not prove it.

## Literal off-diagonal splitting is refuted for the saved source

Define \(J(T)=T\sqcup I^{\sqcup227}\), placing the 227 boundary-parallel z
arcs in a separated sub-ball of a newly standardized z insertion ball.  This
is a valid canopolis operation.  Co-Yoneda would close C-H1 if the full
off-diagonal normalized coefficient
\(\widehat M_R=M_R\{44+271\}\) admitted the relative factorization
\[
\widehat M_R((T,Z),(T',Z'))\cong
\operatorname{Hom}_{z}(JBT,Z')\otimes
\operatorname{Hom}_{z}(Z,JBT')\{-227\}
\tag{C.split}
\]
for arbitrary insertion tangles.

The complete source constructor now decides this question.  It saves all
1260 oriented boundary endpoints and 630 exterior intervals.  The 176
Y-incident intervals have transition counts
\[
84(Y_-,Z_+)+84(Y_+,Z_-)+4(Y_-,Z_-)+4(Y_+,Z_+).
\]
The final eight same-side intervals are attached to the two negatively
oriented base Y passages \(m_2:C_i\) and \(r_{xy}:\mathrm{vertex}:1\), on
both cable copies and both incident sides.

The v2 target has the correct endpoint cardinalities: each closure contains
88 Y--Z arcs and 227 Z--Z arcs, hence its four insertion balls carry
\(88,542,542,88\) endpoints.  Nevertheless a relative ambient isotopy fixes
the endpoint matching, not just those counts.  The eight same-side source
intervals cannot lie in two disjoint closure balls pairing
\((Y_-,Z_+)\) and \((Y_+,Z_-)\).  Thus (C.split) is false for the saved
source matching.

Four crosswise reconnections would change the matching, but they are saddle
or merge--split cobordisms rather than a pivotal retyping or ambient isotopy.
Their Blanchet signs, Euler characteristics and quantum degrees have not been
constructed.  The conditional theorem below remains a correct statement
about a different coefficient exterior satisfying its premise; it is
counterfactual for the saved source and cannot establish the actual C map or
degree.

## Conditional two-representable theorem, with all shifts

The preceding missing sphere is exactly the extra hypothesis needed for an
ordinary tensor/Kunneth proof.  The general statement is as follows.

Let \(p_y\leq p_z\), put \(\ell=p_z-p_y\), let
\(\mathcal C=\mathcal C_{p_y}\), \(\mathcal D=\mathcal C_{p_z}\), and let
\[
J:\mathcal C\longrightarrow\mathcal D,\qquad
J(T)=T\sqcup I^{\sqcup\ell}.
\]
Let \(B\) be the product tangle on the \(p_y\) active channels and write
\(K=J\circ B\).  Let
\(\widehat M_R=M_R\{p_y+p_z\}\) denote the MWW coefficient with its
one-handle normalization.

Assume the relative four-box presentation contains a separating 2-sphere,
disjoint from all coefficient strands and all four insertion boxes, such
that for every \(T,T'\in\mathcal C\) and \(Z,Z'\in\mathcal D\) its two sides
are precisely the closed links defining
\[
\operatorname{Hom}_{\mathcal D}(KT,Z')
\quad\text{and}\quad
\operatorname{Hom}_{\mathcal D}(Z,KT').
\tag{C.split-hom}
\]
Then there is a homogeneous natural isomorphism
\[
\widehat M_R((T,Z),(T',Z'))
\cong
\operatorname{Hom}_{\mathcal D}(KT,Z')
\otimes_{\mathbb Q}
\operatorname{Hom}_{\mathcal D}(Z,KT')\{p_y-p_z\}.
\tag{C.rep2}
\]

The tensor in (C.rep2) is the ordinary tensor over \(\mathbb Q\), not a
relative tensor over an arc algebra.  Indeed, the separating sphere realizes
the coefficient link as a split disjoint union, and monoidality/Kunneth for
the strict foam theory over the field \(\mathbb Q\) gives the displayed
tensor product.  Extending the same relative split by identities on the four
insertion boxes proves naturality in all variables.  The first
\(\mathcal D\) action is postcomposition on the first representable, the
second is precomposition on the second, and the two \(\mathcal C\) actions
are induced by \(K(f)=J(Bf)\).

The shift in (C.rep2) is forced directly by the literal split.  The
normalized coefficient has shift \(p_y+p_z\), whereas the tensor of two
normalized \(\mathcal D\)-Hom spaces has shift \(2p_z\).  Their difference
is \(p_y-p_z=-\ell\).  Taking the enriched coend over
\(\mathcal D\) and composing gives
\[
\begin{aligned}
\widehat M_R^z(T,T')
&=
\int^{Z\in\mathcal D}
\widehat M_R((T,Z),(T',Z))\\
&\cong
\int^{Z\in\mathcal D}
\operatorname{Hom}_{\mathcal D}(KT,Z)
\otimes
\operatorname{Hom}_{\mathcal D}(Z,KT')\{-\ell\}\\
&\cong
\operatorname{Hom}_{\mathcal D}(KT,KT')\{-\ell\}.
\end{aligned}
\tag{C.Yoneda}
\]
The last arrow is enriched co-Yoneda.  Explicitly,
\([a\otimes b]\mapsto b\circ a\), with inverse
\(c\mapsto[\operatorname{id}_{KT}\otimes c]\); the coend relation is exactly
associativity of composition.  Hence all mixing \(\mathcal D\)-morphisms,
including (C.mix1)--(C.mix2), are absorbed before any counit is applied.

The closure of \(JT'\cup\overline{JT}\) is the split union of the closure of
\(T'\cup\overline T\) and \(\ell\) unknots.  From MWW Definition 4.5,
\[
\begin{aligned}
\operatorname{Hom}_{\mathcal D}(JBT,JBT')
&\cong
\operatorname{KhR}_2\!\left(
(BT'\cup\overline{BT})\sqcup U^{\sqcup\ell}
\right)\{p_z\}\\
&\cong
\operatorname{Hom}_{\mathcal C}(BT,BT')\{\ell\}
\otimes A^{\otimes\ell}.
\end{aligned}
\tag{C.Kunneth}
\]
Combining (C.Yoneda) and (C.Kunneth) yields
\[
\widehat M_R^z(T,T')
\cong
\operatorname{Hom}_{\mathcal C}(BT,BT')
\otimes A^{\otimes\ell}.
\tag{C.Hnorm}
\]
Removing the global MWW shift \(\{p_y+p_z\}\) gives the raw comparison
\[
M_R^z(T,T')
\cong
\operatorname{Hom}_{\mathcal C}(BT,BT')\{-(p_y+p_z)\}
\otimes A^{\otimes\ell}.
\tag{C.Hraw}
\]
Thus at \((p_y,p_z,\ell)=(44,271,227)\), the normalized reduced coefficient
has no Hom shift.  The all-\(X\) diagonal has degree \(227\), and the cabled
shift \(-4\) gives degree \(223\).  Equivalently, the raw reduced comparison
has shift \(-315\), after which the global \(+315\) cancels it.

This contradicts, rather than derives, the manuscript's raw shift \(-44\)
and degree \(494\).  The latter shift belongs to a different proposed
single-Hom factorization.  A literal tensor of two normalized
\(\mathcal C_{271}\)-representables cannot simultaneously have the
manuscript's grading.

Both remaining \(\mathcal C\) action squares commute by (C.rep2) naturality,
co-Yoneda associativity, and the split Kunneth map.  After applying
\(\epsilon^{\otimes\ell}\), BPW Proposition 3.12 sends the regular
coefficient qTrace to vertical trace; Propositions 3.20--3.21 send it to
horizontal trace.  Oriented doubling and the BHPW qHH functor give
\[
\operatorname{Sh}^{p_y}_h:
q\operatorname{Tr}(\mathcal C_{p_y};M_R^z)
\longrightarrow
\operatorname{End}(E_{2p_y,h}).
\tag{C.state-shadow}
\]
For \(p_y=44\), this is the required endomorphism of \(E_{88,h}\), and the
external cup/cap give the correctly typed detector (C.H1h).

Without the separating sphere, canopolis gluing supplies a composition of
tangle bimodules, modeled at chain level by a relative tensor over an arc
algebra.  It does not supply the ordinary tensor of Hom homologies in
(C.rep2), and composition is not generally an isomorphism.  Sweetness of the
bimodules removes some derived-projectivity issues but does not turn a
connected planar composite into a split-link Kunneth tensor.  Therefore a
literal separating sphere, or a separate excision theorem proving the same
monoidal equivalence, is mathematically required for this particular
two-representable proof.
