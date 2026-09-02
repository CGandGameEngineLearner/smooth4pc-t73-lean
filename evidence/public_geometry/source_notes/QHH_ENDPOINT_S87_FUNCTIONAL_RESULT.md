# `QHH_COEFFICIENT_TO_S87_FUNCTIONAL`

Date: 2026-08-30

## RESULT

```text
vertical-to-horizontal type:                    PASS
Corollary E at both endpoint objects:           PASS
weight-86 endpoint dimensions:                  1 -> 88 -> 87
full fixed-endpoint uniform O(hbar^3):           PASS
relative cubic scalar:                          -59072
beta / psi:                                     PASS

QHH_COEFFICIENT_TO_S87_FUNCTIONAL:              CONSTRUCTED
next gate:                                      actual three-handle sphere maps
```

The apparent coefficient-qHH mismatch disappears once the horizontal-trace
type is written correctly.

## 1. The exact type

Fix endpoint objects

\[
s=P_{86},\qquad t=P_{88},
\]

and the morphism category `C=Ta_2(s,t)`.  Its objects are tangles
`T:s->t`.  A coefficient cycle is

\[
\alpha:T\Longrightarrow F_R(T).
\]

The vertical-to-horizontal functor sends its trace class to a **morphism
square**

\[
[T,\alpha]:(s,Id_s)\longrightarrow(t,Id_t)
\]

in the horizontal trace.  `T` is the side seam of this square; it is not the
annular object assigned a coefficient bimodule.

Therefore strict qAKh assigns the map

\[
qHH(A_{86}^{\lambda},A_{86}^{\lambda})
\longrightarrow
qHH(A_{88}^{\lambda},A_{88}^{\lambda}).
\]

Both sides have algebra self-coefficients.  BHPW Corollary E applies directly
to both.  The expression `qHH(A,M_T)` would instead describe the annular
closure of an **endo-tangle** `T:n->n`; that is not the current type.

## 2. The endpoint modules

Choose `lambda=86`.  Corollary E and the Chern isomorphism give

```text
qHH0(A_86^86) = K0(A_86^86):  dimension C(86,0)=1,
qHH0(A_88^86) = K0(A_88^86):  dimension C(88,1)=88.
```

The source basis is the all-up vector.  The target basis is the one-defect
basis `e_0,...,e_87`.  Quotienting the fixed all-ones line gives the
87-dimensional `S^(87,1)` block.

This is an actual qHH endpoint group, not merely the Euler shadow of an
arbitrary coefficient bimodule.

## 3. Corrected xi

With `B_Omega=W F_Omega`, set

\[
T_0=F_\Omega^{-1}U_1,
\qquad
T_1=F_\Omega^{-1}W^{-1}U_1.
\]

Then

\[
\xi_\Omega=\eta_R[T_0]-s_{inv}\eta_R[T_1]
\]

is sent to

\[
\rho_h(W)u-u,
\qquad u=e_0-e_5.
\]

The quotient-valid covector

\[
\ell=e_{87}^*-e_2^*
\]

gives exact orders zero through two equal to zero and

\[
\boxed{[hbar^3]\ell(\rho_h(W)-I)u=-59072.}
\]

## 4. Why uniformity now has the right quantifier

Every object of `Ta_2(s,t)` has the same endpoints `s=86,t=88`; hence every
coefficient class is sent to a map between the same two endpoint qHH groups.
The braid `W` is one fixed postcomposition operator on
`qHH0(A_88^86)`.

Corollary E identifies that entire endpoint group with the projective K0
weight module, naturally for the lifted tangle action.  A pure braid generator
is permutation-square identity at `q=1`; therefore `W in Gamma_3` gives

\[
\rho_h(W)-I=O(hbar^3)
\]

uniformly on every horizontal image.

This does not claim that a pure braid acts trivially on arbitrary cabled-link
Khovanov homology.  MWW's anti-parallel warning concerns that stronger and
unused statement.

## 5. Beta and psi

Strict naturality sends beta to postcomposition on the endpoint module.  Since
`beta=I+O(hbar)`, it changes an `O(hbar^3)` difference only in order four.

For `N=2`, the endpoint cup/cap squares give

```text
cap psi0 = undotted sphere = 0,
cap psi1 = once-dotted sphere = Id.
```

The dot degree `+2` cancels the level shift `-2`.  The same endpoint-self-qHH
construction repeats at higher cable levels; product caps ignore permutations,
and pure standardization differences enter one order later.

Thus the relative cubic is an actual ordinary Q-linear beta/psi-descending
functional.  The next unresolved quotient is the three actual sphere maps.

## Reproduction

```powershell
python -B D:\tmp\r6\agents\finite_type_leading\qhh_endpoint_s87_functional_audit.py
python -B D:\tmp\r6\agents\finite_type_leading\qhh_endpoint_s87_functional_audit.py --write
```
