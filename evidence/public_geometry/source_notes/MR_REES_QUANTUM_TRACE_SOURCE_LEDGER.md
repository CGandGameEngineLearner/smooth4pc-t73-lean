# MR Rees / coefficient quantum trace source ledger

## Scope and verdict

This ledger audits the construction in `MR_REES_QUANTUM_TRACE_RESULT.md`.
The conclusion survives, with one clarification: the Burau operator is not an
internal endomorphism of the raw coefficient bimodule.  It acts after the
universal quantum vertical-to-horizontal shadow.  The resulting composite is
nevertheless a genuine map from the coefficient quantum trace, and its
divided cubic specializes to an ordinary MWW `HH_0` functional.

```text
q-coefficient trace:                    CONSTRUCTED
respect for qTr relations:              PROVED BELOW
specialization to ordinary MWW HH0:     PROVED BELOW
uniform h^3 divisibility:               PROVED ON FULL ENDPOINT TARGET
divided ordinary functional:            PROVED BELOW
selected cyclic submodule flat:         CONSEQUENCE, NOT PREMISE
internal W action on raw M_R:            NOT CLAIMED
```

## Object and arrow ledger

| ID | object/arrow | domain -> codomain | degree / ring | source |
|---|---|---|---|---|
| L1 | `C^pre` | objects are tangles `T:P86->P88`; morphisms are the pregraded form of the MWW/BHPW tangle category | bigraded over `Q` | MWW `D:/tmp/r6/mww_handle_src/1handles.tex:542-572`; pregraded/enriched translation `:610-623`; BPW `D:/tmp/r6/bpw_src/traces/graded.tex:70-85` |
| L2 | actual coefficient `M_R(T,T')` | `C^op x C -> grVect_Q`; concretely `KhR(R union T' union bar(T))` with the MWW shift | homogeneous left/right gluing actions | MWW raw summands/actions `1handles.tex:242-299`; actual action-compatible Hattori family supplied by E1 and actual-PD unit certificate `D:/tmp/t73_actual_cable_unit/ACTUAL_PD_CABLE_UNIT_CERT.json` |
| L3 | `R_q` | `Q[q,q^-1]` | `deg q=0` as coefficient; powers record internal degree in cyclicity | BPW `traces/graded.tex:90-115` |
| L4 | `qTr_q(C,M_R)` | cokernel of `directsum_T M_R(T,T) tensor R_q` by `L_f(m)-q^|f| R_f(m)` | graded `R_q`-module | BPW universal quantum trace formula `traces/graded.tex:90-128`, pulled back along the E1 coefficient equivalence |
| L5 | specialization | `qTr_q tensor_{R_q} R_q/(q-1) -> HH0(C;M_R)` | `q=1` | direct cokernel base change; ordinary MWW definition `1handles.tex:420-430` |
| L6 | selected lift `[v]_q` | element of `qTr_q`; representative `H^-1(Id_U tensor X^tensor227)` at `T1=B_actual^-1 U` | homogeneous; one-handle quantum degree 498 before later cable shift | E1 actual Hattori construction; identity trace convention MWW `1handles.tex:783-787`; Frobenius `X`/counit BHPW `D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/preliminaries.tex:601-633` |
| L7 | quantum vertical-horizontal shadow `Sh_q` | `qTr_q(C,M_R) -> Hom_qhTr((P86,Id),(P88,Id))` | degree zero after MWW shifts | ordinary vertical-horizontal construction BPW `D:/tmp/r6/bpw_src/shadows/vertical.tex:11-58`; quantum trace deformation `traces/graded.tex:118-135`; qvTr-to-qhTr realization `D:/tmp/r6/bpw_src/quantum/qannulus.tex:289-309` |
| L8 | strict endpoint functor | the L7 Hom-space -> `Hom_{R_h}(E_86,E_88)` with `E_86=(V_h^tensor86)_86`, `E_88=(V_h^tensor88)_86` | `R_h=Q[[h]]`, `q=1+h` | weight modules/action BHPW `D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/intro.tex:280-299`; strict q-annular functor `:378-422`; exact endpoint typing `D:/tmp/r6/agents/finite_type_leading/QHH_ENDPOINT_S87_FUNCTIONAL_RESULT.md:1-48` |
| L9 | `rho_h(W)-I` | `E_88 -> E_88` | degree zero; image lies in `h^3 E_88` | physical word/Gamma3 recomputation `D:/tmp/r6/AUD_B/AUD_B_REPORT.md:305-339`; group-filtration proof uses pure generators `I+O(h)` and `[I+O(h^p),I+O(h^q)]=I+O(h^(p+q))` |
| L10 | normalized cap `C_hat_87,2(h)` | `E_88 -> E_86 ~= R_h` | normalized total degree zero; any original fixed degree is removed by its invertible q-shift | strict tangle action/functoriality BHPW `intro.tex:252-299`; actual cap typing and normalization `D:/tmp/r6/fullw_tangent_coend/hostile/ACTUAL_CAP_POSTCOMPOSITION_DECISION.md:34-91` |
| L11 | detector `D_h` | `qTr_h -> R_h`, `D_h=C_hat_87,2(h)(rho_h(W)-I)Sh_h` | `R_h`-linear, degree zero, divisible by `h^3` | composite of L7-L10 |
| L12 | divided detector `D_3` | `HH0(C;M_R) -> Q` | coefficient of `h^3` | quotient/division proof below |

