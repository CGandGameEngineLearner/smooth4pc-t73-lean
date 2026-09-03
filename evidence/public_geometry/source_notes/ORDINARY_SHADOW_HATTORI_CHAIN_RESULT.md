# `HATTORI_U_OMEGA_TO_BPW_SHADOW_CHAIN_MAP`

日期：2026-08-30  
范围：每个整数 `Omega` 的 symbolic framed coefficient `R[Omega]`、HATTORI rectangle decomposition、`q_trace=1` ordinary BPW joint preshadow；文末纳入 subsequent `r_xy psi^[0]` follow-up。

## 判词

```text
R_Omega finite BN/foam generator movie:       CONSTRUCTED PARAMETRICALLY
u_Omega chain representative:                 CONSTRUCTED up to standard functorial sign
ordinary BPW coefficient shadow map:          CONSTRUCTED for representable R_Omega family
left/right M_R dinaturality:                   AUTOMATIC from universal preshadow restriction
actual numeric Omega needed:                   NO
shadow image / one-handle class nonzero:        PASS FOR EVERY Omega
t73-vs-identity/anchor relative distinction:    OPEN
later quotient survival:                         FAIL at r_xy psi^[0]; sphere not reached
psi follow-up:                                  r_xy psi^[0] KILLS; sphere unnecessary
```

这次补上的是真正缺口中的“map exists”，不是又一张 character。每个 `Omega` 都有同一套 finite movie schema；`u_Omega` 是明确的 closed chain element；ordinary BPW vertical-to-horizontal trace把它送到 annular closure，并自动商掉 MWW one-handle left/right action relations。

这里必须分清三层：specific `u_Omega` 的 one-handle class已经由identity-shadow证明非零；raw `S^(626,4)` degree4+只关系 `w` 能否与 identity/anchor区分；subsequent owner audit则证明该特定类被 `r_xy psi^[0]` 杀掉。

## 1. 每个 `Omega` 的规范 framed representative

normal-field certificate给出同一 core/CUT output的 `Omega=0` 与 `Omega=1` completions。一般地，固定 exact 630 CUT arcs，并选择如下 representative：

1. feed、两个 cancellation bands、re-emission全部平行运输 normal field；
2. `r_xy` 使用已认证的 `+1` blackboard correction；
3. 把 `m_2` 的全部额外 longitudinal rotation集中到第一张 certified z--z connector rectangle；
4. 在该 rectangle内插
   \[
   (s,z)\mapsto(s,e^{2\pi i\Omega s}z).
   \]

support固定为

```text
R:c_m_2_neg:0309
R:c_m_2_pos:0000
normalized base connector [0,1].
```

对每个整数 `Omega`，`TWIST_BOX_m2(Omega)` 展开成有限个带符号 two-strand full-twist generators。任意同一 oriented core、同一 CUT endpoints、总 winding为 `Omega` 的 framed completion都与这个 localized representative framed-isotopic rel boundary。因此这不是挑 `Omega=0`；它是全部 framing classes的一组规范代表。

actual frozen framing虽然不可识别，但必落在其中某个整数 `Omega`。后面的 construction对所有整数定义，所以不需要先知道是哪一个。

## 2. finite BN/foam generator movie

机器证书把 movie写成七段 macro generators；每段都绑定现有 exact ledger：

| stage | generator | exact content |
|---:|---|---|
| 0 | `FRAMED_R_OMEGA` | 630 oriented CUT arcs、1260 endpoints、localized `TWIST_BOX_m2(Omega)` |
| 1 | `STANDARD_Z_WICKET_CLOSURE` | 542 negative/positive endpoint pairings by `(owner,base_letter_index)` |
| 2 | `HATTORI_RECTANGLE_ISOTOPY` | 88 y-touching open paths + 227 z-only connector strips；全部 rectangles disjoint |
| 3 | `PURE_WICKET_BRAID_IDENTIFICATION` | 44 west/44 east wickets；252 local factor bindings give exact `w73`；framing contributes `F_Omega` |
| 4 | `CHAIN_CYCLE_U_OMEGA` | `Id_(CKh(w73 F_Omega)) tensor X^tensor227` |
| 5 | `ORDINARY_BPW_VERTICAL_TO_HORIZONTAL_TRACE` | `q_trace=1` horizontal/annular closure |
| 6 | `CAP_Z_ONLY_STRIPS` | 227 caps, each `epsilon(X)=1`, total scalar `+1` |

“macro”不是省略无限数据：stage 0对固定整数 `Omega` 展开为有限 crossing/cup/cap word；stages 1--3分别由 CUT、315-component HATTORI ledger及252-row factor binding逐项固定。movie的 canonical SHA已写入 JSON。

## 3. `u_Omega` 是 actual chain cycle

HATTORI simultaneous rectangle isotopy给 chain-level monoidal factorization

\[
C_{R[\Omega]}
\simeq
CKh(w_{73}F_\Omega)\otimes CKh(U)^{\otimes227}
\]

up to the standard Khovanov functorial sign。定义

\[
\boxed{
u_\Omega=operatorname{Id}_{CKh(w_{73}F_\Omega)}
\otimes X^{\otimes227}.}
\]

- identity是 endomorphism complex中的 closed degree-zero chain map；
- crossingless circle factor是 `A=Q[X]/(X^2)`，`d(X)=0`；
- tensor differential故满足 `d(u_Omega)=0`。

在 `Hom(T,F_{R[Omega]}T)` 与

\[
KhR(R[\Omega]\cup T\cup\overline T)
\]

