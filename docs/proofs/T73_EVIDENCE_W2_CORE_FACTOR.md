# Does the closed endpoint detector factor through the MWW two-handle map?

Date: 2026-09-01
Scope: the selected state

\[
s_0=(\alpha=0,r=e_{m2}+e_{rxy})
\]

and, separately, the cross-owner `Z` variant.  This audit does not use the
rejected claim that an all-state endpoint shadow by itself proves the cabled
relations.

## Verdict

```text
C_hat_(87,2) equals the four Phi core disks:       NO
full-q D_h factors through Phi automatically:      NO / NOT CONSTRUCTED
physical W2 movie giving such a full-q L_h:         ABSENT
reason:                                             endpoint cap != core attachment
leading divided cubic D_3 factors through Phi:      YES, with extra cocone data
is that leading factorization automatic from cap?: NO
selected value after leading factorization:         -59072
Z leading value in epsilon normalization:            -16
sphere/full final quotient:                          NOT ADDRESSED
```

The tempting shortcut is false in its full form.  The normalized endpoint cap
and MWW's two-handle core attachment are geometrically different cobordisms.
At cubic order one can build a quotient functional, but only after adjoining
the two-handle core counits and proving their beta/psi cocone equations.  That
is extra work; it is not contained in `C_hat`.

## 1. The two maps and their types

Let

\[
C_{s_0}=\mathcal S^2_0
(W_1;K(r,r),\eta^r;\mathbb Q)\{-4\}.
\]

The boundary cable has exactly four physical components:

```text
rxy-, rxy+, m2-, m2+.
```

The summand map is

\[
C_{s_0}\xrightarrow{\iota_{s_0}}
\mathcal C_{cabled}(W_1;K)
\xrightarrow{\Phi}
\mathcal S^2_0(W_2;\varnothing,(0,0)).
\tag{1.1}
\]

MWW defines `Phi` by attaching, to every raw surface, four pairwise disjoint
disks parallel to the appropriate two-handle cores (`kirby.tex:359-369`):

\[
D_{rxy^-}\sqcup D_{rxy^+}\sqcup D_{m2^-}\sqcup D_{m2^+}.
\tag{1.2}
\]

These disks fill the **entire four cable circles** in the attaching solid tori.

By contrast, the detector is first defined after the coefficient
vertical-to-horizontal shadow:

\[
\mathcal D_h=widehat C_{87,2}(h)
\circ(\rho_h(W)-I)\circ S_h .
\tag{1.3}
\]

Here

\[
\widehat C_{87,2}:P_{88}\longrightarrow P_{86}
\tag{1.4}
\]

is a single oriented endpoint cap between gate indices `87` and `2`.  In the
frozen owner ledger these are one `rxy-` passage and one `m2+` passage.  It is a
local `(88,86)` tangle cobordism in the endpoint category.  It does not attach
any disk to the `rxy+` or `m2-` cable, and even for `rxy-` and `m2+` it caps two
**cut endpoint arcs**, not their complete attaching-circle components.

Thus the boundary data already refute the identity

\[
\widehat C_{87,2}=D_{rxy^-}\sqcup D_{rxy^+}
\sqcup D_{m2^-}\sqcup D_{m2^+}.
\tag{1.5}
\]

The codomains also differ: (1.4) lands in the one-dimensional endpoint block
`E_86`; (1.2) lands in the closed `W2` lasagna module.  A grading shift cannot
repair a boundary/codomain mismatch.

## 2. Why a full-q factorization is not automatic

Suppose that a linear functional

\[
L_h:\mathcal S^2_0(W_2;\varnothing,(0,0))\widehat\otimes\mathbb Q[[h]]
\longrightarrow\mathbb Q[[h]]
\tag{2.1}
\]

satisfied

\[
\mathcal D_h|_{C_{s_0}}=L_h\Phi\iota_{s_0}.
\tag{2.2}
\]

Then `D_h` would have to vanish exactly on every beta and psi relation meeting
the summand, because those relations are in the kernel of the cabled quotient
before `Phi` (`kirby.tex:331-356`).  Equivalently, for every actual owner braid
and every forward stabilization one would need the full-series equations

\[
\begin{aligned}
\mathcal D_h(\beta_i(b)x)&=\mathcal D_h(x),\\
\mathcal D_h(\psi_i^{[0]}x)&=0,\\
\mathcal D_h(\psi_i^{[1]}x)&=\mathcal D_h(x).
\end{aligned}
\tag{2.3}
\]

No physical movie proving (2.3) exists in the supplied artifacts.  More
importantly, (2.3) does not follow by isotopy of (1.4): the psi equations use
two **individual W2 core counits**

\[
(\epsilon\otimes\epsilon)\Delta(1)=0,
\qquad
(\epsilon\otimes\epsilon)\Delta(X)=1,
\tag{2.4}
\]

whereas reversing the raw W1 ribbon is a different surface, has normalized
degree `+2`, and does not give (2.4).  The two counit disks in (2.4) exist only
after the corresponding two-handle cores have been attached.  This distinction
is established in `D:/tmp/anchored_cap_cocone/PSI_RESULT.md:17-78`.

For beta, `B_(1,1)` has trivial constant permutation but a pure-braid kernel
acting as `I+O(h)`.  Since `(rho_h(W)-I)=O(h^3)`, this proves invariance of the
**cubic coefficient**, not equality of the full series.  Pure-braid residuals
can begin in order four.  The existing all-level construction explicitly
records `full q-series: NOT PROVED`; it cannot be used as an exact (2.1).

