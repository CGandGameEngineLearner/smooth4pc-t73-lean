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

精确拓扑 verifier 使用 NumPy、SciPy、SymPy 与 Shapely。WSL 中先运行
`python3 -m venv /home/lifesize/.cache/t73-topology-venv`，再运行
`/home/lifesize/.cache/t73-topology-venv/bin/pip install -r requirements-topology.txt`。

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

数字化所需 PL cells 的可引用文献索引为
[`geometry/t73_literature_geometry_ledger.json`](geometry/t73_literature_geometry_ledger.json)，
使用 `python3 scripts/build_t73_literature_geometry_ledger.py --check` 重建。
它保存原文页码/Figure 以及各来源能和不能提供的数据。

[`geometry/t73_unified_kirby_foot_chart.json`](geometry/t73_unified_kirby_foot_chart.json)
将四个 AR Figure 2a foot pair 与已验证的 T73 passage 数据组合。t/x 历史绑定
其 belt sphere 与实际 cancellation；最终 y/z state 分别含 235 与 1550 个反射
配对 passage。使用 `python3 scripts/build_t73_unified_kirby_foot_chart.py --check`
重建，并用 `python3 scripts/verify_t73_unified_kirby_foot_chart.py` 验收。最终
passage 数据位于
[`geometry/t73_final_yz_foot_state.json`](geometry/t73_final_yz_foot_state.json)，
Johnson-only 基础绑定位于
[`geometry/t73_yz_foot_lane_binding.json`](geometry/t73_yz_foot_lane_binding.json)。
五条 cyclic order 保存于
[`geometry/t73_final_component_passage_cycles.json`](geometry/t73_final_component_passage_cycles.json)：
长度为 `311,1462,4,4,4`；在显式自由约化 isotopy 前保留两条 bottom coordinate
passage。
第一份 common-R3 routing 以 fail-closed 状态保存于
[`geometry/t73_actual_kirby_core_embedding.json`](geometry/t73_actual_kirby_core_embedding.json)，
状态为 `SOURCE_BOUND_KIRBY_CORE_CANDIDATE_STRUCTURAL_CHECK_ONLY`。紧凑
push/projection manifest 位于
[`geometry/t73_actual_kirby_framed_input.json`](geometry/t73_actual_kirby_framed_input.json)。
使用 `build_t73_actual_kirby_framed_input.py --materialize PATH` 在仓库外展开。
`export_t73_full_handle_diagram.py` 已使用 Shapely STRtree 流式 broad phase，但
实际 PD/framing export 尚未通过。

另一个独立层次中，C-cut 的 44-lane candidate realization 为
[`geometry/t73_y_foot_lane_candidate.json`](geometry/t73_y_foot_lane_candidate.json)：
44 条实际 y-cut passage 被绑定到互异的有理 y-foot target 与 product-normal framing rectangle。
重建/检查命令：

```text
python3 scripts/build_t73_y_foot_lane_candidate.py --check
python3 scripts/verify_t73_y_foot_lane_candidate.py
```

其 verifier 只报告 `PASS_CANDIDATE_PL_DISJOINTNESS_ONLY`，不是实际 AR relative Kirby movie。

