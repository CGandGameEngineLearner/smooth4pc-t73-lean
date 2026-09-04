# Relative-isotopy test for the cyclic \(m_2\) connector

Date: 2026-09-05

## Question

The 42nd selected \(m_2\) pairing joins the bottom arc
`m_2:C_i` cyclically to `c1:letter:0`. It runs through both
mapping-handle arcs and the \(t/h_{CS}\) cancellation collar. Can it be moved
to the product-normal connector used in the proposed coefficient
factorization while fixing both insertion boxes, the rest of the attaching
link, and the cancellation data?

## Exact relative framed-arc theorem

Let \(M\) be the post-cancellation boundary collar and let \(F\subset M\)
be the union of:

- the two parametrized insertion boxes;
- every attaching-link segment required to remain fixed;
- the belt/cancellation collars outside the permitted support;
- the 227 leftover tracks.

Let \(a_0,a_1:I\hookrightarrow M\setminus F\) be the actual cyclic connector
and desired product connector, with the same fixed endpoints and endpoint
germs. Give both arcs their transported normal framings.

The following condition is sufficient:

> There is an embedded rectangle \(D\cong I\times I\) in \(M\setminus F\)
> whose opposite sides are \(a_0\) and \(a_1\), whose other sides lie in the
> fixed endpoint disks, and over which the two framed normal fields extend
> with relative twist zero.

Under this condition, pushing across \(D\) gives an isotopy of framed proper
arcs relative to endpoints. The isotopy-extension theorem promotes it to an
ambient isotopy of \(M\) fixed on \(F\). Extending over a boundary collar of
the 4-dimensional 0/1-handlebody gives a diffeomorphism carrying the complete
framed attaching link. If every unattached upper-handle attaching map is
transported by the induced boundary diffeomorphism, the complete closed
handle decomposition remains the same Cappell--Shaneson manifold.

Consequently such an isotopy preserves all pairwise linking numbers, every
2-handle framing, the cancellation framing, and the transported upper
handles. No separate calculation of those invariants is needed after the
ambient framed isotopy is established.

## Necessary obstructions

Put \(N=M\setminus F\). If the rectangle does not exist, progressively weaker
obstructions are:

1. the relative fundamental-groupoid class
   \[
   [a_0\overline{a_1}]\in\pi_1(N,p),
   \]
   after joining the fixed endpoint germs;
2. its abelianization, equivalently the vector of linking/intersection
   numbers with fixed components and insertion-box meridians;
3. the relative framing difference in
   \(\pi_1(SO(2))\cong\mathbb Z\);
4. the local knot type of the proper arc in \(N\).

Vanishing of the first three is necessary but is not generally sufficient:
proper arcs in a 3-ball can be knotted while homotopic relative endpoints and
with identical linking and framing. The complete obstruction is equality in
the framed relative isotopy set
\[
\pi_0\operatorname{Emb}^{fr}_{\partial}(I,N).
\]
Equivalently, one may give the embedded rectangle above or a full ambient
isotopy movie. A separating 2-sphere placing the proposed Hom factors on
opposite sides is a stronger sufficient certificate tailored to the desired
coefficient splitting.

## Result for the committed connector

The current record
`geometry/t73_actual_product_rectangles.json#/rectangles/43` supplies:

- the two source identifiers and orientation;
- a bottom coordinate polyline for one side;
- a reference to the replacement \(m_1\) \(z\)-lane;
- hashes of two \(t/h_{CS}\) slide bands;
- the sentence that a component subannulus is transported.

It does not supply vertices or faces for the cyclic connector itself in one
common complement, the fixed set \(F\), an embedded rectangle to the desired
product connector, a relative fundamental-group word, a relative twist
calculation, or a simultaneous isotopy with the 227 leftover tracks.

Therefore the correct answer is:

- **conditionally yes** under the embedded zero-twist rectangle theorem;
- **not proved yes for the committed data**;
- **not proved impossible either**, because the data are insufficient to
  compute the first necessary invariant
  \([a_0\overline{a_1}]\in\pi_1(M\setminus F)\).

Replacing the connector in a diagram without this relative framed isotopy
would not be a harmless standardization: it could change the attaching-link
isotopy class, a 2-handle framing, or its linking with the fixed coefficient
strands. Calling the replacement \(X_J\) and transporting the old upper
handles afterward would merely assume the missing boundary diffeomorphism.
