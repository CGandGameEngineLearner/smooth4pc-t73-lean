# q=494 与三柄球面关系的分次核验

日期：2026-08-31（Asia/Tokyo）

## 二值判词

```text
Q494_ISOLATED_FROM_ALL_SPHERE_RELATIONS: NO
GRADING_ALONE_PROVES_SURVIVAL:           NO
```

`q=494` 的绝对 MWW 分次本身是对的，但它没有把该类从三柄关系中隔离出来。
对 `N=2`，每一张三柄球面的两列归一化次数都是

```text
Sigma_j(0 dots): -2
Sigma_j(1 dot):   0
```

所以至少存在一条无需任何额外支撑假设的通道：

```text
eta_R[T1] in source q=494
    -- Sigma_j(1 dot), degree 0 -->
target q=494.
```

MWW 的三柄商正是对每个 `v`、每个 `j` 加入

```text
Sigma_j(0 dots)(v) = 0,
Sigma_j(1 dot)(v) = v.
```

第二条是商中的关系，不是商前已经成立的恒等式。若实际
`Sigma_j(1 dot)` 在该向量上为零，关系会直接杀掉 `v`；若非零，也仍需知道
实际 map 才能判断整组关系是否保留它。因此分次不能替代缺失的 map-level
两列。

## 1. 三种分次不可混用

当前输入是

```text
v = eta_R[T1],
T1 = F_Omega^-1 W^-1 U1.
```

现有逐项账给出：

| 层 | q-degree |
|---|---:|
| raw closure | `-44 + 227 = 183` |
| 加 one-handle shift `44+271` | `498` |
| 加 two-handle cabled summand shift `-4` | **`494`** |

这里的 `494` 是最终 cabled module 的绝对 quantum grading，不是内部
Frobenius 标签次数，也不是形式变形参数 `q=1+h` 的幂次。

## 2. 球面列的最终 cabled 次数

对一张具有 `F` 个边界叶的连通 genus-zero 球面截面，

```text
chi = 2-F,
raw degree with n dots = F-2+2n,
cabled source-to-target shift difference = -F.
```

故归一化总次数恒为

```text
deg Sigma_j(n dots) = 2n-2.
```

这与叶数无关，因而对 TH1、TH2、THXY 三张球都给出同一张表：

| sphere | column | normalized degree | 要落到 target q=494 所需 source q |
|---|---|---:|---:|
| TH1 | `Sigma_0` | `-2` | `496` |
| TH1 | `Sigma_1` | `0` | `494` |
| TH2 | `Sigma_0` | `-2` | `496` |
| TH2 | `Sigma_1` | `0` | `494` |
| THXY | `Sigma_0` | `-2` | `496` |
| THXY | `Sigma_1` | `0` | `494` |

其中 `Sigma_1` 的 source `q=494` 已由当前类 `v` 明确提供。因此“没有任何
sphere source degree 能打到 q=494”的前件已经被直接推翻。

## 3. q=496 支撑的地位

`Sigma_0` 若要打到 target `q=494`，需要 source `q=496`。当前语料没有给出
三张实际 sphere source module 的完整 graded-support 清单，因此不能从现有材料
证明 `q=496` 支撑为空。

相反，语料里有一个 **conditional Hattori-form** 的 `q=496` 候选：原 all-X
类加一个合法 owner dot 后，one-handle degree `500`，再加 outer `-4` 得
`496`。但其 coproduct movie / actual class 尚未闭合，所以这里只能登记为
“存在条件候选”，不能登记为实际非零 source class。

这一未定项不影响二值判词：degree-zero 的 `Sigma_1` 已足以证明 q=494 并不
孤立。

## 4. S4 集中在 q=0 的正确射程

`Sz(S^4)` 集中在 `(0,0)` 的作用是：**若**一个非零 `q=494` 类已经穿过完整
三柄商，那么它立刻区分候选球与标准 `S^4`。它不能反过来证明三柄商前的
`q=494` 类不会被关系杀掉，因为三柄映射只是给出一个商，且关系本身在
`q=494` 内有 degree-zero 通道。

## 5. 证据

- MWW `kirby.tex:728-739`：完整 quotient 的两类三柄关系，对所有 `v,j` 成立。
- MWW `kirby.tex:421-425,482-488`：三柄映射为满射，kernel 为两 cap maps
  的差的像。
- `XI_FINAL_CABLED_Q_DEGREE_AUDIT.md`：当前类 final cabled degree `494`。
- `THXY_RELATIVE_CUBIC_SPHERE_ACTION_RESULT.md:40-49`：raw/shifted 公式，
  `Sigma_0=-2`、`Sigma_1=0`。
- `GENERIC_PRODUCT_NORMAL_H0_FORMAL_RESULT.md:46-59`：同一公式对任意叶数 `F`
  保持不变。
- `THREE_STEP_MAINLINE_HOSTILE_AUDIT.md:144-164`：独立先前审计已指出同一
  q=496/q=494 通道。
- `PSI1_SUCCESSOR_RESULT.md:58-73`：仅作 `q=496` 条件候选的出处。

## 6. 文件 SHA-256

```text
55DDAD567FAE2C321B26DD21BA8F45C1B62EECF57DAF52B6F24EA76B3D3056C1  mww_handle_src/kirby.tex
4A1266F66E3627229C477D433D9D85734E0E96ADBCC70AE5C5EAB4B4FFA0E8CE  XI_FINAL_CABLED_Q_DEGREE_AUDIT.md
447B6954FA3ED4FCCA6183CF143DB5EAFE64C1EC18D64EF0708AA33C6BDC2267  THXY_RELATIVE_CUBIC_SPHERE_ACTION_RESULT.md
109B83736BB844D39F715095ED739111C82A8BE688CE070578C3CAC80BE68595  THREE_STEP_MAINLINE_HOSTILE_AUDIT.md
0D720A4247EB3DF6880B92E79232EBEF01E10E78F8D735A2F802150A3EE7A5E4  PSI1_SUCCESSOR_RESULT.md
```

## 对证伪主线的作用

第一条“仅凭分次自动存活”的捷径关闭。`-59072` 与 `q=494` 的算术没有被
推翻；被推翻的是“球面关系碰不到它”。下一步若仍走该链，必须控制实际
`Sigma_0/Sigma_1` 在 q=494 邻域的作用（或构造等价的真实 cocone/消像
泛函），不能只用最终分次。
