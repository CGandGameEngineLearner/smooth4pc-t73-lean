# TL cell ideal closure audit

Date: 2026-08-30

## Verdict

```text
actual y one-handle action:              full sign parabolic B_(44,44)
native owner partition:                  none

S^(86,2) action-closed psi0 ideal rank:  3740 / full
Z3 survives this ideal:                  no
old rank-six result:                     bare columns only

project TL convention:                   unscaled Burau, eigenvalues (1,-t)
S^(87,1) beta relation rank:             44
beta coinvariant dimension:              43
rank(W-I):                               4
rank(beta relations plus W-I):           48, signal +4
oriented cross-cup signals surviving:    168/168

fixed-R relative one-cup class:          PASS before sphere
psi through-degree protection:           PASS
ANCHOR W=I control:                      zero
```

本轮修正两个相反的旧误差：`S^(86,2)` 的 rank6 没闭合 MWW one-handle actions，因此整个 cell 实际被 psi0 ideal 杀掉；`S^(87,1)` 若误用 scaled `q*Burau` 会被全杀，但项目真实 convention 是 unscaled Burau，one-cup signal仍存活。

## 1. Actual action algebra

MWW `1handles.tex` 中，`P_44` 只记44个 negative 与44个 positive points。三球 category 的 objects 是全部具有该 oriented boundary 的 tangles，morphisms 是全部相应 KhR groups；Theorem `mainonehandle` 对所有 tangle pairs 的两侧 actions 取 coinvariants。

因此实际 braid subgroup是 `B_(44,44)`，在 q=1 至少给 `S44^- x S44^+`。这里没有 rxy/m2 owner partition。Owner只是 frozen presentation provenance，不是 MWW one-handle category的native grading。

psi relation在 one-handle skein/coend之后施加。同一 lasagna filling 的 alternate cuts由 full `P_44` actions识别，因此承重对象是 action-closed psi ideal，不是选定六个 raw columns。

## 2. S^(86,2) is fully killed

Pair-interleaved order中 even indices为negative，odd indices为positive。六个 raw `psi_rxy` directions含三类种子：

```text
e02: --
e13: ++
e01: mixed
```

Sign-parabolic orbit sizes为：

```text
--: C(44,2)=946
++ : C(44,2)=946
mixed: 44*44=1936
total: 3828 = dim M2([88])
```

Incidence map `D:M2([88])->M1([88])` rank88，所以 harmonic projector rank为 `3828-88=3740`。Orbit union含全部 raw pair basis，其投影正是完整 `S^(86,2)`。

完整502-entry Z3 ledger逐点 incidence boundary为0，因此 `P Z3=Z3`，并有有限表达：

```text
Z3 = sum_(a<b) z_ab * P e_ab.
```

结论：Z3属于 full one-handle action closure of `im psi_rxy^[0]`。旧 `rank(base6,Z)=7` 与旧 functional只描述 bare initial columns，不能判 ideal membership。

```text
S^(86,2) candidate = CLOSED.
```

## 3. Correct S^(87,1) beta convention

权威 project convention来自 `full_trace_detector/verify_full_trace.py`：

```text
B_i(t) = [[1-t,t],[1,0]]
generator eigenvalues = (1,-t)
```

Trivial/through eigenvalue必须保持1，所以不能乘 q。Scaled `q*Burau` 把 trivial eigenvalue改掉，算的是错误 beta relation。

脚本逐字复用 project 的右乘 convention `M <- M rho(letter)`，再 quotient fixed all-ones line：

```text
red(M)[i,j] = M[i,j] - M[87,j], i,j<87.
```

在 `p=1,000,000,009, t=3` 上计算 full 45,360-letter B88 word及：

```text
Tr = sigma1^2 sigma3^2
Tm = sigma5^2 sigma7^2 ... sigma87^2
```

得到：

```text
rank [Tr-I,Tm-I]       = 44
left quotient dim      = 43
right quotient dim     = 43
rank(W-I)              = 4
rank after adjoining W = 48
```

Left/right都新增4。一个 good specialization 的非零 minor证明 generic beta quotient中有四维 W signal。

## 4. Physical one-cup choices

取 `u_ij=e_i-e_j`，其中 `i in {0,1,2,3}` 是 rxy passage，`j in {4,...,87}` 是 m2 passage。共有336个 cross differences，168个是 opposite orientation，可由普通 oriented cup实现。

脚本逐一把 `(W-I)u_ij` 约到 beta relation quotient：336/336 nonzero，尤其168/168 oriented choices全部nonzero。

可选：

```text
U1 = one cup W1^- (index0) to W3^+ (index5)
all other 86 strands through
```

## 5. Same-fixed-R relative class

Hattori factorization对任意 right-whiskered ordinary object T 给 component：

```text
eta_Rw[T] -> Id_(B_w,Omega T) tensor X^227.
```

所有 terms位于同一个 fixed coefficient `M_Rw[Omega]`，所以无需 kappa_W。

零 framing时可写：

```text
T0=U1
T1=W^-1 U1
```

实际 open word是 `B_w,Omega=W F_Omega`，故 framing-corrected objects应为：

```text
T0=F_Omega^-1 U1
T1=F_Omega^-1 W^-1 U1
```

于是：

```text
B_w,Omega T0 = W U1
B_w,Omega T1 = U1
```

定义

```text
xi_Omega = eta_Rw[T0] - s_inv * eta_Rw[T1]
```

其中 `s_inv` 是固定 foam functor对显式 `W W^-1` cancellation movie给出的 sign。把该 sign写进定义即可；它不是跨 coefficient comparison。

Ordinary BPW shadow给：

```text
Sh(xi_Omega) = [Id_(W U1)] - [Id_U1].
```

其 S^(87,1) beta quotient signal由上一节证明非零。因此 xi在 one-handle plus beta quotient中非zero。

两项同 boundary、alpha/r 与 degree；degree沿用 current Hattori class `(0,+498)`。`W^-1U1` 与 framing-corrected版本都是合法 ordinary oriented tangle objects。

## 6. Psi filtration

`psi_rxy` pair creation增加4个 y endpoints，即至少两 cups，所以其 TL ideal through degree不超过84。左右 tangle actions不能提高 through degree。

新 xi位于 one-cup `through=86`, 即 `S^(87,1)`。故它不在 rxy psi ideal中。m2 pair creation加入更多 cups，bound更低，同样不能触及。

这与旧 identity class被 psi0杀不矛盾：旧类在 two-cup/through84 sector；新类刻意提升到 one-cup/through86。

## 7. ANCHOR and remaining gate

对 `W=I` 的 standard control，framing-corrected `T0=T1`，所以 xi在 source coend中exact zero。

当前状态：

```text
ordinary objects/cycles:      PASS
same fixed R coend:           PASS
beta coinvariant:             PASS
psi through filtration:       PASS
ANCHOR:                       ZERO
three-handle sphere quotient: NOT CHECKED
```

这是第一条不被 full S^(86,2) ideal或 S^(87,1) beta杀掉的 actual TL candidate。下一承重门是 PRODUCT_NORMAL/actual sphere maps及shadow naturality。

## 8. Reproduction

```powershell
python -B D:\tmp\r6\agents\finite_type_leading\tl_cell_ideal_closure_audit.py --write
```

Machine certificate: `TL_CELL_IDEAL_CLOSURE_CERT.json`.