的标准 closure identification下，这正是 coefficient homology class，而不是 whole-complex Euler polynomial。

MWW framed convention固定

```text
q(1)=-1, q(X)=+1, q(cap)=-1.
```

正确 degree ledger：

```text
Id_B in End(B)                         (0,0)
same identity in raw closure           (0,-44)
X^227 raw circle degree                 (0,+227)
raw closed-link class                   (0,+183)
227 plain-cap map degree                (0,-227)
post-cap circle-sector degree           (0,0)
one-handle M_R shift, in this task      +315
bare u_Omega degree in M_R              (0,+498)
```

outer cable shift是后续 two-handle/cabled quotient中的 `-4`；one-handle degree ledger必须先单列，不能与 `+315` 混写成 “net `+311`”。施加该后续 shift时，bare class从 `+498` 到 `+494`。

plain caps把 `X^227` circle sector的 `+227` 送到 degree-zero scalar；它们不把 source class `u_Omega` 重定级为零。以上修正不影响 `d(u_Omega)=0` 或 shadow map的存在。

## 4. ordinary BPW shadow map

令 joint tangle `R[Omega]` 定义 compose-with-`R[Omega]` coefficient functor `F_R`，并取 representable bimodule

\[
M_{R[\Omega]}(T,T')
\cong\operatorname{Hom}(T,F_R(T')).
\]

BPW `shadows/vertical.tex:26-58` 给 natural functor `vTr -> hTr`，并证明有 left duals 时 universal preshadow限制到 morphism category就是 universal twisted trace。令 twist为 ordinary `q_trace=1`，得到

\[
\operatorname{Sh}_\Omega:
HH_0(\Ta_2;M_{R[\Omega]})longrightarrow
\operatorname{Hom}_{hTr}(\operatorname{cl}_h T,operatorname{cl}_h F_RT).
\]

于是对任何 cyclically composable coefficient actions `f,g`，

\[
\operatorname{Sh}_\Omega(fg)=
\operatorname{Sh}_\Omega(gf).
\]

这就是 MWW one-handle quotient要求的 left/right dinaturality；无需逐个重做 off-diagonal relations。

该 construction不使用：

- `w73` central；
- q-twisted cyclicity；
- `dg qHH = MWW HH0` 的同构。

此前 dg/cohomology mismatch阻断的是自动同构与计算，不阻断这个 ordinary representable-coefficient shadow map。

## 5. shadow image

应用 stage 5--6：

\[
\operatorname{Sh}_\Omega([u_\Omega])
=operatorname{cl}_{ann}
\bigl(\operatorname{Id}_{w_{73}F_\Omega}\bigr)
\cdot\prod_{i=1}^{227}\epsilon(X)
=\operatorname{cl}_{ann}
\bigl(\operatorname{Id}_{w_{73}F_\Omega}\bigr),
\]

up to a global sign。全局 sign只把class乘 `-1`，不影响nonzero。

annular closure是一个非空 braid closure。忘掉 annular grading得到其 ordinary Khovanov complex；在 `Q` 上该 homology非零（也可由Lee orientation classes作为下界）。所以 annular object不 contractible，其 identity不可能 null-homotopic。于是

\[
\boxed{\operatorname{Sh}_\Omega([u_\Omega])\ne0}
\]

对每个整数 `Omega` 成立。若 source `HH_0` class为零，任何线性shadow map的image都应为零；故

\[
\boxed{[u_\Omega]\ne0\text{ in the one-handle coefficient }HH_0.}
\]

这不使用 raw `M_4`。raw exterior/M4计算的是 aggregate joint cup--cap functional，回答的是另一个问题：`w` 与 identity/anchor是否被该 functional区分。当前状态应分列：

```text
(a) individual u_Omega one-handle class:             NONZERO / PASS
(b) w-vs-identity or anchor relative distinction:    OPEN
(c) later quotient survival:                          ZERO by r_xy psi^[0]
```

因此 raw `M_4` degree4+ 或合法 gate-point Young action仍有价值，但不再是证明 `u_Omega` 本身非零的前件。

## 6. 为什么 unknown `Omega` 不再阻断 map

不同 `Omega` 只改变：

1. stage 0中 full-twist generators的个数/符号；
2. open factor `F_Omega`。

rectangle disks、227 circle factors、`X` labels和 ordinary shadow formalism全部不变。framed isotopy functoriality把任意同 winding representative的 identity cycle送到同一 projective class。因此得到一族

\[
\{(R[\Omega],u_\Omega,\operatorname{Sh}_\Omega)\}_{\Omega\in\mathbb Z}.
\]

actual geometry对应其中某一项；定义与individual nonzero都对全体 `Omega` 成立，故 framing ambiguity在 one-handle class这一级已经绕过。

## 7. two-handle follow-up

后续 owner audit已追踪227个 `X` labels：它们全部属于 `m_2` z-only strips，`r_xy` pair上没有dot。因此

\[
u_\Omega=\psi_{r_{xy}}^{[0]}(v_\Omega^{m_2}).
\]

对 `N=2`，`psi^[0]` image在two-handle cabled quotient中归零；故 individual class虽然在one-handle `HH_0` 非零，却不进入后续 quotient。three-handle sphere map无需再用来杀它。详见 `PSI0_OWNER_KILL_RESULT.md`。

这不撤销本文件构造的 ordinary shadow map；它只更新最终 survival状态。

## 8. 复算

```powershell
python -B D:\tmp\r6\agents\finite_type_leading\ordinary_shadow_hattori_chain.py --write
```

机器证书：`ORDINARY_SHADOW_HATTORI_CHAIN_CERT.json`。