六步 t-cancellation candidate movie 位于
[`geometry/t73_candidate_t_band_movie.json`](geometry/t73_candidate_t_band_movie.json)，
使用 `python3 scripts/build_t73_candidate_t_band_movie.py --check` 重建。
它保存矩形段、attachment、splice descriptor和有序 candidate link state，但不声称实际 Kirby cancellation。
从 AR records 中真正可恢复的 6 组 source/target attachment endpoint 单独保存在
[`geometry/t73_t_band_attachment_locators.json`](geometry/t73_t_band_attachment_locators.json)，
使用 `python3 scripts/build_t73_t_band_attachment_locators.py --check` 重建。
其范围为 `VERIFIED_ENDPOINTS_ONLY`。
围绕这些 locator 的规范有理区间保存于
[`geometry/t73_t_band_attachment_intervals.json`](geometry/t73_t_band_attachment_intervals.json)，
使用 `python3 scripts/build_t73_t_band_attachment_intervals.py --check` 重建。
locator 已验证；基于 width 的区间选择仍为 candidate。
`python3 scripts/verify_t73_t_band_attachment_intervals.py` 独立证明六个 source
interval 都位于实际 lambda/mu core edge，所有 target interval 都位于其 parallel
h_CS line，并返回 `PASS_T_INTERVAL_ACTUAL_EDGE_BINDING_CANDIDATE_WIDTH`。
`verify_t73_t_band_parallel_hcs_targets.py` 证明六条 target line 是 actual
h_CS framed parallel，顺序系数为 `[-25,-15,-5,5,15,25]`，返回
`PASS_ACTUAL_HCS_PARALLEL_TARGET_BINDING`。
全部 6 条 t-band 的 boundary-compatible normal homotopy 保存于
[`geometry/t73_t_band_framing_extensions.json`](geometry/t73_t_band_framing_extensions.json)。
使用 `build_t73_t_band_framing_extensions.py --check` 重建，并用
`verify_t73_t_band_framing_extensions.py` 独立检查。内部插值仍为 candidate；
source 与 h_CS 边界 framing 是 actual-record binding。
位于实际八面体 t-belt collar 内的六张有理 PL 盘保存于
[`geometry/t73_t_band_collar_surfaces.json`](geometry/t73_t_band_collar_surfaces.json)。
使用 `python3 scripts/build_t73_t_band_collar_surfaces.py --check` 重建，并用
`python3 scripts/verify_t73_t_band_collar_surfaces.py` 独立检查。每张盘各自局部
嵌入，并精确绑定 source/target interval；六次 slide 是顺序 movie，而非同时发生。
完成 current-link-safe 有理绕行后，verifier 仍将 `(0,2)`、`(0,4)`、`(1,4)`、
`(2,4)` 的曲面交汇记录在不同时间层。返回值
`PASS_T_BAND_COLLAR_DISKS_SEQUENTIAL_CANDIDATE_FRAMING_ONLY` 尚不证明
current-link replay 或实际 Kirby 等价。
由该 collar 数据构造的第一条真实顺序状态转换保存于
[`geometry/t73_t_band_sequential_state_01.json`](geometry/t73_t_band_sequential_state_01.json)。
使用 `python3 scripts/build_t73_t_band0_sequential_state.py --check` 重建，并用
`python3 scripts/verify_t73_t_band0_sequential_state.py` 验证。后者独立重算每个
splice piece，并检查商空间嵌入、framed push-off、仅限两条 attachment 的接触、
与全部静止分量的分离，以及 inverse move 对细分后源 lift 的精确恢复。返回值为
`PASS_T_BAND0_SEQUENTIAL_FRAMED_KIRBY_SLIDE`；其范围仅是 state `0 -> 1`。
全部六次 slide 的紧凑、可重放 delta movie 保存于
[`geometry/t73_t_band_sequential_movie.json`](geometry/t73_t_band_sequential_movie.json)。
使用 `python3 scripts/build_t73_t_band_sequential_movie.py --check` 与
`python3 scripts/verify_t73_t_band_sequential_movie.py`。它在每个紧邻前态中唯一
重绑 source interval，处理 wrapped interval 的 deck lift、两种 seam 方向和历史
seam 传播；逐步检查 disk/新 framed curve 对当前 link 与 actual dual-core 空间投影
的分离，并验证每个 inverse。结果为
`PASS_SIX_T_BAND_SEQUENTIAL_FRAMED_KIRBY_SLIDES`。JSON 保存可重放 delta 与内容
SHA，避免重复数十 MB 的相同 normal vectors。
下一道取消门槛保存于
[`audit/t73_t_hcs_cancellation_readiness.json`](audit/t73_t_hcs_cancellation_readiness.json)。
原始 state-6 push-off 有 4 段进入 open t-ball；
[`geometry/t73_t_hcs_framing_exteriorization.json`](geometry/t73_t_hcs_framing_exteriorization.json)
保存 63 个规范 outward normal 替换。使用
`build_t73_t_hcs_framing_exteriorization.py --check`、
`verify_t73_t_hcs_framing_exteriorization.py` 与
`build_t73_t_hcs_cancellation_readiness.py --check` 重建/验收。精确 verdict 为
`PASS_STATE6_FRAMING_EXTERIORIZATION` 和
`READY_FOR_EXPLICIT_T_HCS_CANCELLATION_MAP`；仍须构造 cellwise cancellation map。
取消前的有限 collar map 保存于
[`geometry/t73_t_hcs_collar_ejection_map.json`](geometry/t73_t_hcs_collar_ejection_map.json)。
使用 `build_t73_t_hcs_collar_ejection_map.py --check` 与
`verify_t73_t_hcs_collar_ejection_map.py` 重建/验收。其 24 个保向四面体把内层
八面体从 `r` 推到 `3r/2`，同时固定 `2r` 外层；verdict 为
`PASS_T_HCS_COLLAR_EJECTION_CELL_MAP`。这只闭合 collar ejection，4 维
handle-pair 的下一层数据如下。
完成的标准 pair deletion 与 carried post-link manifest 位于
[`geometry/t73_t_hcs_handle_pair_deletion.json`](geometry/t73_t_hcs_handle_pair_deletion.json)。
先运行 `build_t73_t_hcs_handle_pair_deletion.py --check`，再用 topology venv
运行 `verify_t73_t_hcs_handle_pair_deletion.py`。它验证
`Delta1 x Delta3`、`Delta2 x Delta2` 的 staircase triangulation、三四面体
attaching 3-ball、所得 PL 4-ball/S3 边界、实际 belt 重心交点、AR framing，及
六分量 post-cancel manifest。verdict 为
`PASS_T_HCS_HANDLE_PAIR_DELETION_AND_POST_LINK_STATE`。
第一条 x-slide attachment 层保存于
[`geometry/t73_x_band0_attachment_surface.json`](geometry/t73_x_band0_attachment_surface.json)。
使用 `build_t73_x_band0_attachment_surface.py --check` 与
`verify_t73_x_band0_attachment_surface.py` 重建/验收。它将 `c1:letter:0`
绑定到 post-cancel m2 的 vertex range `[20,22]`、deck `[269,40,0]`，将 target
绑定到第 20 条 framed m1 parallel，并验证六顶点 PL 盘；边界 framing verdict 为
`PASS_X_BAND0_ACTUAL_ATTACHMENTS_AND_BOUNDARY_FRAMING`。
完整局部 obstacle state 位于
[`geometry/t73_x_positive_belt_state0.json`](geometry/t73_x_positive_belt_state0.json)：
包含一条 cancelling m1 arc、1509 条 Johnson arc 与 4 条 dual passage。运行
`build_t73_x_positive_belt_state0.py --check` 和
`verify_t73_x_band0_current_link_clearance.py`；24,232 次精确检查返回
`PASS_X_BAND0_CURRENT_LINK_AND_PUSH_CLEARANCE`。
两侧实际 affine chart germ 与 framing transport 保存于
[`geometry/t73_x_band0_chart_transitions.json`](geometry/t73_x_band0_chart_transitions.json)，
由 `verify_t73_x_band0_chart_transitions.py` 验收。
完整第 20 条 m1 parallel 位于
[`geometry/t73_x_band0_m1_parallel.json`](geometry/t73_x_band0_m1_parallel.json)，
由 `verify_t73_x_band0_m1_parallel.py` 验收。有向 band 使用不塌缩的 half-vector
旋转 `+e_x -> -e_nu -> -e_x`，使插入的 m1 passage 交数为 `-1`，与 source
的 `+1` 抵消。
所得 global/local 状态转换保存于
[`geometry/t73_x_band_hybrid_state_0000_0001.json`](geometry/t73_x_band_hybrid_state_0000_0001.json)。
使用 `build_t73_x_band0_hybrid_state.py --check` 与
`verify_t73_x_band0_hybrid_state.py` 重建/验收；verdict 为
`PASS_X_BAND0_HYBRID_FRAMED_STATE_0_TO_1`。
全部 1513 个 positive-belt 局部状态 delta 紧凑保存于
[`geometry/t73_x_band_local_movie.json`](geometry/t73_x_band_local_movie.json)，
使用 `python3 scripts/build_t73_x_band_local_movie.py --check` 重建。完整
current-segment replay 命令为 `python3 scripts/verify_t73_x_band_local_movie.py`；
设置 `T73_PROGRESS=1` 可显示进度。它验证含全部 source stub、band lane 与
m1-parallel stub 的 1514 个状态，返回
`PASS_ALL_1513_X_LOCAL_FRAMED_BAND_STATES`。首次完整运行绑定于
[`audit/t73_x_band_local_movie_verification.json`](audit/t73_x_band_local_movie_verification.json)。
日常测试运行 `python3 scripts/build_t73_x_band_local_movie_receipt.py --check`；
重建收据必须显式使用 `--write --full`。该收据只覆盖 local state 层；下述
component-level hybrid movie 覆盖全部 global splice。
每个 orientation-rotation 中点使用 outward movie height
`nu=1+(band_index+1)*width`，因此两个 cross-section 顶点始终位于 transverse
D3 边界上或外侧。该修正后已重新完整运行 1513-state verifier 并重签收据。
但全部 target parallel 现已全局化：单张 quotient annulus
[`geometry/t73_x_m1_parallel_foliation.json`](geometry/t73_x_m1_parallel_foliation.json)
包含 `20,40,...,30260` 全部层。使用
`build_t73_x_m1_parallel_foliation.py --check` 与
`verify_t73_x_m1_parallel_foliation.py` 重建/验收。后者返回
`PASS_ALL_1513_M1_PARALLELS_IN_EMBEDDED_QUOTIENT_ANNULUS`；4 个 mapping-torus
seam triangles 被正确视为 gluing cells，而非 affine triangle。
全部 source-side global chart germ 保存于
[`geometry/t73_x_source_chart_germs.json`](geometry/t73_x_source_chart_germs.json)。
使用 `build_t73_x_source_chart_germs.py --check` 与
`verify_t73_x_source_chart_germs.py` 重建/验收。它在实际分量中唯一定位 1509 条
Johnson top arc 与 4 条有向 dual-disk boundary arc，返回
`PASS_ALL_1513_X_SOURCE_CHART_GERMS`，且不假设 `nu=u`。
完整 component-level atlas movie 保存于
[`geometry/t73_x_band_hybrid_movie.json`](geometry/t73_x_band_hybrid_movie.json)。
使用 `build_t73_x_band_hybrid_movie.py --check` 与
`verify_t73_x_band_hybrid_movie.py` 重建/验收。它验证 1513 个 replacement
cell、6052 个 chart gluing、1513 个 inverse 与全部 component Merkle state，
返回 `PASS_ALL_1513_X_HYBRID_PIECE_WORD_STATES`。这里刻意使用 chart-typed
cell replacement，不引入虚假的全局坐标等同。
第二个 cancelling pair 现已显式化。core collar map
[`geometry/t73_x_m1_collar_ejection_map.json`](geometry/t73_x_m1_collar_ejection_map.json)
与 framing exteriorization
[`geometry/t73_x_m1_framing_exteriorization.json`](geometry/t73_x_m1_framing_exteriorization.json)
分别返回 `PASS_X_M1_CORE_COLLAR_EJECTION_MAP` 与
`PASS_X_FINAL_LINK_UNIFORM_OUTWARD_FRAMING`。标准 4-ball deletion 和五分量输出位于
[`geometry/t73_x_m1_handle_pair_deletion.json`](geometry/t73_x_m1_handle_pair_deletion.json)。
先运行其 builder，再用 topology 环境运行
`verify_t73_x_m1_handle_pair_deletion.py`；verdict 为
`PASS_X_M1_HANDLE_PAIR_DELETION_AND_FIVE_COMPONENT_STATE`。
第一条端到端 candidate slide（含显式闭合的 post-slide 4D core）位于
[`geometry/t73_candidate_t_band0_splice.json`](geometry/t73_candidate_t_band0_splice.json)，
使用 `python3 scripts/build_t73_candidate_t_band0_splice.py --check` 重建。
其范围为 `CANDIDATE_CLOSED_SPLICE_ONLY`，仍待相交与 Kirby-move 检查。
连接两个 attachment interval 的完整 candidate band disk 位于
[`geometry/t73_candidate_t_band0_surface.json`](geometry/t73_candidate_t_band0_surface.json)，
使用 `build_t73_candidate_t_band0_surface.py --check` 重建并由
`verify_t73_candidate_t_band0_surface.py` 独立检查。它是具有四部分指定边界的
8 顶点、6 三角形 framed disk。精确 barycentric 与 edge-triangle 检查同时覆盖
push-off surface 和所有 disk-vs-push triangle pairs，返回
`PASS_CANDIDATE_FRAMED_BAND_DISK_AND_PUSH_LOCAL_EMBEDDEDNESS_ONLY`。
`verify_t73_candidate_t_band0_surface_clearance.py` 检查 disk/push disk 与其余
五条 core；128184 对 quotient AABB 全部精确分离，返回
`PASS_CANDIDATE_BAND_SURFACE_OTHER_CORE_CLEARANCE_ONLY`。
`verify_t73_candidate_t_band0_relative_boundary.py` 随后检查 actual source
interval、parallel h_CS target interval、两条 movie lane 与其边界 normal，返回
`PASS_CANDIDATE_BAND0_RELATIVE_BOUNDARY_ONLY`。
`verify_t73_candidate_t_band0_relative_contacts.py` 求解精确 segment-triangle
交集参数区间，并证明所有 m1/h_CS 接触都位于这两条 attachment edge，返回
`PASS_CANDIDATE_BAND0_RELATIVE_CONTACTS_ONLY`。
`python3 scripts/verify_t73_candidate_t_band0_splice.py` 当前返回
`OPEN_PERIODIC_T3_LIFT_REQUIRED`：保存的源 core 使用 torus wrap 坐标，必须先 lift
到 universal cover，才能进行有效的 affine PL 相交检查。
已验证的连续 lift 保存于
[`geometry/t73_ar_core_universal_lifts.json`](geometry/t73_ar_core_universal_lifts.json)，
使用 `python3 scripts/build_t73_ar_core_universal_lifts.py --check` 重建。
其 closing deck translation 精确等于 `A-I` 的三列。
第一条 t-band splice 的 quotient-aware 重建位于
[`geometry/t73_candidate_t_band0_quotient_splice.json`](geometry/t73_candidate_t_band0_quotient_splice.json)，
使用 `python3 scripts/build_t73_candidate_t_band0_quotient_splice.py --check` 重建。
其 universal-cover 首尾差为已验证的 m1 deck translation。
独立 quotient verifier 为
`python3 scripts/verify_t73_candidate_t_band0_quotient_splice.py`；它将唯一
`u=0~1` mapping-torus seam 作为 gluing cell，并对其余 PL segments 返回
`PASS_CANDIDATE_QUOTIENT_FRAMED_EMBEDDEDNESS_ONLY`，同时检查其余 PL segments
及 boundary-compatible push-off。
`python3 scripts/verify_t73_candidate_t_band0_core_clearance.py` 还会对 actual
m2/m3 lift 与下述 candidate dual-cell lift 的相关 deck translates 做精确检查。
三条 candidate dual-core lift 保存于
[`geometry/t73_candidate_dual_core_lifts.json`](geometry/t73_candidate_dual_core_lifts.json)，
使用 `python3 scripts/build_t73_candidate_dual_core_lifts.py --check` 重建。
加入 candidate `u=1/2` lift 后，clearance verifier 同时检查 post-slide core
及其 push-off，并返回 `PASS_CANDIDATE_FRAMED_ALL_CORE_CLEARANCE_ONLY`。

1513 步 x-cancellation candidate movie 位于
[`geometry/t73_candidate_x_band_movie.json`](geometry/t73_candidate_x_band_movie.json)，
使用 `python3 scripts/build_t73_candidate_x_band_movie.py --check` 重建。
它同样只具有 candidate 状态，尚未重放实际 link state。
t/x 两条 candidate movie 使用
`python3 scripts/verify_t73_candidate_band_movies.py` 独立检查。当前 verdict
`PASS_CANDIDATE_MOVIE_RECORDS_ONLY` 覆盖全部 1519 条 band 与 3035 个 rectangle
segment，但不表示实际 Kirby slide movie。

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
有序的 1519 条 band strip 与端点 splice descriptor 保存于
[`geometry/t73_candidate_band_splice_descriptors.json`](geometry/t73_candidate_band_splice_descriptors.json)，
使用 `python3 scripts/build_t73_candidate_band_splice_descriptors.py --check` 重建。

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
