# THXY full macro chosen successor：终裁

日期：2026-08-31（Asia/Tokyo）  
cert SHA：`EABF67C0D1AE309F0281297710A283B8ED5A11D88C8E810837932313F4C53227`  
script SHA：`AD2C722BF44BFD69E00B27F1B3537910FF3EAA6FDAB8985ED1C13B00E8C6F362`

## 判词

```text
313/313 outer leaves consume actual owner/corridor subarcs: PASS
313 owner connectors PL self-check:                      PASS; actual embedding NOT CERTIFIED
312 macro bands full PL/new-new/hash chained:            PASS
10802 corridor split events actual embedded source:      PASS by pinned corridor theorem
12247 root bigons + final cap consume macro root:         PASS
Euler characteristic / genus-zero combinatorics:        PASS; actual sphere NOT CERTIFIED

constant H0 new-only map / I2:                           PASS
closed-cap scalar pair at h3:                            0 / 0, PASS
P3-free semantic whitelist:                              NOT NEEDED FOR h3

chosen class determinant:                                PASS; simultaneous actual HJ basis NOT CERTIFIED
```

## 1. identity与测试

工作树曾短暂出现tests先于script的竞态；最终identity已重建，7 tests全PASS。
full cert现在含 `full_surface`，不是旧的312-band截断件。

相对退休的BFC/9B0 identity，最新EABF/AD2只增强corridor provenance：逐条
读取PRODUCT的5401 positive与5401 negative typed bands，核band ID、反向
source/target state、relator copy、private slab、pants status与normal0；macro、
root、Euler、map及scalar字段未回退。

## 2. actual leaves与connectors

前两枚m2 leaves绑定`FRAMED_RYZ` stable whisker actual subarcs；其余311枚从
PRODUCT `other_311_actual_owner_cables`逐项读actual carrier segment、copy/lane、
orientation与framing。每个connector消费source hash并输出对应macro leaf hash。

honest routes逐条self-free。旧字段把未缩放的 `53360` 当成 scaled12 上界；
正确值是 `640704`，因此 `all_macro_routes_outside_old_projection_box=false`。
本件不再声称这些routes整体位于old projection box之外。独立重算313 connectors之间有30932枚projection
hits，但313枚private D2 lanes全唯一；这些是不同radial sheets的投影交叉，不是
3D intersections。connector是invertible mixed transport；即使绕old factor，
WEAK_ALL_EDGE theorem给constant `H=I`、positive part `O(h)`，不影响h3。

因此不需要逐crossing证明“完全不看old strands”；private lanes+material labels+
weak constant-edge theorem正是足够射程。

## 3. 312 macro bands

每band消费previous output与一枚actual-bound leaf，所有noninvertible feet均
`NEW_NEW`。独立重算312对left/right routes：

```text
bands with mutual projection crossings = 0.
```

所以旧敌审的“coincident legs mutation可逃”是validator天花板，不是当前诚实
geometry反例；actual coordinates自身无交。distinct parent slabs给inter-band
disjointness，最后output hash逐band传到root。

P3 marker mutation不再承重：任意mixed pure holonomy在fixed-weight constant
endpoint qHH为I，正阶只从h4改变incoming h3 row。终审不要求full holonomy
为零。

## 4. corridor parent rows不是空IDs

10802 corridor events的单行payload主要是IDs/hashes/slabs，但最新identity
又逐条反绑PRODUCT typed handle-slide bands；它们绑定的
`CHRISTOFFEL_CORRIDOR_5401_RECURSIVE_CERT` 已给：

- 5401 forward + 5401 true-inverse full-word equalities；
- distinct actual product-cable D2 points；
- 10802 disjoint macro slabs与10800 exact gap annuli；
- framed owner copies、terminal geometric bigon；
- old-U1 intersections 0。

所以parent rows是对一个已证universal coordinate construction的逐event
commitments，不是仅有名字。new full macro补上它此前唯一缺的313-face outer
attachment。

## 5. root bigons/cap

full cert把312nd macro output geometry hash直接交给root cap。12247 reverse
bigons继承parent LIFO/nested-disjoint ledger，post-reduction word为空；final cap
disk在outer THXY collar，normal0，与old U1及bigons相交数0。

Euler ledger：

\[
11115\text{ core disks}-11114\text{ split bands}+1\text{ root cap}=2,
\]

故closed genus0 sphere。root cap mutation由第7项测试拒。

## 6. surface-to-map与scalar

全部11114 noninvertible events是standard oriented new-only split pants；old
detector factor仅经identity cylinders与invertible mixed transports。WEAK theorem
因此给constant map

\[
Id_{old}\otimes T_{new}.
\]

new tree的undotted column为exactly-one-1，dotted column为all-X；actual W2
core counits给 `E(U)=0,E(D)=1`。incoming detector从h3开始，所有pure transport
正阶只进h4。故

```text
C872 Sigma_THXY(0) U05 = 0;
C872 (Sigma_THXY(1)-Id) U05 = 0
```

在h3 associated graded为actual chosen-sphere结果。

## 7. global HJ gate

现有三腿：

```text
THXY sector [2,13/2];
TH1  sector [8,9];
TH2  sector [10,11].
```

class matrix determinant为1；但在old projection box字段纠正后，三张曲面的
actual embedded/disjoint绑定不再由本件认证，须作为候选特有前件另审。当前路线
`L=empty`，无需历史K/CUT-relative equivalence。HJ v3 Theorem5.3遂允许这套
NEW CHOSEN basis替代历史三柄system。三张map都绑定各自同一chosen surface。

因此本件只保留组合结构与 determinant 的 PASS；THXY actual embedding、三张曲面
simultaneous HJ basis 与对应 sphere-map 绑定均维持 NOT CERTIFIED。不认领历史movie，
也不声称full-q series。
