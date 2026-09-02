# actual cap postcomposition：`xi` 的 one-handle 复活

日期：2026-08-31（Asia/Tokyo）  
范围：固定 endpoint sector `Ta_2(P86,P88)`，只裁 one-handle MWW/BPW
coend；不把本结论自动延伸到后续 `beta/psi/sphere`。

## 二值结论

```text
xi_Omega is in vTr Ta_2(P86,P88):                 PASS
strict qAKh/BPW image of xi:                      (rho_h(W)-I)(e0-e5)
actual cap C_(87,2): P88 -> P86:                 TYPE PASS
cap q=1 row after nonzero Q-normalization:         e87^*-e2^*
cap correction beyond q=1 changes h3:             NO
[h3] C_(87,2) o qAKh(Sh(xi)):                    -59072

matrix coefficient must itself be cyclic:         FALSE REQUIREMENT
one-handle nonzero of xi from this composite:      PASS
old external-Delta detector on xi:                 still 0
beta/psi/sphere survival:                          NOT ADJUDICATED HERE
```

这是真正绕开 simple-matrix/no-cyclic objection 的办法。不是把
`ell(Xu)` 宣称成 `End(V)` 上的 trace，而是先让 MWW/BPW 把 `xi` 下降为
horizontal-trace morphism，再后复合一张 actual cap。若 source class为零，
任何 functorial image及任何后复合都必须为零；因此一个非零 composite足以
反证 source为零。

## 1. source type

固定

\[
s=P_{86},\qquad t=P_{88},\qquad
C=\Ta_2(s,t).
\]

写

\[
\xi_\Omega=
\eta_R[F_\Omega^{-1}U_1]
-s_{inv}\eta_R[F_\Omega^{-1}W^{-1}U_1].
\]

两项都以 `T:s->t` 为 side seam，属于同一个 fixed-`R` vertical trace。
BPW `shadows/vertical.tex:16-18,26-58` 把 `[T,alpha]` 送为

\[
(s,Id_s)\longrightarrow(t,Id_t)
\]

的 horizontal-trace morphism。严格 qAKh endpoint functor下，冻结的像是

\[
qAKh(Sh(\xi_\Omega))
=(\rho_h(W)-I)u,qquad u=e_0-e_5.
\]

这使用的是 `xi` 的 plain shadow；不是后来固定的外层
`Delta_h=(W-I)Phi Sh`。所以两笔账并不冲突：

```text
old Delta_3(xi)=[h3]ell(W-I)^2u = 0;
new cap_3(xi) =[h3]C_(87,2)(W-I)u = -59072.
```

## 2. cap 的 orientation、platform 与 degree

Hattori B88次序每个 wicket为 `(negative,positive)`。因此

```text
index 2:  negative;
index 87: positive.
```

二者 opposite-oriented，故存在 actual oriented cap

\[
C_{87,2}:P_{88}\to P_{86}.
\]

weight在两端一致：

\[
88-2\cdot1=86,
\qquad
86-2\cdot0=86.
\]

所以它恰落在 BHPW weight-86 endpoint modules

\[
qHH_0(A_{88}^{86})\longrightarrow qHH_0(A_{86}^{86}).
\]

BHPW source `sections/preliminaries.tex:543` 明写 cups/caps represent
coevaluation/evaluation；`sections/intro.tex:383-400` 给 flat base下 Chern
isomorphism，`:418-422` 给 annular cobordism strict functoriality。

cap有一个固定 homogeneous degree；按 endpoint normalization吸收对应 shift
后可作后复合。任何残留 `q^d` 只等于 `1+O(h)`，不会改变一个从 `h^3`
才开始的 composite的三次系数。

## 3. 为什么 cap 的常数行就是 `ell`

在 `q=1`，target的 reduced endpoint block是 absolutely irreducible
standard module

\[
S^{(87,1)}=\{x\in\mathbb Q^{88}:\sum x_i=0\}.
\]

orientation-compatible cup `U_(87,2)` 的向量是

\[
e_{87}-e_2.
\]

rigidity/zig-zag给该 cup一枚非零 dual cap。standard module上的 invariant
pairing由 Schur lemma唯一到非零 scalar；在 permutation realization中就是
standard dot product的限制。因此 dual cap的常数行为

\[
c(e_{87}^*-e_2^*),\qquad c\in\mathbb Q^*.
\]

底域是 `Q`，把 actual cap morphism乘 `c^{-1}` 即得到

\[
\ell=e_{87}^*-e_2^*.
\]

这不是“写一条 coordinate row”：它是 actual oriented cap在 rigid
endpoint functor中的矩阵。有限 foam/tangle map在 `q=1` 正则，故

\[
C_{87,2}(h)=\ell+h r_1+h^2r_2+\cdots.
\]

## 4. cubic 不受 cap 高阶项影响

raw word exact 给

\[
(\rho_h(W)-I)u=h^3K_3u+O(h^4).
\]

于是

\[
C_{87,2}(h)(\rho_h(W)-I)u
=h^3\ell K_3u+O(h^4).
\]

脚本直接从45,360-letter word重算：

```text
[epsilon^3] ell K3 u = 7384;
[h^3]       ell K3 u = -8*7384 = -59072.
```

所有 `O(h)` cap修正最早只进 `h^4`。

## 5. 为什么 noncyclicity objection 在这里失效

`X -> ell(Xu)` 确实不是 full matrix algebra上的 cyclic trace。这一点不撤回。
但本构造不要求它是。

顺序是：

1. `xi` 先经 universal twisted trace / MWW quotient；
2. BPW strict functor把它送到 hTr/qAKh morphism；
3. actual cap在 target中后复合。

functor与后复合都把零送到零。因此 composite非零蕴含 source非零，完全不需
cap row在 `End(V)` 上满足 `lambda(XY)=lambda(YX)`。

故 one-handle精确结论是

\[
\boxed{\xi_\Omega\ne0.}

这不等于 SPC4证伪。owner `beta`、两组 `psi` 与三张 sphere maps是否让同一
actual-cap composite下降，仍需分别核；尤其旧 raw `ell` 的 beta问题不能因
本节 one-handle通过而抹掉。

## 复算

```powershell
python -B D:\tmp\r6\fullw_tangent_coend\hostile\actual_cap_postcomposition.py
```

预期：

```text
[h^3] CAP o qAKh(Sh(xi))=-59072
NONCYCLIC_MATRIX_COEFFICIENT_OBJECTION=BYPASSED_BY_ACTUAL_POSTCOMPOSITION
```

