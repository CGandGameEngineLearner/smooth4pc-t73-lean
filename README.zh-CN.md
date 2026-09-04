# Smooth4PC T73 — 条件 skein-lasagna 阻碍

[English](README.md)

本仓库支持对 trace-73 Cappell--Shaneson **同伦** \(4\)-球面
\[
A=\begin{pmatrix}0&269&1240\\0&41&189\\1&0&32\end{pmatrix}
\]
（Iwaki 标准形 \(X_{41,189,73}\)）的一份**条件性** skein-lasagna 阻碍论证。

**不断言光滑四维 Poincaré 猜想的反例。** 控制性文稿为
[`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
（中文对照：`main-zh.tex`；标题：《trace-73 Cappell--Shaneson 球面的条件
skein-lasagna 阻碍》）。

## 已证与开放

对显式 **Johnson 生成元** 柄表示，正文证明 skein-lasagna 在 quantum degree
\(494\) 处比较所需的几何输入 **P0、C、S、P3**，包括识别
\(X_J\cong\Sigma_A^0\)。

精确有限计算给出非零 divided cubic \(D_3=2624\)。Artin--Magnus 证书与
pure-braid Andreadakis 定理确立公开 braid 词的三阶性质。

Lean 开发将**抽象商论证**形式化：若给定将 MWW 商与四柄运输组装起来的接口数据
（`ExternalGeometry`），则非零次数-\(494\) 类**将**阻碍与 \(S^4\) 的微分同胚。
这些几何接口**未**在 Lean 中构造。

| 层次 | 状态 |
| --- | --- |
| 有限代数（\(2624\)、次数 \(494\)、\(\det A=\det(A-I)=1\)） | Lean 已检 |
| 抽象条件蕴含 | Lean 已检 |
| Johnson P0 / C / S / P3（正文几何 + 证书） | 正文已证 |
| Lean 中 `ExternalGeometry` 实例 | **开放** |

Lean 边界见
[`Smooth4PC/T73External.lean`](Smooth4PC/T73External.lean)。前提审计：

```text
python3 scripts/audit_t73_premises.py --check
```

预期摘要：`P0/C/S/P3=PASS`，`OVERALL=OPEN`，`COUNTEREXAMPLE=False`。

**勘误（2026 年 9 月 2 日）。** 较早草稿混用两套 endpoint 索引表，报告了
\(-59072\)。统一到 braid 词所用 collar 表后，精确值为 \(+2624\)（仍非零）。

## 审阅 PDF

- 英文：[`output/pdf/spc4-t73-candidate.pdf`](output/pdf/spc4-t73-candidate.pdf)
- 中文：[`output/pdf/spc4-t73-candidate-zh.pdf`](output/pdf/spc4-t73-candidate-zh.pdf)

文稿与编译说明：
[`paper/spc4-t73-candidate/README.md`](paper/spc4-t73-candidate/README.md)。

## 从哪里开始

1. 阅读论文摘要与第 3 节（精确陈述）：
   [`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
   或上方英文/中文 PDF。
2. 按 [`REPRODUCING.md`](REPRODUCING.md) 从全新 clone 编译、检查公理报告并重算检测量。
3. 按下方命令重放有限检测量与 Johnson P0/C/S/P3 证书（完整清单见 `REPRODUCING.md`）。
4. 复核边界图见
   [`docs/INDEPENDENT_REVIEW.md`](docs/INDEPENDENT_REVIEW.md)。

## 快速重放

在仓库根目录运行：

```text
# 当前 actual AR → C → S → 四柄链
python3 -B scripts/verify_t73_actual_chain.py

# 另重算耗时的 93 因子 PL 映射与汇总 P0
python3 -B scripts/verify_t73_actual_chain.py --full
```

末尾应为：

```text
T73_ACTUAL_CHAIN=PASS
T73_FORMAL_STATUS=CONDITIONAL_EXTERNAL_GEOMETRY
```

第一行覆盖数学证书链；第二行记录唯一形式化边界：不会把 JSON 布尔值伪装成
Lean 的 `ExternalGeometry` 或 `CSTopologyData` 居民。

## 分步重算 / 重放

在仓库根目录使用 **Python 3.10+**。Windows 上可用 `python` 代替 `python3`。
每个 `--check` 会在内存中再生证书，并与 `audit/` 下已提交的 JSON 比对。

### 有限检测量（\(D_3=2624\)）

```text
python -I -B scripts/recompute_t73_delta3.py --check
```

预期：`DELTA3_ETA_T1=2624`、`DELTA3_XI=0`、`VERIFY=PASS`。

### Johnson P0 → C → S → P3/E13

```text
# P0（约 1–2 分钟）：AR 桥、消去、几何辫
python -B scripts/certify_t73_p0_johnson.py --check

# 实际 AR link 与两次 Kirby 消去
python -B scripts/verify_t73_actual_ar_link.py --check
python -B scripts/verify_t73_handle_cancellation.py --check
python -B scripts/verify_t73_actual_cut_tangle.py --check

# C：全部实际矩形/圆、比较支撑、汇总 witness
python -B scripts/verify_t73_actual_product_rectangles.py --check
python -B scripts/verify_t73_actual_leftover_z_circles.py --check
python -B scripts/verify_t73_actual_geometric_braid.py --check
python -B scripts/verify_t73_endpoint_transport.py --check
python -B scripts/certify_t73_c1_cut_link.py --check
python -B scripts/certify_t73_c2_comparison.py --check
python -B scripts/verify_t73_product_ribbon_isotopy.py --check
python -B scripts/generate_t73_c_comparison_witness.py --check

# S：实际 H1 盘迹、Kirby 曲面运输、球面与半球映射
python -B scripts/verify_t73_johnson_dual_disk_movie.py --check
python -B scripts/verify_t73_three_handle_surface_transport.py --check
python -B scripts/verify_t73_actual_sphere_system.py --check
python -B scripts/verify_t73_hemisphere_movies.py --check
python -B scripts/certify_t73_s_relative_moves.py --check

# P3：四柄图景、标准 S^4 次数 494、CS 识别
python -B scripts/certify_t73_p3_four_handle.py --check
python -B scripts/certify_t73_e12_s4.py --check
python -B scripts/certify_t73_e13_close.py --check
python -B scripts/certify_t73_e13_identification.py --check

# 前提汇总（须保持 OVERALL=OPEN / 非反例）
python -B scripts/audit_t73_premises.py --check
python -B scripts/check_t73_claim_boundary.py
```

| 脚本 | 作用 | 预期 |
| --- | --- | --- |
| `certify_t73_p0_johnson.py` | P0 Johnson 替换 | `T73_P0_JOHNSON_CERTIFICATE=PASS` |
| `verify_t73_actual_ar_link.py` | 七分量带 framing AR link | `ACTUAL_AR_LINK=PASS` |
| `verify_t73_handle_cancellation.py` | 两次实际 Kirby 消去 | `T_HCS=PASS`，`X_M1=PASS` |
| `verify_t73_actual_cut_tangle.py` | 消去后 detector | `PASSAGES=44`，`LEFTOVER_Z_CIRCLES=227` |
| `verify_t73_actual_product_rectangles.py` | 全部实际 y/z 矩形 | `RECTANGLES=44` |
| `verify_t73_actual_leftover_z_circles.py` | 全部 source-bound 剩余圆 | `CIRCLES=227` |
| `certify_t73_c1_cut_link.py` | 44 条带 + 227 剩余 \(z\) | `RECTANGLES=44`，`LEFTOVER_Z_CIRCLES=227` |
| `certify_t73_c2_comparison.py` | C2 支撑不相交 / \(H\) movies | `T73_C2_COMPARISON=PASS` |
| `generate_t73_c_comparison_witness.py` | C 账本绑定 P0/C1/C2 | `C_STATUS=PASS` |
| `verify_t73_johnson_dual_disk_movie.py` | 93 因子 H1 盘运输 | `GEOMETRIC_CORE_COUNTS=[12578,1824,409]` |
| `verify_t73_three_handle_surface_transport.py` | 盘迹穿过全部 Kirby band | `ACTUAL_THREE_HANDLE_SURFACE_TRANSPORT=PASS` |
| `verify_t73_actual_sphere_system.py` | 实际 partial-W2 球面系 | `ACTUAL_SPHERE_SYSTEM=PASS` |
| `verify_t73_hemisphere_movies.py` | 实际 MWW 三柄映射 | `ACTUAL_W2_LASAGNA_MAP=True` |
| `certify_t73_p3_four_handle.py` | \(X_J\) 四柄层 | `E11`/`E12` PASS；`E13=PARTIAL` 属设计 |
| `certify_t73_e12_s4.py` | 标准 \(S^4\) 上空链次数 \(494\) | `S4_DEGREE_494_ZERO=True` |
| `certify_t73_e13_*.py` | \(X_J\cong\Sigma_A^0\) 管道 | `IDENTIFIED_WITH_SIGMA=True` |
| `audit_t73_premises.py` | 汇总状态 | `P0/C/S/P3=PASS`，`COUNTEREXAMPLE=False` |
| `check_t73_claim_boundary.py` | 论文/Lean 声称边界 | `T73_CLAIM_BOUNDARY=CONDITIONAL_LEAN_PACKAGING` |

**说明。**

- 证书经 SHA 链式绑定：C 绑定 P0，S 绑定 P0+C，P3 绑定 P0+C+S。改上游而不再生下游会导致 `--check` 失败。
- `certify_t73_p3_four_handle.py` 报 `E13=PARTIAL` 是预期行为；完整 \(\Sigma_A^0\) 识别在 `e13_*` 脚本中。
- 旧的 word-only `band_slides` / `derived_crossings` 路线已删除；当前检查从实际带 framing AR link 与 source-bound 弧开始。
- Lean 编译（`tests/test_t73_minimal_formalization.py`）另计，较慢（约 5–10 分钟）；见 [`REPRODUCING.md`](REPRODUCING.md)。

## 复现约定

- Lean 工具链：`leanprover/lean4:v4.32.1`
- mathlib 修订：`520045ab14e26149ee970e2e617ca04b09bde5d6`
- Python：3.10 或更高
- Lean 公理报告由 focused formalization tests 检查，不在 README 手工维护数量。
- 允许公理：`propext`、`Classical.choice`、`Quot.sound`
- `sorryAx`：无
- 预期检测量：`2624`

已提交的 `lake-manifest.json` 锁定 Lean 依赖。构建产物与本地依赖副本不在源码约定内。

## 范围

这是面向**条件性**阻碍的公开核验包，不是同行接受声明，也不是已证反例。
最有用的否定性审阅应针对 Johnson 几何绑定与尚未组装的 Lean
`ExternalGeometry`，而非已检整算术。

## 为何先在 GitHub 公开

GitHub 作为首个公开渠道，便于获取、速度与复现，不能替代学术审阅。既有
arXiv 投稿史在计算机科学方向；数学类目背书可能暂不具备。完整论证、Lean
源码、证书与重放说明均可在此检查。经实质审阅后，计划提交常规预印本。

## 许可证

本仓库以 [MIT License](LICENSE) 发布。
