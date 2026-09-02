# 全 cable lattice 的 common-target Reynolds / foam family

日期：2026-08-31（Asia/Tokyo）  
范围：从已经 actualized 的 one-handle closed cap出发，为每个 physical-copy selection构造共同 target；证明任意 cable multiplicity下的 owner-beta、`psi0/psi1` 相容。只到 `h^3` leading，不碰 sphere。

## 总判

```text
stable positive-braid common target:          PASS at h3
all-k physical-copy beta:                     PASS at h3
all-k psi0:                                   0
all-k psi1:                                   identity

current pair C_(87,2) U_(0,5):               PASS beta/psi, h3=-59072
alternative pair C_(87,0) U_(1,86):          PASS beta/psi, h3=-115456

full q-series:                                NOT PROVED
sphere maps:                                  NOT INCLUDED
```

本结果不靠 `a,b<=8` 的有限扫推广。有限扫只作回归；全量词来自 stable permutation braid、MWW gluing自然性、binomial orbit恒等式与 `N=2` core-disk Frobenius求值。

## 1. actual common target怎么造

固定 cable state

\[
n=(k_i^-,k_i^+)_{i,\pm}
\]

和一个 physical-copy occupancy `a`。在每个 owner/sign block内选 canonical copies为字典序最前的 `a_i^sign` 个。

对任意另一 selection `S`，取唯一的 stable positive permutation braid：

1. 把 `S` 中的 copies按原相对次序移到 canonical前段；
2. 未选 copies也保持原相对次序；
3. 每对 strands至多交一次。

这是相应 coset的唯一 minimal positive lift。其 crossing数为

\[
\sum_j(s_j-j).
\]

应用 BHPW strict tangle functor后，所有 selections进入同一个 ordered target。再按固定次序接：

- MWW `Phi` 所附的两枚 individual W2 core disks；
- 旧 closed cap；
- 其余 canonical core caps。

这些不是“假装 `R` split”。stable braid正是 MWW 定义的 owner tubular-neighborhood beta diffeomorphism；gluing/Phi compatibility把整个 non-split coefficient一起运过去。

### sign与degree

- beta standardization是 degree `(0,0)`；
- strict movie固定 functorial sign；
- `psi1` raw degree `+2`，level shift `-2`，total `0`；
- `psi0` total degree `-2`。

不同 stable lifts的差落在 stabilizer/pure braid。stabilizer在 `h=0` 固定相同 labels；pure part为 `I+O(h)`。closed witness从 `h^3` 开始，所以这些差只进 `h^4+`。

## 2. beta：任意 `k`，不是 passage averaging

令

\[
G_n=\prod_{i,\pm}S_{k_i^\pm}.
\]

对 common-target cap summands取 Reynolds sum。任意 `beta_i(b)` 把 selection summands置换；stable standardization后的残差是上一节的 stabilizer/pure braid。因此

\[
\Lambda_n^{(3)}\beta_i(b)=\Lambda_n^{(3)}
\]

对所有 `i,b,k` 成立。

这里平均的是 physical cable copies。base ledger中的 `rxy=2`、`m2=42` 是每条 copy穿 y gate的 passage数，绝不进入 Reynolds multiplicity。base `B_(1,1)` 的 constant permutation本来就是 trivial，故 raw值分别保留：

```text
-59072,
-115456.
```

## 3. orbit theorem：一般公式

occupancy orbit size为

\[
O(n,a)=\prod_{i,\pm}{k_i^\pm\choose a_i^\pm}.
\]

沿 `psi_i` 加一负一正 pair时，distinguished zero-extension的 Reynolds平均缩放为 `O_source/O_target`；dual row乘倒数

\[
d_i(n,a)=\frac{O(n+e_i,a)}{O(n,a)}.
\]

任意路径上因子 telescope：

\[
\prod_e d_e=\frac{O(n_{final},a)}{O(n_{initial},a)}.
\]

所以不同 owner顺序与同 owner重复添加自动相容；无需有限枚举归纳。

### 当前 pair

```text
U_(0,5):  rxy- , m2+
C_(87,2): rxy- , m2+
```

整张 closed pattern占用同一枚 `rxy-` copy与同一枚 `m2+` copy：

\[
O_{cur}=k_{rxy}^-k_{m2}^+.
\]

故

\[
d_{rxy}=\frac{k_{rxy}^-+1}{k_{rxy}^-},qquad
d_{m2}=\frac{k_{m2}^++1}{k_{m2}^+}.
\]

### robust alternative

```text
U_(1,86): rxy+ , m2-
C_(87,0): m2+ , rxy-
```

占用四个 sign blocks：

\[
O_{alt}=k_{rxy}^-k_{rxy}^+k_{m2}^-k_{m2}^+.
\]

