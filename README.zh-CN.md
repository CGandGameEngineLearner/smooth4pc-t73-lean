# Smooth4PC T73 — trace-73 skein-lasagna 阻碍

[English](README.md)

本仓库支持对 trace-73 Cappell--Shaneson **同伦** \(4\)-球面
\[
A=\begin{pmatrix}0&269&1240\\0&41&189\\1&0&32\end{pmatrix}
\]
（Iwaki 标准形 \(X_{41,189,73}\)）的一份论文层面 skein-lasagna 阻碍论证。

**当前论文只给出条件式阻碍，不宣称得到光滑四维 Poincaré 猜想的反例。**
控制性文稿为
[`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
（中文对照：`main-zh.tex`；标题：《trace-73 Cappell--Shaneson 球面的
skein-lasagna 阻碍》）。

## 已证与开放

对显式 **Johnson 生成元** 柄表示，正文在纸面层面给出 **P0/E13** 与上柄
运输。新的完整系数构造器在源端与目标端各保存 \(1260\) 个端点和 \(630\)
条带框弧，但两张匹配表相差八条 wrong-side connector，因此先前的 literal
two-representable split 已被否定。其 \(223\) 只是反事实目标的分次账本；历史
值 \(494\) 与 \(223\) 都不是当前已构造的实际 MWW 类次数。**C 与 S 仍开放。**

精确有限计算给出非零端点模型标量 \(2624\)。把它识别为实际 MWW divided
cubic 仍属于 C 假设。Artin--Magnus 证书与
pure-braid Andreadakis 定理确立公开 braid 词的三阶性质。

Lean 开发将**抽象商论证**形式化：若给定将 MWW 商与四柄运输组装起来的接口数据
（`ExternalGeometry`），则任意非零量子次数中的非零类**将**阻碍与 \(S^4\)
的微分同胚。
这些几何接口**未**在 Lean 中构造。

| 层次 | 状态 |
| --- | --- |
| 有限代数（端点标量 \(2624\)、历史次数 \(494\)、\(\det A=\det(A-I)=1\)） | Lean 已检；实际 MWW 次数未构造 |
| 抽象条件蕴含 | Lean 已检 |
| Johnson P0 / E13 / 拓扑 P3 | 纸面层面已给出 |
| C / S 系数与三柄比较 | **开放** |
| Lean 中 `ExternalGeometry` 实例 | **开放** |

Lean 边界见
[`Smooth4PC/T73External.lean`](Smooth4PC/T73External.lean)。前提审计：

```text
python3 scripts/audit_t73_premises.py --check
```

旧聚合脚本仍会打印历史 `PASS` 与 `COUNTEREXAMPLE=True`，这些状态不是当前
完成判据。应以 `audit/RUNNING_PAPER_AUDIT.md`、完整几何 bundle 及新的
fail-closed gates 为准。

完整 selected-C 几何 bundle 的重建命令为：

```text
python3 scripts/build_t73_complete_geometry_bundle.py --write
python3 scripts/build_t73_complete_geometry_bundle.py --check
python3 scripts/build_t73_complete_geometry_bundle_v2.py --check
```

它保存当前可重构的全部端点与弧几何；实际 coend/currying map 未构造，所以
顶层 manifest 按设计保持 `OPEN`。

### 实际 AR→Kirby 构造数据

[`geometry/t73_actual_ar_kirby_construction_request.json`](geometry/t73_actual_ar_kirby_construction_request.json)
由实际 AR coordinate atlas 经
[`scripts/build_t73_actual_ar_kirby_construction_request.py`](scripts/build_t73_actual_ar_kirby_construction_request.py)
生成。它是带 SHA 绑定、状态为 `OPEN` 的构造请求，不是 Kirby witness：保存三条
缺失 chart transition、6 条 t-band 与 1513 条 x-band 所需的两条边/splice 数据，及
七个最终 component。重建命令为：

```text
python3 scripts/build_t73_actual_ar_kirby_construction_request.py --check
```

未来 witness 由 `scripts/verify_t73_ar_to_kirby_presentation.py` 验收；它只接受
显式 cut-and-surgery 几何和精确的 AR/t/x source SHA 绑定。

[`geometry/t73_actual_cancellation_splice_request.json`](geometry/t73_actual_cancellation_splice_request.json)
是下一层生成输入：列出全部 6 条 t-band 和 1513 条 x-band 的 center-path hash，及
每条所缺的 boundary/splice 字段：

```text
python3 scripts/build_t73_actual_cancellation_splice_request.py --check
```

仅供软件探索的、明确非实际的候选输入为
[`geometry/t73_candidate_kirby_presentation.json`](geometry/t73_candidate_kirby_presentation.json)，
其 PD/framing 导出为
[`geometry/t73_candidate_kirby_export.json`](geometry/t73_candidate_kirby_export.json)。
其 SnapPy/Spherogram/Regina 收据为
[`geometry/t73_candidate_kirby_open_source_receipt.json`](geometry/t73_candidate_kirby_open_source_receipt.json)
（7 components、7 crossings、7 cusps、36 tetrahedra）。
使用 `python3 scripts/build_t73_candidate_kirby_presentation.py --write`，再运行
`scripts/export_t73_full_handle_diagram.py` 重建。其状态是
`CANDIDATE_UNVERIFIED`；绝不能用于闭合 P0、C、S 或 P3/E13。
全部 6 条 t-band 与 1513 条 x-band 的候选统一坐标 lift 保存于
[`geometry/t73_candidate_band_chart_normalization.json`](geometry/t73_candidate_band_chart_normalization.json)，
使用 `python3 scripts/build_t73_candidate_band_chart_normalization.py --check` 重建。
其 3035 个有理 PL rectangle 分段、边界和 push-off 保存于
[`geometry/t73_candidate_band_rectangles.json`](geometry/t73_candidate_band_rectangles.json)，
使用 `python3 scripts/build_t73_candidate_band_rectangles.py --check` 重建。

### Gmsh frame 与分块 frame 输入

已独立验收的 Gmsh prefix-20 frame 位于
[`geometry/examples/t73_selected_source_gmsh_prefix20_frame.json`](geometry/examples/t73_selected_source_gmsh_prefix20_frame.json)，
收据位于
[`audit/t73_selected_source_gmsh_prefix20_frame_verification.json`](audit/t73_selected_source_gmsh_prefix20_frame_verification.json)。
它有 4134 个顶点、23725 个四面体、20 条 arcs/ribbons、5 个边界分量及精确外部体积
63968；其唯一有效状态是 `PASS_PREFIX_ONLY`，不是完整 T73 几何。

分块路线已保存三个精确输入：

- [`geometry/t73_selected_source_partition_z0.json`](geometry/t73_selected_source_partition_z0.json)：在 `z=0` 裁切的全部 ruled-ribbon、core、push-off 与 connector fragments；
- [`geometry/t73_z0_interface_triangulation.json`](geometry/t73_z0_interface_triangulation.json)：带四个 insertion-hole loops 的共同 36 顶点/42 三角形接口；
- [`scripts/probe_t73_z0_block_volumes_gmsh.py`](scripts/probe_t73_z0_block_volumes_gmsh.py)：fail-closed 的 Gmsh OCC probe。其 `PASS_FRAGMENT_BATCH_ONLY` 只覆盖指定的 lower-side fragment batch，绝不表示完整 frame。

WSL 拓扑运行请使用独立环境（Gmsh wheel 还需要下列系统运行时库）：

```text
python3 -m venv ~/.venvs/t73-topology
~/.venvs/t73-topology/bin/python -m pip install 'regina>=7.4' 'gmsh==4.15.2'
sudo apt-get install libglu1-mesa libxft2
~/.venvs/t73-topology/bin/python scripts/probe_t73_z0_block_volumes_gmsh.py --fragments 10
```

下列日常精确检查不会重新运行完整 mesh：

```text
python3 scripts/build_t73_selected_source_partition_z0.py --check
python3 scripts/build_t73_z0_interface_triangulation.py --check
python3 scripts/build_t73_gmsh_frame_verification_receipt.py --check-files
python3 scripts/build_t73_gmsh_frame_verification_receipt.py --check-files --frame geometry/examples/t73_selected_source_gmsh_prefix20_frame.json --output audit/t73_selected_source_gmsh_prefix20_frame_verification.json --expected-prefix 20 --expected-vertices 4134 --expected-tetrahedra 23725 --expected-arcs 20 --expected-ribbons 20 --expected-boundary-components 5 --expected-exact-volume 63968
```

单体 630-ribbon HXT 尝试已被 OOM killer 终止且未写出 mesh。上述分块输入和 probe
仅作为构造数据保留；共同 630-ribbon tetrahedral frame gate 仍为 `OPEN`。

**勘误（2026 年 9 月 2 日）。** 较早草稿混用两套 endpoint 索引表，报告了
\(-59072\)。统一到 braid 词所用 collar 表后，精确值为 \(+2624\)（仍非零）。

## 审阅 PDF

- 英文：[`output/pdf/spc4-t73-candidate.pdf`](output/pdf/spc4-t73-candidate.pdf)
- 中文：[`output/pdf/spc4-t73-candidate-zh.pdf`](output/pdf/spc4-t73-candidate-zh.pdf)

文稿与编译说明：
[`paper/spc4-t73-candidate/README.md`](paper/spc4-t73-candidate/README.md)。

默认论文构建会把英文 PDF 保存到仓库输出目录（Windows 路径
`C:\Users\Administrator\Documents\ChatGPT\smooth4pc-t73-lean\output\pdf`）：

```text
bash scripts/build_papers.sh          # 默认：英文
bash scripts/build_papers.sh --zh     # 仅中文
bash scripts/build_papers.sh --all    # 两者
```

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

# 前提汇总（数学 PASS；解析 Lean 装配仍开放）
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
| `audit_t73_premises.py` | 汇总状态 | `PASS_MATHEMATICAL_LEAN_PARTIAL`，`COUNTEREXAMPLE=True` |
| `check_t73_claim_boundary.py` | 论文/Lean 声称边界 | `T73_CLAIM_BOUNDARY=UNCONDITIONAL_PAPER_LEAN_PARTIAL` |

**说明。**

- 证书经 SHA 链式绑定：C 绑定 P0，S 绑定 P0+C，P3 绑定 P0+C+S。改上游而不再生下游会导致 `--check` 失败。
- `certify_t73_p3_four_handle.py` 报 `E13=PARTIAL` 是预期行为；完整 \(\Sigma_A^0\) 识别在 `e13_*` 脚本中。
- 旧的 word-only `band_slides` / `derived_crossings` 路线已删除；当前检查从实际带 framing AR link 与 source-bound 弧开始。
- Lean 编译（`tests/test_t73_minimal_formalization.py`）另计，较慢（约 5–10 分钟）；见 [`REPRODUCING.md`](REPRODUCING.md)。

### Focused 测试与 Lean 编译

```text
python3 -m unittest \
  tests.test_t73_actual_cut_tangle \
  tests.test_t73_actual_product_rectangles \
  tests.test_t73_actual_leftover_z_circles \
  tests.test_t73_actual_geometric_braid \
  tests.test_t73_endpoint_transport \
  tests.test_t73_johnson_dual_disk_movie \
  tests.test_t73_three_handle_surface_transport \
  tests.test_t73_actual_three_handle \
  tests.test_t73_e13_close tests.test_t73_e13_identification

python3 scripts/generate_t73_lean_geometry.py --check
python3 scripts/check_t73_external_geometry_boundary.py
lake env lean Smooth4PC/T73CertificateIndex.lean
lake env lean Smooth4PC/T73JohnsonTransvections.lean
lake env lean Smooth4PC/T73GeometryPack.lean
lake env lean Smooth4PC/T73Conditional.lean
```

本仓库的 `lake build` 没有默认 target，请使用上述显式模块命令。生成的 Lean
索引记录 actual artifact SHA 以及精确计数 `44`、`227`、`93`、
`[12578,1824,409]`、`6`、`1513`。
边界检查必须报告 `OPEN_MISSING_ANALYTIC_MWW_FOUNDATIONS`；只有真正形式化
MWW 模与映射后才能改为 PASS，不能由证书布尔值替代。

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

这是面向**无条件论文级反例定理**的公开核验包，不是同行接受或完整 Lean
形式化声明。最有用的否定性审阅应针对 Johnson 几何绑定、解析 MWW 比较与尚未组装的 Lean
`ExternalGeometry`，而非已检整算术。

## 为何先在 GitHub 公开

GitHub 作为首个公开渠道，便于获取、速度与复现，不能替代学术审阅。既有
arXiv 投稿史在计算机科学方向；数学类目背书可能暂不具备。完整论证、Lean
源码、证书与重放说明均可在此检查。经实质审阅后，计划提交常规预印本。

## 许可证

本仓库以 [MIT License](LICENSE) 发布。