Here `qTr_h=qTr_q tensor_{R_q}R_h`.  All tangles in `C` have the same
boundary objects `P86,P88`; therefore L7 always lands in the same horizontal
Hom-space.  The fixed cap and `W` postcomposition are consequently defined on
the image of every trace class, not merely on the selected class.

## Proof that `D_h` respects every q-trace relation

Take homogeneous `f:T->T'` of degree `d` and a cyclically typed coefficient
element `m`.  Let

\[
r=L_f(m)-q^dR_f(m).
\]

The universal quantum trace relation is exactly the assertion

\[
Sh_q(L_f(m))=q^d Sh_q(R_f(m)).
\]

This is BPW's deformed cyclicity
`t_y(F(f)g)=q^{|f|}t_x(gf)` (`traces/graded.tex:90-107`).  E1's two action
squares identify the MWW left/right gluing maps with the two sides of this
relation.  Hence `Sh_q(r)=0`.  Since the endpoint functor, `rho_h(W)-I`, and
the normalized cap are linear maps of the displayed fixed Hom-space,

\[
D_h(r)=\widehat C(h)(\rho_h(W)-I)Sh_h(r)=0.
\]

Thus `D_h` is defined on the quotient `qTr_h`; it is not a functional first
defined on a shadow space and then informally pulled back.

## Specialization and division

`qTr_q` is an explicit cokernel over `R_q`.  Tensoring its presentation with
`R_q/(q-1)` replaces every coefficient `q^d` by one.  Right exactness of
tensor product gives

\[
qTr_q\otimes_{R_q}R_q/(q-1)
\cong
\frac{\bigoplus_T M_R(T,T)}{\langle L_f(m)-R_f(m)\rangle}
=HH_0(C;M_R).
\]

No flatness of the whole trace module is needed for this equality.

By L9, `rho_h(W)-I=h^3K+O(h^4)` on the entire endpoint module, not only on
`u`.  The cap and shadow are h-adically regular.  Therefore

\[
D_h(qTr_h)\subseteq h^3R_h.
\]

As `R_h` is a domain, there is a unique `R_h`-linear map
`D'_h:qTr_h->R_h` satisfying `h^3D'_h=D_h`.  Define

\[
D_3(\bar x)=D'_h(x)\bmod h
\]

for any lift `x` of `bar x` in `qTr_h/h`.  If `x'=x+hy`, then
`D'_h(x')-D'_h(x)=hD'_h(y)`, so this definition is lift independent.  Under
the specialization isomorphism above, `D_3` is therefore an ordinary MWW
`HH_0` functional.

## Selected value and flatness

The selected representative satisfies

\[
Sh_h([v]_h)=u_h,
\qquad u_h\bmod h=e_0-e_5.
\]

The direct raw-word evaluation gives

\[
D_h([v]_h)=-59072h^3+O(h^4),
\qquad D_3([v])=-59072.
\]

Consequently `[v]` is nonzero in ordinary MWW `HH_0`.  Moreover, if a
nonzero `a(h)` annihilated `[v]_h`, applying `D_h` would give
`a(h)(-59072h^3+O(h^4))=0` in the domain `R_h`, impossible.  Hence the cyclic
submodule `R_h[v]_h` is torsion-free; over the DVR `R_h` it is free rank one.
This proves the selected flat lift as a consequence of the detector rather
than assuming flatness to build it.

## Retained boundary

The construction does not define `rho_h(W)-I` internally on every raw
`M_R(T,T')`.  It defines a coefficient-compatible quantum shadow and then
acts on the fixed endpoint target.  That is enough to produce `D_3` on the
source quotient.  Full-q or later-handle descent is not asserted here.