所以

\[
d_{rxy}=
\frac{(k_{rxy}^-+1)(k_{rxy}^++1)}{k_{rxy}^-k_{rxy}^+},
\]

`m2` 同式。其它 owner factor为1。

## 4. psi：为什么是两枚 disks，不是 reverse ribbon

MWW `psi` 在 W1侧是一条 connected ribbon annulus；但 cabled module经 `Phi` 进入 W2时，新增的负、正 cable各自接一枚 individual 2-handle core disk。compatible target detector使用的局部 map因此是

\[
\epsilon\otimes\epsilon,
\]

不是只在 W1侧倒转 annulus所得的 `epsilon o m`。

在 `A=Q[X]/X^2` 中

\[
\epsilon(1)=0,qquad\epsilon(X)=1,
\]

且

\[
\psi^{[0]}(1)=1\otimes X+X\otimes1,qquad
\psi^{[1]}(1)=X\otimes X.
\]

于是

\[
(\epsilon\otimes\epsilon)\psi^{[0]}=0,
\qquad
(\epsilon\otimes\epsilon)\psi^{[1]}=1.
\]

### selected-new copy 防火墙

仅写上式还不够：stable shuffle可能把 newly created copy搬进 selected
cap/cup slot。承重对象因此不是“这两枚 disks永远孤立”，而是全局 relative
head filtration

\[
\nu=\#\{\text{psi-added factors carrying }1\}.
\]

target covector在 `nu=0` 取前述 Reynolds endpoint row，在所有 `nu>0` 上定义为
零。任一 physical-copy permutation或 stable shuffle只移动 `1` 所在的 copy，
不改变 `nu`。于是：

```text
selected old copy + psi0: nu=1 -> 0;
selected new copy + psi0: nu=1 -> 0;
selected old/new copy + psi1: nu=0 -> source row.
```

脚本把 one-selected-sign 的 old/new 两种，以及 both-signs alternative 的
`old/old,new/old,old/new,new/new` 四种逐项展开；每个 psi0 term均为0、psi1
head均为1。这个 filtration 才是 `REYNOLDS_SELECTED_NEW_COPY_PSI0_FOAM_SQUARE`
的证明；孤立 `epsilon tensor epsilon` 只负责其局部 `0/1` 校准。

这里的 factor separation不是从 raw tensor table猜的。既有 constant-edge theorem
已在完整 fixed-weight source上把 edge写成

\[
Q_t^{-1}(Id_{old}\otimes T_{local})Q_s.
\]

old/new residual只是一枚 pure braid `I+O(h)`；因此 raw cube里可能出现的
`m(1 tensor X)=X` 不在 order-0 constant edge上制造 `nu=1 -> 0` 泄漏。

结合上一节的 orbit factor，任意 cable state均有

\[
\boxed{\Lambda_{n+e_i}^{(3)}\psi_i^{[0]}=0},
\qquad
\boxed{\Lambda_{n+e_i}^{(3)}\psi_i^{[1]}=\Lambda_n^{(3)}}.
\]

## 5. alternative pair的独立数值

raw B88 exact cubic重算：

\[
u'=e_1-e_{86},qquad \ell'=e_{87}^*-e_0^*,
\]

\[
[\epsilon^3]\ell'K_3u'=14432,qquad
[h^3]=-8\cdot14432=-115456.
\]

orientation合法：`1/87` 为 positive，`86/0` 为 negative，cup与cap都连接 opposite orientations。

现有 fixed local P3 `(0,5,87)` 模型对这对的贡献为零；但 actual old-endpoint product collar尚未绑定，所以只能记

```text
P3 robustness: CONDITIONAL.
```

不能把它写成 actual sphere immunity。

## 6. full q-series边界

该构造证明的是 associated `h^3` family。stable braid之间的 pure remainder、projective normalization及 beta的正阶 action都可能从 `h^4` 起进入。因此：

```text
h3 leading beta/psi: PASS;
full q-series beta/psi: NOT PROVED.
```

证伪只需要当前最低非零系数在后续 quotient中有良定义；本节已闭 beta/psi leading，但没有替代 sphere maps。

## 7. 复算

```powershell
python -B D:\tmp\r6\fullw_tangent_coend\main\all_level_reynolds_foam_family.py
```

预期：

```text
VERIFY=PASS
STABLE_SHUFFLE_COMMON_TARGET=PASS_AT_H3
ALL_K_BETA=PASS; PSI0=0; PSI1=IDENTITY
CURRENT_H3=-59072; ALTERNATIVE_H3=-115456
FULL_Q_SERIES=NOT_PROVED; SPHERE=NOT_INCLUDED
```
