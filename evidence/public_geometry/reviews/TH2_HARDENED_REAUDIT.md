# hardened TH2 exhaustive receipt：终裁

日期：2026-08-31（Asia/Tokyo）  
receipt SHA-256：
`4D1B627C0343A1C464319704EAFADCA127902A2E4E90CF1C283004359B7ADC24`

## 判词

```text
all 229198 leaves/fingers and 229197 bands visited: PASS
independent route/self/mutual/old-link replay:       PASS
9 hostile mutations:                                9/9 PASS
material ancestry and root cap binding:              PASS

TH2 chosen surface embedded:                         PASS
TH2 constant new-only H0 minor I2:                   PASS
closed-cap scalar pair at h3:                        0 / 0, PASS

historical TH2 recovered:                            NO / not needed for chosen basis
full-q map:                                          NOT CLAIMED
joint HJ basis:                                      waits TH1/THXY
```

旧敌审的bow-tie逃逸已由hardened runner修掉；旧报告由本件覆盖。

## 1. independent geometry replay

新runner不再消费producer的空intersection字段。它从每一行的
`left_route_scaled12/right_route_scaled12` 重算self/mutual intersections，
并从pinned ERKMO component segments重算old-link projection crossings。

精确总账：

```text
band route self intersections:       0;
band mutual projection crossings:    1;
band old projection crossings:       0;
finger route self intersections:     0;
finger old projection crossings:     312,186,510.
```

### 312,186,510 为什么在3D不相交

每枚finger的forward、owner、inverse tracks共享projection route，但具有严格
不同的exact microheights

```text
forward=3/16, owner=8/16, inverse=13/16.
```

old diagram位于base layer；每一枚重算出的projection crossing都由统一height
inequality隔开。不同leaves又位于互不相交的flat-comb slabs，并使用injective
owner-D2 indices。因此大数是projection incidence，不是3D intersection。

runner同时钉actual conjugator length/word hash与route ledger，不能通过清空
旧status字段伪造。

### band mutual的唯一crossing

唯一left/right projection crossing对应microheights

```text
left=2/8, branch core=4/8, right=6/8.
```

crossing点处两legs高度严格分开；它们只在指定branch core处由pair-of-pants
连接。equal-height mutation被拒。

## 2. mutations

九项测试包括：middle ancestry break、hidden slab overlap、missing full row、
dual output mismatch、band bow-tie with forged empty sweep、equal-height mutual
crossing、finger bow-tie与finger forward/inverse collision。全部拒绝。

root cap继续逐项绑定last SLP/cycle/terminal hashes；streamed 406,243,364-letter
word free-reduces为空，LIFO bigons给nested/disjoint radial cap。

## 3. embedded chosen TH2

每枚leaf绑定actual owner carrier subarc与global D2 index；finger、band、inter-band
product annuli和root cap现在形成一条完整geometry ancestry。严格slabs、height
orders与fresh D2 indices共同给pairwise embedded genus-zero surface。

runner虽动态启用all-row模式并选core output为canonical output，但这是NEW
CHOSEN geometry的定义，不再冒充historical recovery。其数学对象已完整消费，
所以不构成剩余阻断。

## 4. H0 I2 与 scalar `0/0`

TH2 surface的所有noninvertible critical points属于new-only product tree；old
detector block由identity cylinders承载。finger/standardization的mixed motion在
constant endpoint qHH中只是labelled pure braid，作用为Id；positive order只从
h4影响h3 witness。

new-only Frobenius columns因此是

```text
undotted U = exactly-one-1;
dotted D   = all-X.
```

dual all-X row给I2 minor，并在closed detector上给

```text
C Sigma_TH2(0) U = 0;
C (Sigma_TH2(1)-Id) U = 0
```

于h3 associated graded。这里用的是actual chosen TH2，不是historical scalar
恢复，也不声称full-q series。

## 5. 剩余边界

要启用NEW CHOSEN HJ basis，还需TH1与THXY各自同等级embedded receipt、三球
simultaneous disjointness及surface-to-map binding。TH2这一腿本身可记PASS。

