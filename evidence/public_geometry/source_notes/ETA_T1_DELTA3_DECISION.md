# Single-input decision: `delta_3(eta_R[T1])`

Date: 2026-08-31  
Scope: the one number requested.  No repair of the remaining chain and no new
input.

## Binary verdict

```text
delta_3(eta_R[T1]) = -59072 != 0
delta_3(xi)         =      0

INPUT-CONFUSION CHALLENGE: SURVIVED
```

This is under the functional fixed in the request,

\[
\Delta_h(x)=\ell(\rho_h(W)-I)\Phi_h\operatorname{Sh}(x),
\qquad
\delta_3(x)=[h^3]\Delta_h(x).
\]

The Fable objection identifies a real notational trap, but its proposed value
`0` for `eta_R[T1]` drops the **outer** factor `rho_h(W)-I` from this fixed
definition.  A constant inner image does not make `Delta_h` constant.

## 1. Definition frozen independently of the old scalar

MWW's one-handle formula is the direct sum over inserted tangles modulo the two
category actions (`mww_handle_src/1handles.tex:242-299`); its algebraic form is
zeroth Hochschild homology, whose generators are diagonal trace classes and
whose relation is `fg-gf` (`:420-429`).  The Chern/Hattori identity is the trace
class of an identity (`:783-787`).  The vertical-to-horizontal source formula is

\[
t^{Sh}(p\xrightarrow{\alpha}Fp)=Sh([p,\alpha])
\]

(`bpw_src/shadows/vertical.tex:11-18,26-50`).

For this fixed coefficient, define `eta_R[T]` to be the MWW summand class of the
fixed Hattori rectangle coefficient morphism at object `T`.  Its horizontal
image is the identity on the composite coefficient tangle `B_Omega T`, together
with the common `X^227` factor.  The instantiated Hattori identities are frozen
at `PRODUCT_NORMAL_CHRISTOFFEL_THXY_MOVIE.json:748191-748219`; they are not read
from the previous `-59072` computation.

The noncommutative order is

\[
B_\Omega=W F_\Omega,
\quad T_0=F_\Omega^{-1}U_1,
\quad T_1=F_\Omega^{-1}W^{-1}U_1.
\]

Therefore

\[
B_\Omega T_0=WU_1,
\qquad
B_\Omega T_1=U_1.
\]

After the 227 common caps and the fixed one-defect identification,

\[
\Phi_h Sh(\eta_R[T_1])=u+O(h),
\qquad u=e_0-e_5.
\]

The frozen strict normalization writes this as `u`.  If one keeps an unabsorbed
projective movie sign instead, the answer below changes only by an overall
sign, never to zero.

For

\[
\xi=\eta_R[T_0]-s_{inv}\eta_R[T_1],
\]

`s_inv` is exactly the cancellation-sign calibration.  Hence, using the same
definition and sign convention,

\[
\Phi_h Sh(\xi)=(\rho_h(W)-I)u.
\]

Thus `eta_R[T1]` and `xi` are not the same input: the former has leading inner
image `u`; the latter already has one factor `rho_h(W)-I`.

## 2. Exact raw-word calculation

The verifier reads the 45,360-letter B88 word directly from
`T73_COLLAR_BRAID.json` and evaluates the unreduced Burau action with Python
unbounded integers in `Z[epsilon]/(epsilon^7)`, where
`epsilon=t-1`, `t=q^-2`, `h=q-1`.

It obtains

```text
ell (rho(W)-I) u, epsilon degrees 0..6:
  [0, 0, 0, 7384, -660412, 34814626, -1365512573]

ell (rho(W)-I)^2 u, epsilon degrees 0..6:
  [0, 0, 0, 0, 0, 0, -456576]
```

Since `epsilon=-2h+3h^2-4h^3+...`,

\[
[h^3]\ell(\rho_h(W)-I)u=(-2)^3\,7384=-59072,
\]

whereas the square starts in order six and therefore

\[
[h^3]\ell(\rho_h(W)-I)^2u=0.
\]

Consequently,

\[
\boxed{\delta_3(\eta_R[T_1])=-59072\ne0},
\qquad
\boxed{\delta_3(\xi)=0}.
\]

The source of the confusion is now explicit: the **plain shadow cubic** of
`xi` is also `-59072`, while `Delta_3(xi)` is zero.  The same matrix product
occurs in two different expressions:

```text
[h^3] ell Phi_h Sh(xi)       = -59072
[h^3] ell (rho_h(W)-I)Phi_h Sh(eta_R[T1]) = -59072
[h^3] ell (rho_h(W)-I)Phi_h Sh(xi)         = 0
```

## 3. Reproduction

```powershell
python -B D:\tmp\r6\eta_t1_delta3_reaudit\recompute_eta_t1_delta3.py --write
```

Expected terminal output:

```text
VERIFY=PASS
delta3(eta_R[T1])=-59072
delta3(xi)=0
plain_shadow_cubic(xi)=-59072
BINARY=ALIVE_ON_THIS_INPUT-CONFUSION_QUESTION
```

Artifacts:

```text
41131EC1C15118F4251EBE1A54619D3887B3BE3FFD0A39FAA11F0086EE7B4499  recompute_eta_t1_delta3.py
FE9AB4FAF27846F347D2F3BA005B30BF23442157A328CEF4C7DFB88F6D3B0BA7  ETA_T1_DELTA3_CERT.json
```

This verdict settles only the claimed input confusion.  It does not adjudicate
any other descent, geometry, or full-chain premise.