There is also no alternative direct movie for (2.1).  To define one from a
closed W2 filling, one would have to:

1. choose intersections with all two-handle cores;
2. cut them open to a cable state;
3. choose the two marked endpoint passages `87,2`;
4. apply the point-push word `W-I` in that chosen cut collar;
5. standardize all other physical copies and close them by core counits.

Changing steps 1--3 is precisely the beta/psi ambiguity in MWW's proof of
`Phi`.  Independence of those choices is (2.3), not a consequence of `Phi`.
Using `Phi^{-1}` and then (1.3) would therefore be circular.

Hence no full-q `L_h` with a supplied complete geometric movie has been
constructed, and core attachment does not automatically kill beta/psi.

## 3. The valid leading-order factorization

There is a narrower statement.  Write

\[
\mathcal D_h=h^3\mathcal D_3+O(h^4).
\]

At the base state:

- every beta pure residual is `I+O(h)`, so it changes a cubic witness only in
  order four;
- the newly added psi pair is closed by the two W2 core counits (2.4);
- the cabled grading shift changes by `-2`, cancelling the raw degree `+2` of
  `psi^[1]`; thus the undotted relation has total degree zero;
- `psi^[0]` has total degree `-2` and is killed by (2.4).

After choosing the physical-copy common target and its fixed strict signs,
these equations define a cubic cocone

\[
\Lambda^{(3)}_s:C_s\longrightarrow\mathbb Q
\tag{3.1}
\]

on the cabled direct sum.  The quotient universal property, followed by the
isomorphism `Phi`, gives a unique **linear** functional

\[
L_3:\mathcal S^2_0(W_2;\varnothing,(0,0))\longrightarrow\mathbb Q
\tag{3.2}

such that

\[
\boxed{
\mathcal D_3|_{C_{s_0}}=L_3\Phi\iota_{s_0}.}
\tag{3.3}
\]

This is the strongest justified factorization.  It is a quotient functional
assembled from the endpoint cap, four W2 core disks, stable-copy
standardizations and counits.  It is not represented in the evidence by one
closed physical cobordism, and it does not lift to a proved `L_h` on the full
power series.

### Degree ledger

For the selected raw class:

```text
one-handle Hattori class:                         498
cabled s0 shift:                                  -4
class entering Phi:                              494
Phi four-core attachment:          grading preserving
endpoint W and normalized cap:        normalized degree 0
divided cubic coefficient:          scalar degree bookkeeping only
```

For a psi1 edge, the raw dotted ribbon has degree `+2` and the target cabled
shift contributes `-2`, so the total degree is zero.  For psi0 the total is
`-2` and its two-core-counit value is zero.  These are exactly the degrees
needed for (3.1)--(3.3); they do not furnish a full-q movie.

The selected value remains

\[
L_3\Phi\iota_{s_0}(\widetilde v_{s_0})=-59072.
\tag{3.4}
\]

## 4. Cross-owner Z

For the cross-owner harmonic class, the corrected endpoint row satisfies

\[
\phi(\epsilon)C(\epsilon)=O(\epsilon^4),
\qquad
\phi(\epsilon)Z(\epsilon)=-16\epsilon^3+O(\epsilon^4).
\]

Together with the actual E1 coefficient lift and the same leading core-counit
relations, this gives an analogous `epsilon`-cubic quotient functional with
value `-16`.  Again, this is a leading-order linear factorization, not an
identification of its endpoint cap with the four core disks and not a
full-series W2 invariant.

## 5. Exact first missing object

The full shortcut would require

```text
FULL_Q_W2_CORE_ENDPOINT_CAP_COCONE
```

consisting of a common target for every physical-copy selection, exact
standardization movies and signs, exact beta invariance (including pure-braid
residuals), exact psi0/psi1 squares, and compatibility of the non-split
coefficient with all four core disks.  Only its cubic truncation is presently
available.

Therefore the answer to the core question is:

> `D_h` does not factor through `Phi` merely because it ends with a cap.  The
> cap closes two artificial endpoint arcs; `Phi` closes four complete physical
> cable circles.  A divided cubic factorization exists after adding a separate
> W2 core-evaluation cocone, but full-q automatic beta/psi descent does not.

## Sources

- MWW cabled relations and `Phi`:
  Manolescu--Walker--Wedrich, [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), handle-presentation section.
- Exact endpoint cap type and cubic:
  [`ACTUAL_CAP_POSTCOMPOSITION_DECISION.md`](../../evidence/public_geometry/source_notes/ACTUAL_CAP_POSTCOMPOSITION_DECISION.md).
- Named `s0` representative and four-core movie:
  `D:/tmp/raw_state_binding/RAW_STATE_BINDING_RESULT.md:1-139`.
- Why reverse ribbon is not two core counits:
  `D:/tmp/anchored_cap_cocone/PSI_RESULT.md:1-130`.
- Base beta order statement:
  [`BASE_BETA_MULTIPLICITY_REAUDIT.md`](../../evidence/public_geometry/source_notes/BASE_BETA_MULTIPLICITY_REAUDIT.md).
- Cubic common-target/core-counit construction and explicit full-q boundary:
  [`ALL_LEVEL_REYNOLDS_FOAM_FAMILY_DECISION.md`](../../evidence/public_geometry/source_notes/ALL_LEVEL_REYNOLDS_FOAM_FAMILY_DECISION.md).
