# Independent audit of the two-representable grading

Date: 2026-09-05

## Source conventions

The following line references are to the TeX source of MWW,
arXiv:2206.04616.

1. `1handles.tex:173--192` (published Definition 4.5) defines
   \[
   \operatorname{Hom}_{\mathcal C_p}(T_1,T_2)
   =\operatorname{KhR}_N(T_2\cup\overline{T_1})\{p(N-1)\}
   \]
   and expressly makes composition grading-preserving.
2. `1handles.tex:140--156` defines one-handle gluing with the shift
   \(\{(\sum_i p_i)(N-1)\}\), saying that it compensates the Euler
   characteristic change.
3. `1handles.tex:242--274` (published Theorem 4.7) uses exactly that
   global shift in the one-handle coinvariant formula.
4. `kirby.tex:331--346` (published Definition 3.1) shifts cable level
   \(r\) by \(\{(1-N)(2|r|+|\alpha|)\}\).
5. `kirby.tex:19--35` assigns a surface cobordism
   \(\Sigma\) degree \((0,(1-N)\chi(\Sigma))\).

We work intrinsically in MWW's framed \(\operatorname{KhR}_2\) convention;
no ordinary-Khovanov/MN conversion is used in the computation below.

## Forced shift of the two-representable factorization

Set \(p_y=44\), \(p_z=271\), and
\(\ell=p_z-p_y=227\). Let
\(\widehat M_R=M_R\{p_y+p_z\}=M_R\{315\}\) be the coefficient with the
one-handle normalization.

Each normalized \(\mathcal C_{p_z}\)-Hom contains shift \(+p_z=+271\).
Therefore a literal split tensor of two such representables contains total
shift \(+542\). To represent \(\widehat M_R\), whose shift is \(+315\), the
factorization must carry the residual shift
\[
315-542=p_y-p_z=-227.
\]
No choice remains here once both factors are MWW Definition 4.5 Hom spaces.

Taking the enriched \(\mathcal C_{p_z}\)-coend composes the two
representables:
\[
\int^Z
\operatorname{Hom}(JBT,Z)\otimes\operatorname{Hom}(Z,JBT')
\{-227\}
\cong
\operatorname{Hom}(JBT,JBT')\{-227\}.
\]
This map has degree zero because MWW Definition 4.5 has already normalized
composition to be grading-preserving.

Now apply split-link Kunneth. Definition 4.5 gives
\[
\begin{aligned}
\operatorname{Hom}_{\mathcal C_{271}}(JBT,JBT')
&=\operatorname{KhR}_2(
  (BT'\cup\overline{BT})\sqcup U^{\sqcup227})\{271\},\\
\operatorname{Hom}_{\mathcal C_{44}}(BT,BT')
&=\operatorname{KhR}_2(BT'\cup\overline{BT})\{44\}.
\end{aligned}
\]
Thus
\[
\operatorname{Hom}_{\mathcal C_{271}}(JBT,JBT')
\cong
\operatorname{Hom}_{\mathcal C_{44}}(BT,BT')
\{227\}\otimes A^{\otimes227}.
\]
The \(+227\) cancels the co-Yoneda residual \(-227\). Hence
\[
\widehat M_R^z(T,T')
\cong
\operatorname{Hom}_{\mathcal C_{44}}(BT,BT')
\otimes A^{\otimes227}
\]
with no remaining Hom shift. Equivalently, the raw reduced coefficient has
shift \(-315\), canceled when the global one-handle \(+315\) is restored.

## Degree of the selected class

The identity in the normalized Hom space has degree zero. For the
\(\operatorname{KhR}_2\) unknot factor, the counit cap is a disk, so MWW's
Euler formula gives it degree \(-1\). Since
\(\epsilon(X)=1\) has degree zero in the empty target, \(X\) has degree
\(+1\). Therefore the all-\(X\) diagonal in \(A^{\otimes227}\) has degree
\(+227\).

At the selected two-handle state \(r=s_0\), one has \(|r|=2\) and
\(\alpha=0\). Definition 3.1 contributes
\[
(1-2)(2\cdot2+0)=-4.
\]
The resulting absolute MWW degree is therefore
\[
227-4=\boxed{223}.
\]

The former ledger
\[
-44+227+315-4=494
\]
uses the shift appropriate to a proposed single
\(\mathcal C_{44}\)-Hom factorization. It cannot be combined with a literal
tensor of two normalized \(\mathcal C_{271}\)-representables: doing so omits
the second \(+271\) Hom normalization before co-Yoneda and double-counts the
global one-handle shift after reduction.

## Euler-shift check

No further Euler contributions are missing from 223:

- the \(+315\) one-handle shift is explicitly the correction for gluing the
  core-parallel sheets;
- the two \(+271\) Hom shifts make the merging/composition cobordism
  degree-preserving, so co-Yoneda adds no degree;
- split Kunneth is an isomorphism of link homologies, not an additional
  surface cobordism;
- the 227 cap disks used later by a detector have total map degree \(-227\),
  canceling the \(+227\) labels in the scalar evaluation, but they do not
  regrade the source class;
- the four 2-handle core disks at \(|r|=2\) are exactly compensated by the
  cabled summand shift \(-4\).

Any comparison to an ordinary Khovanov/BHPW convention still requires the
separate writhe-correction audit. It cannot change this intrinsic MWW
calculation unless the proposed comparison itself is inhomogeneous.

## Obstruction consequence

MWW Corollary 3.5 says
\(\mathcal S^2_0(S^4)\cong\mathbb Z\) concentrated in bidegree \((0,0)\).
Therefore a nonzero class in bidegree \((0,223)\) obstructs a diffeomorphism
to \(S^4\) just as effectively as a class in degree 494.

This consequence remains conditional on C and S: the two-representable
factorization, the detector's homogeneity, beta/psi descent, and three-handle
descent must still be proved. If the 223 route is adopted, every hard-coded
494 in the abstract theorem, Lean interface, S4 control, and grading ledger
must be changed or parameterized.
