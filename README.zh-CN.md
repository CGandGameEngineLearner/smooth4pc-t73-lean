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
实际 passage words 与历史 railroad ledger 的比较保存于
[`geometry/t73_final_railroad_word_binding.json`](geometry/t73_final_railroad_word_binding.json)。
旧 m3 compact word 因不与 Johnson passage 顺序共轭而被拒绝；从实际 words
重建得到 1878 个 mixed crossings，connector counts 为 `84,378,4,4,0`。
使用 `python3 scripts/verify_t73_final_railroad_word_binding.py` 验收。
订正后的 target 构造继续保存于
[`geometry/t73_actual_railroad_core_coordinates.json`](geometry/t73_actual_railroad_core_coordinates.json)
（1178 个 exact generic raw-passage core crossings）、
[`geometry/t73_railroad_product_framings.json`](geometry/t73_railroad_product_framings.json)
（5 条 linking=0 的 target push-off），以及
[`geometry/t73_source_bound_standard_pd_candidate.json`](geometry/t73_source_bound_standard_pd_candidate.json)。
后者含 4748 行标准 PD、9496 个 arc labels 和1785个逐 passage 绑定的 dotted
Hopf clasp。verdict 为 `PASS_SOURCE_BOUND_STANDARD_PD_COMBINATORICS_ONLY`：
target framing 已通过，但 framed hybrid→railroad isotopy 仍开放。被拒绝的
diagonal-only closure 保留于
[`audit/t73_actual_railroad_standard_pd_gap.json`](audit/t73_actual_railroad_standard_pd_gap.json)。
三个可选自由约化 endpoint-tube candidates 保存于
[`geometry/t73_final_free_reduction_bigons.json`](geometry/t73_final_free_reduction_bigons.json)。
它们在互不碰撞的 z-foot endpoint tube 中识别 m3 的一对 inverse passage 与
r_zx 的两层嵌套 pair，但尚无 central-connector spanning surfaces。使用
`build_t73_final_free_reduction_bigons.py --check` 与
`verify_t73_final_free_reduction_bigons.py` 重建/验收；verdict 为
`PASS_FREE_REDUCTION_ENDPOINT_TUBES_ONLY`；raw-passage kappa 路径不依赖它们。
surviving framed 1-skeleton map 位于
[`geometry/t73_hybrid_to_railroad_graph_map.json`](geometry/t73_hybrid_to_railroad_graph_map.json)。
它将1785个 source vertices 与1785条 connector edges 双射到全部 raw-passage
railroad event/segment cells，包含全部1513个 hybrid replacements。使用
`verify_t73_hybrid_to_railroad_graph_map.py` 验收；verdict 为
`PASS_HYBRID_TO_RAILROAD_FRAMED_GRAPH_ISOMORPHISM_ONLY`，ambient tracks 仍开放。
graph map 已在
[`geometry/t73_hybrid_to_railroad_tubular_map.json`](geometry/t73_hybrid_to_railroad_tubular_map.json)
中扩张到五个 framed regular neighborhoods。五个 solid-torus templates 共含
5385 个 tetrahedra 与10770个 boundary triangles，closing fiber 恒等且五个
relative twist均为0。使用 `verify_t73_hybrid_to_railroad_tubular_map.py` 验收；
当前只剩 handlebody complement extension 开放。
complement boundary 数据现包含
[`geometry/t73_foot_to_dotted_slot_map.json`](geometry/t73_foot_to_dotted_slot_map.json)
及
[`geometry/t73_foot_to_dotted_disk_tracks.json`](geometry/t73_foot_to_dotted_disk_tracks.json)
中的1785条显式反射配对路径；verifier 完成2,455,940次精确固定点碰撞检查。
这些路径已在
[`geometry/t73_dotted_disk_ambient_extensions.json`](geometry/t73_dotted_disk_ambient_extensions.json)
中加厚为显式有支撑 PL ambient isotopy。可复用 corridor 模板每段含36个
spacetime tetrahedra；3570个段实例对应257040个反射配对物理四面体实例。
使用 `python3 scripts/build_t73_dotted_disk_ambient_extensions.py --write` 重建，
并以 `python3 scripts/verify_t73_dotted_disk_ambient_extensions.py` 独立验收；
verdict 为 `PASS_REFLECTION_PAIRED_AMBIENT_DOTTED_DISK_EXTENSIONS`。这只闭合
局部 foot-disk extension，不闭合 source-to-railroad complement isotopy。
每条 reduced source edge 也在
[`geometry/t73_reduced_source_connector_provenance.json`](geometry/t73_reduced_source_connector_provenance.json)
中绑定回 raw geometry：1773个 Johnson central connectors 与12个 dual-boundary
connectors 一一分区全部1785条 raw target edges。
native source-connector 的完整精确投影过大，不进入Git，保存在
`C:\Users\Administrator\.cache\t73_actual_source_connector_projection.full.json`
（约1.68 GB）。紧凑收据为
[`audit/t73_actual_source_connector_projection_receipt.json`](audit/t73_actual_source_connector_projection_receipt.json)：
7116 segments、4,791,364 个 broad candidates、1,758,060 个 exact crossings。
使用 `build_t73_actual_source_connector_projection.py --write` 重建，并用
`build_t73_actual_source_connector_projection_receipt.py` 流式生成/检查收据。
当前 source-native 七分量 connector/local-Hopf PD 骨架以 SQLite 保存于
`C:\Users\Administrator\.cache\t73_actual_source_standard_pd.sqlite`
（约817 MB），紧凑收据为
[`audit/t73_actual_source_standard_pd_sqlite_receipt.json`](audit/t73_actual_source_standard_pd_sqlite_receipt.json)。
它含1,761,630个 crossings 与3,523,260个 arc labels；这些 rows 的完整 integrity/incidence
检查命令为 `python3 scripts/verify_t73_actual_source_standard_pd_sqlite.py --full
--check-database-sha`。实际 core linking matrix 有 `lk(m_2,m_3)=-318`，dotted
linking为 `(40,269)` 与 `(189,1271)`。因此小型 zero-linking railroad target
不是固定七分量S³ link中的直接ambient-isotopic图；它仍可能经所需的
dotted-handle/handlebody map 与source等价，所以这本身不否定 κ_AR。source
但它不再称为完整 source-native PD：显式 post-x cache 证明其投影遗漏了
60,520条 replacement core segments 及对应60,520条 push segments。机器可读
缺口为
[`audit/t73_source_pd_post_x_coverage_gap.json`](audit/t73_source_pd_post_x_coverage_gap.json)，
使用 `python3 scripts/verify_t73_source_pd_post_x_coverage.py` 验收。现有 SQLite
仍是有效的 connector/local-Hopf 骨架；完整 replacement-path projection 与
source product framings 仍开放。
订正后的片段现已在
[`geometry/t73_post_x_framed_cycle_assembly.json`](geometry/t73_post_x_framed_cycle_assembly.json)
中组装为 verified graph-of-charts 上的五条闭合 framed cycles。它穷尽3558个
blocks，并给出各68176条边的 core/push cycles；每个抽象顶点均恰有一条入边
和一条出边。使用 `python3 scripts/build_t73_post_x_framed_cycle_assembly.py
--check` 与 `python3 scripts/verify_t73_post_x_framed_cycle_assembly.py`
重建/验收。这闭合的是组合 cycle incidence，不是到单一 S³ chart 的
cancellation-complement embedding。
x/m1 collar 的显式 x-product 延拓现位于
[`geometry/t73_x_m1_collar_product_extension.json`](geometry/t73_x_m1_collar_product_extension.json)：
36个 transverse tetrahedra 延拓成144个保向4-simplices。它覆盖全部12104条
remaining local core segments 与6052条 band-lane segments。verifier 同时发现
原局部 push 有4768条 lane segments 进入待删除内立方体；已有 uniform outward
framing 修复全部越界，使12104+6052条 pushed segments 均位于 collar 定义域。
使用 `python3 scripts/build_t73_x_m1_collar_product_extension.py --check` 与
`python3 scripts/verify_t73_x_m1_collar_product_extension.py` 验收。完整 hybrid
paths 的逐片仿射像仍待输出。
非平凡求像现已保存在
`C:\Users\Administrator\.cache\t73_x_m1_ejected_band_lanes.jsonl.gz`
（约58.2 MB），收据为
[`audit/t73_x_m1_ejected_band_lanes_receipt.json`](audit/t73_x_m1_ejected_band_lanes_receipt.json)。
精确 product-simplex 相交将12104条 core/outward-push lane segments 细分为
30144条 affine image segments。完整 verifier 逐片重算重心坐标 containment、
source interpolation、target image 与连续性：`python
scripts/verify_t73_x_m1_ejected_band_lanes.py --full --input-cache
C:\Users\Administrator\.cache\t73_post_x_framed_replacement_cells.jsonl.gz
--check-cache-sha`。每个 replacement 的四条 splice-end segments 也已在
`C:\Users\Administrator\.cache\t73_x_m1_ejected_splice_stubs.jsonl.gz`
中求像（约6.3 MB），收据为
[`audit/t73_x_m1_ejected_splice_stubs_receipt.json`](audit/t73_x_m1_ejected_splice_stubs_receipt.json)。
其12104条 core+push source stubs 生成25712条 affine image segments；完整验收：
`python scripts/verify_t73_x_m1_ejected_splice_stubs.py --full --input-cache
C:\Users\Administrator\.cache\t73_post_x_framed_replacement_cells.jsonl.gz
--check-cache-sha`。中间48416条 core 与48416条 push m1-complement segments
位于这些局部 germs 之外；下述 F-592/F-593 构造运输它们所需的完整 tubular map。
完整曲线 tubular layer 的第一步位于
[`geometry/t73_m1_parallel_annulus_tubular_frame.json`](geometry/t73_m1_parallel_annulus_tubular_frame.json)。
一个共同有理 outward vector 在全部34条 m1 segments 上与 tangent/parallel
frame 横截；68个 annulus triangles 生成204个非退化 tubular tetrahedra，且
274次精确 quotient 检查证明 source/push annuli 分离。使用 `python3
scripts/verify_t73_m1_parallel_annulus_tubular_frame.py` 验收。完整
nonincident tetrahedra clearance 现已通过并记录于
[`audit/t73_m1_parallel_annulus_tubular_clearance_receipt.json`](audit/t73_m1_parallel_annulus_tubular_clearance_receipt.json)：
573次精确有理凸包可行性检查未发现 quotient 中的非相邻 tetrahedron 相交。
verdict 为 `PASS_M1_PARALLEL_ANNULUS_NONINCIDENT_TETRAHEDRON_CLEARANCE`；现在可用
此 tube 运输48416条 middle complement segments。
紧支撑 ambient ejection 本身位于
[`geometry/t73_m1_parallel_annulus_ambient_ejection.json`](geometry/t73_m1_parallel_annulus_ambient_ejection.json)。
其 PL 区间映射把层 `(-1,0,2)` 送到 `(-1,1,2)`，固定支撑两侧边界，共含
408个保向 tetrahedra。完整收据
[`audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json`](audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json)
记录2100次非相邻精确凸包检查，verdict 为
`PASS_M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_SUPPORT_CLEARANCE`。其实际应用保存于
`C:\Users\Administrator\.cache\t73_x_m1_ejected_middle_complements.jsonl.gz`
（约53.2 MB），收据为
[`audit/t73_x_m1_ejected_middle_complements_receipt.json`](audit/t73_x_m1_ejected_middle_complements_receipt.json)。
全部48416条 middle core 与48416条 product-push segments 通过99858个顶点像
检查及 cache SHA 验证。完整命令：`python
scripts/verify_t73_x_m1_ejected_middle_complements.py --full --input-cache
C:\Users\Administrator\.cache\t73_post_x_framed_replacement_cells.jsonl.gz
--check-cache-sha`。结合 F-590/F-591，全部60520条 replacement core segment
images 已分块生成；但3026对 local/global endpoints 位于不同 target charts，
core 与 push 都还缺 extended transition。fail-closed 缺口记录于
[`audit/t73_x_m1_ejection_overlap_transition_gap.json`](audit/t73_x_m1_ejection_overlap_transition_gap.json)。
该缺口现已在 graph of charts 中由
`C:\Users\Administrator\.cache\t73_x_m1_ejection_overlap_transitions.jsonl.gz`
解决（约1.86 MB），收据为
[`audit/t73_x_m1_ejection_overlap_transitions_receipt.json`](audit/t73_x_m1_ejection_overlap_transitions_receipt.json)。
3026个互不相交的 framed mapping-cylinder germs 共含18156个 tetrahedra，且
逐点匹配全部3026对 core/push boundaries。完整验收：`python
scripts/verify_t73_x_m1_ejection_overlap_transitions.py --full --stub-cache
C:\Users\Administrator\.cache\t73_x_m1_ejected_splice_stubs.jsonl.gz
--middle-cache C:\Users\Administrator\.cache\t73_x_m1_ejected_middle_complements.jsonl.gz
--check-cache-sha`。charted-cycle continuity 已通过；转换到单一 affine
dotted-S³ chart 仍开放。
core 部分现已实现于单一 affine chart：
[`geometry/t73_affine_s3_core_realization.json`](geometry/t73_affine_s3_core_realization.json)。
它保留全部7092条 actual Johnson connector segments，加入全部1785条 local
Hopf arcs，并使用3558条各四段的外部 corridors，共23109条 core segments。
完整收据
[`audit/t73_affine_s3_core_realization_verification.json`](audit/t73_affine_s3_core_realization_verification.json)
记录25,318,728次精确 waypoint/endpoint-fiber incidence checks，verdict 为
`PASS_CANONICAL_AFFINE_S3_CORE_EMBEDDING`。affine push corridors、整数 framing
与完整 framed PD 仍开放。
五条 affine push cycles 现已加入
[`geometry/t73_affine_s3_framed_realization.json`](geometry/t73_affine_s3_framed_realization.json)。
其中 core 与 push 各23109段，另含两条 dotted components。完整收据
[`audit/t73_affine_s3_framed_realization_verification.json`](audit/t73_affine_s3_framed_realization_verification.json)
记录50,637,456次 push-waypoint/fiber 检查及4,567,172次非相邻
endpoint-fiber/base-segment 精确检查。verdict 为
`PASS_CANONICAL_AFFINE_S3_FRAMED_LINK_EMBEDDING`。这证明五条 disjoint
companion cycles，但尚未证明 product framing：3558条独立路由的 push corridors
没有通向 core corridors 的 ruled ribbons。fail-closed 订正位于
[`audit/t73_affine_push_corridor_framing_gap.json`](audit/t73_affine_push_corridor_framing_gap.json)。
投影或计算整数 framing 前必须先构造 corridor product ribbons。
局部修复现缓存于
`C:\Users\Administrator\.cache\t73_affine_s3_product_framed_realization.json`
（112,997,433 bytes），收据为
[`audit/t73_affine_s3_product_framed_realization_receipt.json`](audit/t73_affine_s3_product_framed_realization_receipt.json)。
它沿每条 core corridor 线性插值已验证的两端 product normals，生成28464个
ruled triangles；全部7116个端点匹配及28464次局部横截检查通过。使用
`python3 scripts/verify_t73_affine_s3_product_framed_realization.py` 验收；
nonlocal clearance 现已在
[`audit/t73_affine_s3_product_ribbon_global_clearance.json`](audit/t73_affine_s3_product_ribbon_global_clearance.json)
中通过。保持全部 endpoint product normals 不变，仅把三个 corridor 内部 normals
缩小为 `1/1000` 后，1779个 exact triangle/triangle 与3560个 exact
segment/triangle survivors 全部无交。verdict 为
`PASS_AFFINE_S3_PRODUCT_CORRIDOR_RIBBON_GLOBAL_CLEARANCE`；五条 affine
companions 现已认证为 product push-offs。
其精确 affine-model self-linkings 保存于
[`geometry/t73_verified_integer_surgery_framings.json`](geometry/t73_verified_integer_surgery_framings.json)：
`m_2=-156621`、`m_3=-3338112`、`r_xy=-1`、`r_yz=-1`、`r_zx=-3`。
五个 component databases 位于 `C:\Users\Administrator\.cache\`，文件名为
`t73_product_self_linking_*.sqlite`；m3 约4.30 GB。全部25,776,472条 crossings
及数据库 SHA 已在
[`audit/t73_product_self_linking_full_verification.json`](audit/t73_product_self_linking_full_verification.json)
中独立重放。使用 `python3 scripts/verify_t73_verified_integer_surgery_framings.py`
验收；verdict 为 `PASS_FIVE_AFFINE_MODEL_PRODUCT_SELF_LINKINGS_ONLY`。十个 model
pairwise core linkings 也已在
[`audit/t73_pairwise_core_linking_full_verification.json`](audit/t73_pairwise_core_linking_full_verification.json)
中全量重放。合成的七分量 dotted-surgery matrix 有 determinant=`-3`、Smith
diagonal `(1,1,1,1,1,1,3)`，预测 boundary H1=`Z/3`；这与三条3-handles 最终
得到 S³ 所需的 post-2-handle boundary 矛盾。因此这些精确数值只属于当前
affine model，不能作为 T73 surgery framings；见
[`audit/t73_affine_kirby_matrix_homology_obstruction.json`](audit/t73_affine_kirby_matrix_homology_obstruction.json)。
精确修正目标及其局部 PL 实现分别保存在
[`geometry/t73_kirby_homology_admissible_correction.json`](geometry/t73_kirby_homology_admissible_correction.json)
和
[`geometry/t73_dual_zero_framing_twist_ribbons.json`](geometry/t73_dual_zero_framing_twist_ribbons.json)。
由于 dotted-incidence 子块 determinant=`-1`，在保留全部 core 与非对角
linking 的条件下，三条 dual framing 被唯一强制为零。构造器加入有理正方形
法向 twist `+1,+1,+3`；144 个精确 self-linking crossings 全部重放为零，40 个
新 ribbon triangles 对 32,028 个保留 ribbon triangles 和 46,260 条 framed
segments 的增量全局检查通过。汇总数据
[`geometry/t73_homology_admissible_affine_framed_model.json`](geometry/t73_homology_admissible_affine_framed_model.json)
的 rank=`4`、nullity=`3`、signature=`0`、Smith diagonal 为
`(1,1,1,1,0,0,0)`。verdict 为
`PASS_HOMOLOGY_ADMISSIBLE_AFFINE_FRAMED_MODEL_ONLY`；相对 T73 的
meridian/longitude 等价仍为 OPEN。此外，覆盖门禁
[`audit/t73_affine_core_atlas_coverage_gap.json`](audit/t73_affine_core_atlas_coverage_gap.json)
证明这仍是 skeleton model：它含 7,092 条保留 connector、1,785 条
dotted-passage 与 14,232 条替代 corridor，却没有完整 atlas 所要求的 60,520 条
显式 post-x replacement core segments 及 60,520 条 pushes；完整 atlas 总量为
80,007/84,383。因此这里的同调 PASS 不是完整 T73 PD PASS。重建与验收命令：

```bash
python3 scripts/build_t73_kirby_homology_admissible_correction.py --write
python3 scripts/build_t73_dual_zero_framing_twist_ribbons.py --write
python3 scripts/build_t73_dual_zero_framing_twist_global_clearance_receipt.py
python3 scripts/build_t73_homology_admissible_affine_framed_model.py --write
python3 scripts/verify_t73_homology_admissible_affine_framed_model.py
python3 scripts/audit_t73_affine_core_atlas_coverage.py --check
python3 scripts/verify_t73_affine_core_atlas_coverage_gap.py
```

覆盖修复的第一阶段现已在 Git 外物化到
`C:\Users\Administrator\.cache\t73_x_m1_complete_explicit_replacement_images.jsonl.gz`
（68,417,260 字节），构造收据和首次完整独立重放收据分别为
[`audit/t73_x_m1_complete_explicit_replacement_images_receipt.json`](audit/t73_x_m1_complete_explicit_replacement_images_receipt.json)
与
[`audit/t73_x_m1_complete_explicit_replacement_images_verification.json`](audit/t73_x_m1_complete_explicit_replacement_images_verification.json)。
全部 1,513 个 replacement blocks 已从 lane、splice-stub、middle-complement
及 overlap-transition 流逐项重建，得到 77,182 条 core 与 81,558 条 push
segments，其中包含 6,052 条显式 transition center tracks；24,208 个 piece
boundary matches 和完整缓存 SHA 已独立重放。这闭合的是分散 4D atlas 的组装，
尚未闭合公共三维流形坐标图。WSL 重建命令：

```bash
python3 scripts/build_t73_x_m1_complete_explicit_replacement_images.py \
  --output /mnt/c/Users/Administrator/.cache/t73_x_m1_complete_explicit_replacement_images.jsonl.gz
python3 scripts/build_t73_x_m1_complete_explicit_replacement_images_verification.py
```

其中 48,416-segment 的 middle-complement 部分现已相对源数据映入显式有理 R3
solid torus。坐标图
[`geometry/t73_x_m1_canonical_r3_annulus_chart.json`](geometry/t73_x_m1_canonical_r3_annulus_chart.json)
含 204 个 quotient vertices、408 个非退化 tetrahedra，以及连通的 408-triangle
torus boundary。映射流缓存于
`C:\Users\Administrator\.cache\t73_x_m1_middle_paths_r3.jsonl.gz`；构造和全量
重放收据分别为
[`audit/t73_x_m1_middle_paths_r3_receipt.json`](audit/t73_x_m1_middle_paths_r3_receipt.json)
与
[`audit/t73_x_m1_middle_paths_r3_verification.json`](audit/t73_x_m1_middle_paths_r3_verification.json)。
全部 99,858 个源 Q4 core/push 点均恢复出唯一 quotient 角索引；1,511 条路径
正向、2 条反向。96,832 个有理 framing-ribbon triangles 位于 1,513 个两两不交
的径向条带中。尚待映入 R3 的部分被精确缩小为 splice stubs、band lanes 与
overlap tracks。重建命令：

```bash
python3 scripts/build_t73_x_m1_canonical_r3_annulus_chart.py --write
python3 scripts/build_t73_x_m1_middle_paths_r3.py \
  --output /mnt/c/Users/Administrator/.cache/t73_x_m1_middle_paths_r3.jsonl.gz
python3 scripts/build_t73_x_m1_middle_paths_r3_verification.py
```

逐字端点审计随后发现并修复了另一项 framing 接口。全部 3,026 个 replacement
core ports 都与相邻 Johnson connector 或 dual passage 端点模 mapping-torus deck
相等，但原先没有一个 push port 相等；四类 mismatch 的数量为
`2480,538,4,4`，见
[`audit/t73_post_x_connector_stub_framing_gap.json`](audit/t73_post_x_connector_stub_framing_gap.json)。
缓存
`C:\Users\Administrator\.cache\t73_post_x_connector_stub_framing_transitions.jsonl.gz`
现含 3,026 个显式 (1/10^6)-collar normal homotopies 与 12,104 个 ruled
ribbon triangles。6,052 个 endpoint-normal matches、12,104 个法向横截检查、
relative twist 总和 0 及完整缓存 SHA 已在
[`audit/t73_post_x_connector_stub_framing_transitions_verification.json`](audit/t73_post_x_connector_stub_framing_transitions_verification.json)
中重放。verdict 为
`PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITIONS_FULL_LOCAL`。全局验收记录于
[`audit/t73_post_x_connector_stub_framing_transition_global_clearance.json`](audit/t73_post_x_connector_stub_framing_transition_global_clearance.json)：
精确替换 3,026 条旧 product segments 后，12,104 个新 triangles 对 8,164 个
保留 product-ribbon triangles 和 20,268 条 corrected framed segments 完成
检查；每个阶段约 1,700 万宽候选最终缩为 4,527 个精确有理相交判定，全部无交。
verdict 为
`PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITION_GLOBAL_CLEARANCE`。

collar-product support 本身不能冒充缺失的 ambient R3 boundary。精确审计
[`audit/t73_x_m1_collar_boundary_topology.json`](audit/t73_x_m1_collar_boundary_topology.json)
得到一个连通闭 support boundary，其 simplex 数为 `(32,176,288,144)`、边界算子
秩为 `(0,31,144,143)`、有理 Betti 数为 `(1,1,1,1)`。重心 carrier 检查表明
27,228 个 lane/stub core 点实例位于该 support boundary，但 24,252 个 band-lane
点严格位于其四维内部；独立 target-shell 统计得到同样划分。verdict 为
`PASS_X_M1_COLLAR_SUPPORT_BOUNDARY_TOPOLOGY_AUDIT`。因此下一项必须是完整
x/m1 handle-pair deletion 给出的真实 ambient 3-boundary map，而不是 support
boundary 的投影或 Schlegel 图。

标准 x/m1 handle pair 本身现已有有限 S³ 识别证书：
[`geometry/t73_x_m1_standard_pair_boundary_s3.json`](geometry/t73_x_m1_standard_pair_boundary_s3.json)。
其 10 个 4-simplices 给出 26 个 boundary tetrahedra；删除 `(0,1,2,3)` 后，
余下 25 个 tetrahedra 有显式 shelling。24 次二维圆盘附着及 240 个纯交检查
通过，最终边界严格等于被删 tetrahedron 的四个面；补回最后一个 3-ball 即识别
为 S³。verdict 为
`PASS_STANDARD_X_M1_HANDLE_PAIR_BOUNDARY_S3_SHELLING`。所以剩余问题是把
actual collar refinement 映入这个标准边界，而不是标准取消目标的拓扑未知。

Regina 7.4.1 安装在隔离的 WSL 环境
`/home/lifesize/.cache/t73-regina-venv`。独立组合识别收据
[`audit/t73_x_m1_regina_boundary_recognition.json`](audit/t73_x_m1_regina_boundary_recognition.json)
给出：144-tetrahedron support boundary 的唯一 prime isoSig 为 `cMcabbjaj`，
与 Regina 内置 `S2 x S1` 完全一致；标准边界简化为单 tetrahedron 的 S³
isoSig `bkaagj`。

product 结构还给出了显式非分离 cubical sphere 和 cut-open chart。在
[`geometry/t73_x_m1_support_generator_sphere_cut.json`](geometry/t73_x_m1_support_generator_sphere_cut.json)
中，8-vertex A 层含 18 edges、12 triangles；在另一侧复制 A 后得到
40-vertex、144-tetrahedron 复形及两个球面边界。分别锥封两个球面后，Regina
将结果识别为 S³，故 cut complex 为 `S2 x I`。其精确有理 R3 realization 位于
[`geometry/t73_x_m1_support_cut_r3_shell.json`](geometry/t73_x_m1_support_cut_r3_shell.json)：
`A-B-D-C-A_copy` 五层映成半径 1–5 的同心立方球面。144 个 tetrahedra 的
精确 determinant 全部非零，总绝对体积严格为 `992`，即半径 5 与半径 1
立方体的体积差。

WSL 重建 Regina 收据：

```bash
/home/lifesize/.cache/t73-regina-venv/bin/python \
  scripts/build_t73_x_m1_regina_boundary_recognition.py
python3 scripts/build_t73_x_m1_support_generator_sphere_cut.py --write
/home/lifesize/.cache/t73-regina-venv/bin/python \
  scripts/build_t73_x_m1_support_generator_sphere_cut_regina_verification.py
python3 scripts/build_t73_x_m1_support_cut_r3_shell.py --write
```

全部 splice-stub **core** pieces 现已映入该 shell。缓存
`C:\Users\Administrator\.cache\t73_x_m1_splice_stub_cores_r3.jsonl.gz`
及收据
[`audit/t73_x_m1_splice_stub_cores_r3_receipt.json`](audit/t73_x_m1_splice_stub_cores_r3_receipt.json)、
[`audit/t73_x_m1_splice_stub_cores_r3_verification.json`](audit/t73_x_m1_splice_stub_cores_r3_verification.json)
包含 1,513 条记录与 10,582 个精确分片仿射 segments。每个开 piece 都有唯一
`AC` boundary-side carrier，故无需选择即可映到 cut shell 的 `C-A_copy` 部分。
独立全量重放重新求解全部源重心坐标，复现 21,164 个 endpoint occurrences、
4,530 个 continuity matches，并检查流与缓存 SHA。verdict 为
`PASS_X_M1_ALL_SPLICE_STUB_CORES_R3_FULL`。该结论严格限于 core：把保存的 push
normal 延拓进 R3 shell collar 仍为 OPEN，15,151 个 interior band-lane pieces
也仍待处理。

```bash
python3 scripts/build_t73_x_m1_splice_stub_cores_r3.py \
  --output C:/Users/Administrator/.cache/t73_x_m1_splice_stub_cores_r3.jsonl.gz
python3 scripts/build_t73_x_m1_splice_stub_cores_r3_verification.py
```

剩余 support-boundary lane restriction 也已完整处理。精确数据
[`geometry/t73_x_m1_boundary_band_lane_core_r3.json`](geometry/t73_x_m1_boundary_band_lane_core_r3.json)
扫描全部 15,158 个 band-lane core pieces；严格只有 7 个开线段 carrier 位于
`AC` side，它们连续组成 band 0 的完整 `positive_band_lane`（两个源 segments），
并有 6 个精确 R3 continuity matches。独立 verifier 先用 target outer-shell
方程重新定位同一批 7 个 pieces，再重算其源重心 R3 像。verdict 为
`PASS_X_M1_BOUNDARY_BAND_LANE_CORE_R3_FULL`。其余 15,151 个 pieces 仍为
interior，不从该 boundary prefix 推断。

全部 interior lane 数据现在也有 source-bound 的逐 cell R3 模型，但不冒充已完成
global port gluing。atlas
[`geometry/t73_x_band_canonical_r3_cell_atlas.json`](geometry/t73_x_band_canonical_r3_cell_atlas.json)
把 1,513 个实际 6-vertex/4-triangle band disks 分别映为互不相交的 2×1 有理矩形，
并保留精确 source boundary order `negative=0-2-4`、`positive=5-3-1`、两个
attachment intervals、component、orientation、source-cell SHA 与 relative
twist 0。独立 verifier 检查 6,052 个 core triangles、12,104 个 lane-ribbon
triangles 及 18,156 个非退化 surface-product tetrahedra。相邻 x supports 的
精确间隔均为 2，故全部规范 band cells 两两不交。verdict 为
`PASS_ALL_X_BAND_CANONICAL_R3_CELL_ATLAS_FULL`。剩余全局任务被明确限制为：
每个 band 的四个 attachment ports 到 shell stubs 与 middle-transition charts 的
显式映射。

每个 band 的四个 **shell attachment ports** 现已全局粘合。缓存
`C:\Users\Administrator\.cache\t73_x_band_global_r3_port_strips.jsonl.gz`
由
[`audit/t73_x_band_global_r3_port_strips_receipt.json`](audit/t73_x_band_global_r3_port_strips_receipt.json)
及
[`audit/t73_x_band_global_r3_port_strip_clearance.json`](audit/t73_x_band_global_r3_port_strip_clearance.json)
绑定。每个 band 的两个 source 与两个 target shell ports 逐点固定，disk 沿五段
centerline 细分。3,026 个中心端点的 `y-1000003*x` 值两两不同；vertical
columns 与 routing rays 由该精确泛函分离，horizontal pieces 使用不同整数高度，
exterior pieces 位于 `x>10000`，strip 半宽严格小于所有分离量的一半。band 内
68,085 对 triangles 最终执行 13,622 个精确非关联相交判定，全部无交。verdict
为 `PASS_X_BAND_GLOBAL_R3_PORT_STRIP_CLEARANCE`。这闭合了 band-to-shell core
port glue；push framing 与独立的 middle transition glue 仍为 OPEN。

从 shell stubs 到 middle annulus chart 的全部 **core** transitions 也已路由。
middle chart 平移 `(20000,2000,0)`，3,026 条 transition paths 保存于
`C:\Users\Administrator\.cache\t73_x_m1_global_r3_middle_transition_cores.jsonl.gz`，
收据为
[`audit/t73_x_m1_global_r3_middle_transition_cores_receipt.json`](audit/t73_x_m1_global_r3_middle_transition_cores_receipt.json)。
精确泛函 `y-1000033*x+z` 在全部 6,052 个 shell/middle endpoints 上单射；提升
方向 `(0,-1,1)` 保持该泛函，每条 transition 再使用独立平面 `z=3000+j` 与
exterior x interval。独立重放验证 15,130 个 segments、6,052 个 endpoint
matches、12,104 个 functional-line identities 及完整缓存 SHA。verdict 为
`PASS_X_M1_GLOBAL_R3_MIDDLE_TRANSITION_CORES_FULL`。它与 band strips、stub
paths、平移后 middle curves 的跨系统 clearance，以及全部 push transitions，
仍为 OPEN。

四个 core 子系统现已在同一 R3 坐标系中组装为完整 replacement paths。缓存
`C:\Users\Administrator\.cache\t73_x_m1_complete_global_r3_replacement_cores.jsonl.gz`
由
[`audit/t73_x_m1_complete_global_r3_replacement_cores_receipt.json`](audit/t73_x_m1_complete_global_r3_replacement_cores_receipt.json)
绑定。每条 1,513 records 严格串接九类保存 pieces：outer stub、negative band
lane、target stub、first transition、平移后的 middle、last transition、target
stub、positive band lane 和 outer stub。独立全量重放重建全部 89,258 个有理
segments 与 12,104 个跨 piece endpoint 等式，并检查 6,807,692-byte 缓存 SHA。
verdict 为 `PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORES_FULL`。这是完整坐标
与连续性结果；统一 all-segment embedding-clearance 门禁及完整 push paths 仍为
OPEN。

V4 的第一道 ribbon gate 在局部即否证 V4。在
[`audit/t73_x_m1_outer_collar_v4_ribbon_candidate_matrix.json`](audit/t73_x_m1_outer_collar_v4_ribbon_candidate_matrix.json)
中，interface 3018 的 retained source germ 与 start skew lift 形成共面同侧折叠；
精确局部星 normals 的叉积为零、点积为正
`6509/250000000000`。V5 只修复 8 条 dual collars，使用保持 F 的 lift
`(1/499900,233/499900,1)`；3,018 条 Johnson collars 全部不变。9,504,077-byte
cache 保持 18,156 个 core/push segments 与 36,312 个 triangles。独立重放检查
18,156 个 transversality 方程和全部 15,134 个局部星：15,130 个异面横截，4 个
dual germs 共面反向。见
[`audit/t73_x_m1_framed_outer_interface_collars_v5_verification.json`](audit/t73_x_m1_framed_outer_interface_collars_v5_verification.json)。
新的全局矩阵通过前，V5 仍为 `CANDIDATE_UNVERIFIED`。

V5 三张矩阵与 one-skeleton clearance 现已通过。core、push、有向 mutual 的
broad counts 分别为 14,249,042、14,249,042、28,516,174；对应 GMP 精确检查
为 6,048、75,610、90,784，交点均为 0。ribbon artifact
[`audit/t73_x_m1_outer_collar_v5_ribbon_candidate_matrix.json`](audit/t73_x_m1_outer_collar_v5_ribbon_candidate_matrix.json)
包含 18,156 个 rectangles/36,312 个 triangles、全部 15,134 个合法局部星，
以及 8 个语义类型对中的 14,233,908 个非 incidence candidates。八类矩形通过
精确 clearance 前，V5 仍只算 candidate。

该精确检查否证 V5：interface 3024 的 start-lift triangle 0 与 interface 3023
的 first-ray triangle 0 在
[`audit/t73_x_m1_outer_collar_v5_ribbon_clearance.json`](audit/t73_x_m1_outer_collar_v5_ribbon_clearance.json)
记录的有理点相交，edge 参数为非零的 `2/28015882679000001`。V6 保持共同 dual
lift，但把 4 条 `after` dual collars 送到负 exterior x，4 条 `before` 保持正侧。
9,661,382-byte V6 cache 只改变这 4 条记录。独立重放验证全部 18,156 个 normal
方程、15,134 个局部星，并用完整精确谓词重算 V5 原三角形对，现已无交。见
[`audit/t73_x_m1_framed_outer_interface_collars_v6_verification.json`](audit/t73_x_m1_framed_outer_interface_collars_v6_verification.json)。
重新生成全局矩阵前，V6 仍只算 candidate。

V6 新矩阵含 core/core 14,249,056、push/push 14,249,056、有向 mutual
28,516,206 个候选；完整 one-skeleton 再次以 6,048、75,610、90,784 个精确
方程通过。但精确 ribbon clearance 否证 V6：interface 3020 的 start-lift
triangle 0 与 interface 3019 的 first-ray triangle 0 在已保存有理点相交，edge
参数为 `1/28014908919000000`。因此统一 before/after 半空间规则错误。四对
shared-dual 的穷尽精确检查给出最小 V7 分配：保持全部 V5 符号，仅把 interfaces
3022、3023 送到负 exterior x。

V7 现精确实现该两记录修改。9,665,877-byte cache 中 3,024 条 V5 collars 保持
字面不变；独立重放检查两个历史 triangle pairs 与全部局部星。新 one-skeleton
矩阵含 core/core 14,249,037、push/push 14,249,037、mutual 28,516,170 个候选；
三层分别以 6,048、75,610、90,784 个 GMP 方程通过。ribbon 矩阵含八类
14,233,903 个非 incidence candidates。精确 F 区间将其降至 9,098 个 overlaps，
exact bounds 后仅 48 个 triangle-pair checks，全部无交。verdict 为
`PASS_X_M1_OUTER_COLLAR_V7_RIBBON_CLEARANCE`。这证明 V7 collar ribbon 系统内部
嵌入；与 retained/replacement ribbons 的交叉 clearance 及 ambient support
仍为 OPEN。

第一张跨系统矩阵现为
[`audit/t73_x_m1_outer_collar_v7_replacement_ribbon_candidate_matrix.json`](audit/t73_x_m1_outer_collar_v7_replacement_ribbon_candidate_matrix.json)。
它比较 18,156 个 collar rectangles 与全部 92,284 个 replacement rectangles：
得到 19,224,171 个扩张 AABB pairs，其中含 3,026 个精确 target framing-edge
邻接；全部 target 局部星均为异面横截。19,221,145 个非 incidence pairs 只在
五个 collar-type/replacement-system 类中，和向外舍入 exact-F intervals 相交后
剩 4,809,221 个 broad survivors。当前仅是 matrix evidence，下一步做 exact
skew/triangle clearance。

该精确跨系统 clearance 现已在
[`audit/t73_x_m1_outer_collar_v7_replacement_ribbon_clearance.json`](audit/t73_x_m1_outer_collar_v7_replacement_ribbon_clearance.json)
中通过。4,809,221 个 AABB/F survivors 中，exact bounds 排除 1,342 个，精确
core-tangent skew axes 排除其余 4,807,879 个；无需进入 triangle solver，交点为
0。保存的完整运行收据为
[`audit/t73_x_m1_outer_collar_v7_replacement_ribbon_clearance_verification.json`](audit/t73_x_m1_outer_collar_v7_replacement_ribbon_clearance_verification.json)。
retained Johnson/dual 跨系统 clearance 与 ambient support 仍为 OPEN。

retained-side 库存与 clearance 现由
[`audit/t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix.json`](audit/t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix.json)
和
[`audit/t73_x_m1_outer_collar_v7_retained_ribbon_clearance.json`](audit/t73_x_m1_outer_collar_v7_retained_ribbon_clearance.json)
闭合。原 7,656 个非-x segments 中精确删除 3,026 个被 collar 替换的 terminal
segments，留下 4,630 个 rectangles：4,074 connector、524 Johnson handle
arcs、24 bottom-closure、8 dual。3,018 个 retained source-edge stars 全部横截；
4 个被完全替换的 dual passages 通过 V7 内部已验证 germ stars 连接。1,651,086
个非 incidence AABB candidates 降为 825,896 个 AABB/F survivors，全部由精确
skew axes 分离，交点为 0。现在只有 relative isotopy trace 与 tetrahedral
ambient support 阻止 collars 升级为 actual map。

两阶段 trace 现已显式保存于 22,041,553-byte cache
`C:\Users\Administrator\.cache\t73_x_m1_outer_collar_v7_isotopy_trace.jsonl.gz`。
每条旧 germ-to-port segment 先等分为五段，在 phase 1 以 constant source normal
线性送到五段 V7 route；phase 2 固定 core，仅改变 terminal push normal。cache
在 R3xI 中包含 30,260 个 core trace triangles、30,260 个 translated push trace
triangles 和 6,052 个 phase-two push triangles。独立重放检查 15,130 个全时间
edge noncollapse 方程及每个 R4 triangle rank。见
[`audit/t73_x_m1_outer_collar_v7_isotopy_trace_verification.json`](audit/t73_x_m1_outer_collar_v7_isotopy_trace_verification.json)。
spacetime 全局嵌入和 fixed-boundary tetrahedral ambient extension 通过前，它仍是
局部候选。

统一全局时间版本保存在 15,154,391-byte 持久 cache
`/home/lifesize/.cache/t73_x_m1_outer_collar_v7_isotopy_trace_v2.jsonl.gz`，
构造元数据位于
[`audit/t73_x_m1_outer_collar_v7_isotopy_trace_v2_receipt.json`](audit/t73_x_m1_outer_collar_v7_isotopy_trace_v2_receipt.json)，
独立重放收据位于
[`audit/t73_x_m1_outer_collar_v7_isotopy_trace_v2_verification.json`](audit/t73_x_m1_outer_collar_v7_isotopy_trace_v2_verification.json)。
phase 1 使用 `[0,1/2]`，phase 2 使用 `[1/2,1]`，并补全 v1 未记录的静止 core
与静止 push-prefix world sheets。3,026 条记录共含 60,520 个完整 core 和
60,520 个完整 push triangles；6,052 个 core/push 阶段边界匹配及 121,040
次精确 R4 rank 检查全部通过。它是下一步全局 R4 相交门禁的完整局部输入，尚不
证明 spacetime 全局嵌入或 ambient extension。

在 WSL 中重建并独立验收：

```bash
python3 scripts/build_t73_x_m1_outer_collar_v7_isotopy_trace_v2.py
python3 scripts/build_t73_x_m1_outer_collar_v7_isotopy_trace_v2_verification.py --write --check-files
python3 -m unittest tests.test_t73_x_m1_outer_collar_v7_isotopy_trace_v2
```

同时移动方案的全局 clearance 探测保存在
[`audit/t73_x_m1_outer_collar_v7_simultaneous_phase_one_core_broad_probe.json`](audit/t73_x_m1_outer_collar_v7_simultaneous_phase_one_core_broad_probe.json)。
即使使用包含 `F=y-1000033*x+2*z` 及其时间耦合版本的 24 个保守线性
泛函边界，仅 phase-one core triangles 仍留下 140,683,374 个非邻接候选。
这否定的是该 broad-phase 作为实用 exact-clearance 路线，并不否定 isotopy
候选本身。

替代构造把 collar `i` 排入互不重叠的有理时间槽
`[i/3026,(i+1)/3026]`，并在中点分割两个局部阶段。完整的
22,303,951-byte cache 位于
`/home/lifesize/.cache/t73_x_m1_outer_collar_v7_sequential_isotopy_trace.jsonl.gz`。
构造元数据与独立重放分别位于
[`audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_receipt.json`](audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_receipt.json)
和
[`audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_verification.json`](audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_verification.json)。
3,026 条记录含 90,770 个完整 core 和 121,020 个完整 push world-sheet
triangles。独立重放检查 15,130 个边界匹配、211,790 个精确 R4 ranks 以及
`[0,1]` 的无缝覆盖；不同 moving-sheet interiors 由时间槽直接分离。
moving-versus-static clearance 和 fixed-boundary ambient extension 仍为 OPEN。

在 WSL 中重建并验证 sequential trace：

```bash
python3 scripts/build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace.py
python3 scripts/build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace_verification.py --write --check-files
python3 -m unittest tests.test_t73_x_m1_outer_collar_v7_sequential_isotopy_trace
```

第一个全局 sequential 门禁保存在
[`audit/t73_x_m1_outer_collar_v7_sequential_static_core_clearance.json`](audit/t73_x_m1_outer_collar_v7_sequential_static_core_clearance.json)。
在时间槽边界只会出现 `final_interface < source_interface` 的混合 pair。
18,156 个 final 与 3,026 个 source core segments 经向外舍入的三维 AABB
枚举后仅剩 3,022 个有序候选。独立精确有理线段方程分离其中 3,018 个；其余
4 个只在唯一的 dual-germ 公共端点相交，且两条离开方向共线反向。因此有序混合
静态 core 的禁止交点为 0。push、ribbon 和 active-moving-sheet clearance
仍为 OPEN。重建和独立检查命令：

```bash
python3 scripts/build_t73_x_m1_outer_collar_v7_sequential_static_core_clearance.py --write --check
python3 scripts/verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance.py
python3 -m unittest tests.test_t73_x_m1_outer_collar_v7_sequential_static_core_clearance
```

其余 ordered mixed one-skeleton 矩阵由
[`audit/t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance.json`](audit/t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance.json)
闭合。push/push 有 3,022 个候选，其中 3,018 个精确分离、4 个为允许的反向
push germs；final-core/source-push 与 final-push/source-core 各有
3,018 个候选，精确交点均为 0。独立 verifier 因而重放 9,058 次精确线段检查、
9,054 个分离、4 个允许 incidence，禁止交点为 0。ribbon 和
active-moving-sheet clearance 仍为 OPEN。

```bash
python3 scripts/build_t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance.py --write --check
python3 scripts/verify_t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance.py
python3 -m unittest tests.test_t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance
```

有序混合 framed ribbons 在
[`audit/t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance.json`](audit/t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance.json)
中通过。同一批 3,022 个 rectangle 候选分为 4 个允许的
`COPLANAR_OPPOSITE_SIDES` dual-germ stars 和 3,018 个非邻接 pairs。
GMP triangle 实现与独立的提升四维重心 verifier 均执行 12,072 次精确
triangle-pair tests，禁止交点为 0。因此 sequential schedule 中出现的每个
静止 source/final framed mixture 均已嵌入。active-moving-sheet clearance
仍为 OPEN。

```bash
python3 scripts/build_t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance.py --write --check
python3 scripts/verify_t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance.py
python3 -m unittest tests.test_t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance
```

第一个跨系统门禁找到并修复了真实碰撞，没有提前升级该 assembly。流式 Rust
1.98.1 checker 位于
[`rust/t73_exact_cross_clearance`](rust/t73_exact_cross_clearance)，使用
`num-bigint`/`num-rational`。v1 route 的 transition 0 与 band 1
`target_complement_first` segment 1 精确相交；反证保存在
[`audit/t73_x_m1_cross_system_core_clearance_obstruction.json`](audit/t73_x_m1_cross_system_core_clearance_obstruction.json)。
v2 builder 在 skew lift 前沿 incident stub 的延长方向插入 `1/1000000` continuation
germ，缓存为
`C:\Users\Administrator\.cache\t73_x_m1_repaired_global_r3_middle_transition_cores.jsonl.gz`。
精确修复收据
[`audit/t73_x_m1_repaired_stub_cross_clearance.json`](audit/t73_x_m1_repaired_stub_cross_clearance.json)
检查 3,026 个 escape germs：3,630 个精确同线候选恰给出 3,026 个预期端点接触、
额外 0。全部 32,021,132 个 repaired skew-lift/stub 对经三素数筛选后 survivor
为 0。verdict 为 `PASS_X_M1_REPAIRED_STUB_CROSS_CLEARANCE`。旧 v1 cache 与
obstruction 保留，可继续重放。

repaired transitions 现已进入新的完整 assembly；有碰撞的 v1 assembly 未被覆盖。
v2 缓存
`C:\Users\Administrator\.cache\t73_x_m1_complete_global_r3_replacement_cores_v2.jsonl.gz`
及收据
[`audit/t73_x_m1_complete_global_r3_replacement_cores_v2_receipt.json`](audit/t73_x_m1_complete_global_r3_replacement_cores_v2_receipt.json)
包含 1,513 条九-piece paths、92,284 个 core segments 与 12,104 个精确接缝。
独立重放重建每个 vertex/range 并检查 8,242,321-byte cache SHA。verdict 为
`PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORES_V2_FULL`。剩余 core clearance
被限制为 repaired non-shell transition segments 对 band strips 与平移 middle 的
检查，以及绑定 F-563 已有的 stub embeddedness 归纳证明。push paths 仍为 OPEN。

上述三项 v2 core-clearance obligations 现已闭合两项。归纳传输收据
[`audit/t73_x_m1_stub_r3_embeddedness_transfer.json`](audit/t73_x_m1_stub_r3_embeddedness_transfer.json)
把 1,514 个不同初始 belt positions、F‑563 的 23,265,900 个精确 current-state
segment/triangle checks 与 AC-side PL homeomorphism 绑定，证明 6,052 个 source
stub segments 细分为 10,582 条 R3 pieces 后仍为嵌入不交并。另一方面，
[`audit/t73_x_m1_repaired_transition_middle_clearance.json`](audit/t73_x_m1_repaired_transition_middle_clearance.json)
验证全部 48,416 个 translated middle segments 位于 `z=0`，而 3,026 条 repaired
transitions 各自只有声明的 middle endpoint 位于该平面，其余顶点全在 `z>0`；
因此恰有 3,026 个端点接触、额外 0。v2 core 唯一剩余跨系统检查是 repaired
transition non-shell segments 对 band strips。

最后一项 core cross-check 现由 negative-height v3 routes 闭合。v3 transition
cache 使用高度 `-3000-j`；全部 non-shell transition segments 满足 `z<=0`，
而 band horizontals 的 z 严格接近或高于 100。对唯一剩余的 shell escape/skew
对 band-column 情形，Shapely outward-rounded-box builder 与独立 NumPy interval
verifier 均在 6,052×6,052 段之间得到 conservative xy candidates 0，见
[`audit/t73_x_m1_negative_transition_band_clearance.json`](audit/t73_x_m1_negative_transition_band_clearance.json)。
最终 v3 路径缓存于
`C:\Users\Administrator\.cache\t73_x_m1_complete_global_r3_replacement_cores_v3.jsonl.gz`。
汇总证书
[`audit/t73_x_m1_complete_global_r3_replacement_core_embedding_v3.json`](audit/t73_x_m1_complete_global_r3_replacement_core_embedding_v3.json)
逐项列出并验证全部 10 个无序 subsystem pairs，认证 1,513 条 paths、全部
92,284 个 core segments 构成一个全局嵌入 R3 replacement system。verdict 为
`PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORE_EMBEDDING_V3`。完整 push paths
与 framing ribbons 仍为 OPEN，不从 core 结果推断。

framing 重建现从完整 v3 core 开始。缓存
`C:\Users\Administrator\.cache\t73_x_band_global_r3_push_disks.jsonl.gz`
及收据
[`audit/t73_x_band_global_r3_push_disks_receipt.json`](audit/t73_x_band_global_r3_push_disks_receipt.json)
为每个 global band strip 指定方向 `(1,1,2)`、尺度 `band_width/1000` 的常量有理
product displacement；该方向对全部 15,130 个 strip triangles 横截。1,513 条
records 含 15,130 个 core 与 push triangles、30,260 个 lane framing-ribbon
triangles、45,390 个非退化 surface-product tetrahedra；所有 source relative
twist 均为 0。独立全量重放检查全部单元及 9,616,648-byte cache SHA。verdict
为 `PASS_X_BAND_GLOBAL_R3_PUSH_DISKS_FULL_LOCAL_PRODUCT`。全局 push-disk
clearance 以及把这些 push ports 粘到 stub/transition pushes 仍为 OPEN。
首次全局 disk 检查 fail-closed：band 0 core triangle 0 与平移后的 push triangle 2
相交，精确记录位于
[`audit/t73_x_band_global_r3_push_disk_obstruction.json`](audit/t73_x_band_global_r3_push_disk_obstruction.json)。
因此保存的 product tetrahedra 仍是有效局部单元，但常量平移已被否定为全局平行
**disk**。修复方向改为仅构造 Kirby diagram 实际需要的两条 attaching-lane
push paths 与 ruled framing ribbons。

该 lane-only 修复已经成功。缓存
`C:\Users\Administrator\.cache\t73_x_band_global_r3_lane_push_paths.jsonl.gz`
与构造收据
[`audit/t73_x_band_global_r3_lane_push_paths_receipt.json`](audit/t73_x_band_global_r3_lane_push_paths_receipt.json)
包含 3,026 条 negative/positive attaching-lane companions、15,130 个 core 与
push segments、30,260 个 ruled framing triangles。完整 clearance 收据
[`audit/t73_x_band_global_r3_lane_push_clearance.json`](audit/t73_x_band_global_r3_lane_push_clearance.json)
检查 151,300 个 core/push segment pairs（19,673 个精确判定）、136,170 个
ribbon triangle pairs（27,245 个精确判定）及 605,200 个 ribbon/segment pairs
（87,033 个精确判定），额外交点均为 0。跨 band push/push 由共同平移保持，
精确 functional 与 height 余量证明跨 band core/push clearance。verdict 为
`PASS_X_BAND_GLOBAL_R3_LANE_PUSH_AND_RIBBON_CLEARANCE`。该 band 层只剩把 push
endpoints 粘到 stub/transition/middle companions。

全部已映射 splice stubs 现有与 band 侧兼容的 R3 push paths。缓存
`C:\Users\Administrator\.cache\t73_x_m1_stub_r3_push_paths.jsonl.gz`
及收据
[`audit/t73_x_m1_stub_r3_push_paths_receipt.json`](audit/t73_x_m1_stub_r3_push_paths_receipt.json)
包含 6,052 条 push paths、10,582 个 core 与 push segments、21,164 个 ruled
ribbon triangles。同一个已验证 band displacement 对每条 stub segment 横截，
全部 6,052 个共享 stub/band push ports 精确相等。独立重放检查所有坐标/ribbon
及 7,129,377-byte cache SHA。verdict 为
`PASS_X_M1_STUB_R3_PUSH_PATHS_FULL_LOCAL`。source-normal homotopies、全局 stub-push
clearance 与 transition-side push ports 仍为 OPEN。

stub framing 现也完成 source-relative 绑定。收据
[`audit/t73_x_m1_stub_source_normal_homotopy.json`](audit/t73_x_m1_stub_source_normal_homotopy.json)
用 `N(t)=(t*delta,t*delta,2*t*delta,(1-t)*U)` 将 source collar normal
`(0,0,0,U)` 连接到 lifted R3 displacement `(delta,delta,2*delta,0)`。`U` 与
`delta` 均为正，所以两端非零，并在开区间内同时具有正的第一、第四坐标。
独立 verifier 检查 1,001 个有理参数，正锥论证覆盖所有实参数。该同伦统一作用于
6,052 条 paths、10,582 个 segments，relative twist 为 0。verdict 为
`PASS_X_M1_STUB_SOURCE_NORMAL_HOMOTOPY`。

stub core/push paths 也通过第一层全局 clearance。10,582 个 segments 只有四个
精确空间方向类。收据
[`audit/t73_x_m1_stub_core_push_clearance.json`](audit/t73_x_m1_stub_core_push_clearance.json)
对全部 16 个方向配对使用 coplanarity scalar `(u cross v) dot point` 或平行线
向量 `point cross direction` 作精确有理哈希，仅 1,582 个候选存活，全部精确
线段方程无交。push/push clearance 由嵌入 stub cores 的共同平移直接保持。
verdict 为 `PASS_X_M1_STUB_CORE_PUSH_CLEARANCE`。

全部 stub ribbons 也通过完整的 **band-local** 检查。收据
[`audit/t73_x_m1_stub_ribbon_local_clearance.json`](audit/t73_x_m1_stub_ribbon_local_clearance.json)
检查 137,474 个 ribbon-triangle pairs：24,172 个为允许 incidence，其余
113,302 个全部由精确三维 bounds 排除，没有相交 survivor。另检查 296,112 个
ribbon/segment pairs：69,508 个 incidence 与 226,604 个精确 bounds 排除后同样
无 survivor。verdict 为 `PASS_X_M1_STUB_RIBBON_LOCAL_CLEARANCE`。

跨 band clearance 现已由
[`audit/t73_x_m1_stub_ribbon_cross_band_clearance.json`](audit/t73_x_m1_stub_ribbon_cross_band_clearance.json)
闭合，首次完整重放收据保存于
[`audit/t73_x_m1_stub_ribbon_cross_band_verification.json`](audit/t73_x_m1_stub_ribbon_cross_band_verification.json)。
verifier 用 `(p,r)=(x-y,2*x-z)` 商掉共同 sweep 方向 `(1,1,2)`。精确直线哈希
留下 791 个平行跨-band pairs；带严格误差余量的 Shapely/NumPy broad phase
覆盖 4,802,618 个非平行 pairs，其中 4,576,817 个数值上接近的 lift 全部再做
`Fraction` 精确检查。最小精确 clearance 为 `100000*delta`，故 10,582 个
ruled rectangles 全局互不相交。首次或上游改变后执行完整重放：
`python scripts/build_t73_x_m1_stub_ribbon_cross_band_verification_receipt.py --write`；
日常只检查 artifact/cache/builder/verifier 字节绑定时改用 `--check-files`。verdict 为
`PASS_X_M1_STUB_RIBBON_CROSS_BAND_CLEARANCE`。

每个 band 的两个 transition-side framing ports 现也已显式构造。cache
`C:\Users\Administrator\.cache\t73_x_m1_negative_transition_push_paths_v3.jsonl.gz`
包含 3,026 条负高度 transition push paths、各 18,156 个 core/push segments
和 36,312 个 ruled triangles。每条 path 除最后一个切换段外保持已验证 stub
法向；该段通过精确线性 normal homotopy 接到平移后的 m1-annulus product push。
全部 6,052 个 stub/middle core 与 push ports 精确相等，homotopy 对所有实参数
保持横截，relative twist 总和为 0。构造与完整重放收据分别为
[`audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json`](audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json)
和
[`audit/t73_x_m1_negative_transition_push_paths_v3_verification.json`](audit/t73_x_m1_negative_transition_push_paths_v3_verification.json)。
重建与验证命令：

```bash
python3 scripts/build_t73_x_m1_negative_transition_push_paths_v3.py
python3 scripts/build_t73_x_m1_negative_transition_push_paths_v3_verification.py --write
```

verdict 为 `PASS_X_M1_NEGATIVE_TRANSITION_PUSH_PATHS_V3_FULL_LOCAL`。新 transition
ribbons 的全局 clearance 现已独立闭合于
[`audit/t73_x_m1_transition_ribbon_global_clearance.json`](audit/t73_x_m1_transition_ribbon_global_clearance.json)。
证明按真实几何分解：用 GMP 有理算术精确求解 5,865,390 个
transition/transition 与 2,287,656 个 transition/stub 公共位移矩形；对 88 个
含变化法向的 transition/transition triangles 作一般三维精确检查；
transition/band 的扩张三维 AABB 候选为 0。所有 transition/middle 候选均来自
terminal triangle：非端口顶点严格位于 `z<0`，middle ribbons 全在 `z=0`。
verifier 因而将问题归约到 3,026 条 framing-port edges，执行 193,664 次精确
segment/triangle 检查，恰得 6,052 个规定 incidence、无额外交。六个
`t73_x_m1_transition_ribbon_*candidates.json` audit 记录持久 broad/exact
候选流的位置与 SHA。先用
`python3 -m pip install -r requirements-topology.txt` 安装维护中的几何依赖，
再用以下命令重建完整收据：

```bash
python3 scripts/build_t73_x_m1_transition_transition_ribbon_clearance_verification.py --write
python3 scripts/build_t73_x_m1_transition_stub_ribbon_clearance_verification.py --write
python3 scripts/build_t73_x_m1_transition_ribbon_global_clearance.py --write
```

verdict 为 `PASS_X_M1_TRANSITION_RIBBON_GLOBAL_CLEARANCE`。

剩余 stub/band 交叉 clearance 与完整 framed assembly 也已闭合。GMP 收据
[`audit/t73_x_m1_stub_band_ribbon_clearance_verification.json`](audit/t73_x_m1_stub_band_ribbon_clearance_verification.json)
在保留 19,673 个规定端口 incidence 后，精确检查 2,656,225 个非 incidence
公共位移矩形，交点为 0。stub/middle 与 band/middle ribbons 的 core/push 精确
x 区间互不相交。cache
`C:\Users\Administrator\.cache\t73_x_m1_complete_global_r3_framed_replacement_cycles.jsonl.gz`
随后组装全部 1,513 条九段 cycles，包含 92,284 个 core segments、92,284 个
push segments、184,568 个显式 ribbon triangles 和 12,104 个精确 core/push
piece joins。构造与独立重放收据为
[`audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_receipt.json`](audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_receipt.json)
和
[`audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_verification.json`](audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_verification.json)。
重建命令：

```bash
python3 scripts/build_t73_x_m1_stub_band_ribbon_exact_candidates.py
python3 scripts/build_t73_x_m1_stub_band_ribbon_clearance_verification.py --write
python3 scripts/build_t73_x_m1_complete_global_r3_framed_replacement_cycles.py
python3 scripts/build_t73_x_m1_complete_global_r3_framed_replacement_cycles_verification.py --write
```

verdict 为 `PASS_X_M1_COMPLETE_GLOBAL_R3_FRAMED_REPLACEMENT_CYCLES_FULL`。
这闭合了 replacement framing，但尚未与不变的 Johnson/dual 分量合成为最终
七分量 Kirby input。
精确 integration 边界保存于
[`audit/t73_x_m1_complete_framed_outer_interface_gap.json`](audit/t73_x_m1_complete_framed_outer_interface_gap.json)。
其中记录全部 3,026 个相邻 Johnson/dual source-inner、source-port 与 target R3
的 core/push 端点 tuple。3,026 个 core ports 与 push ports 均没有现成相等，
且 core 位移全部不同，所以禁止直接拼接。下一构造必须把每条旧邻接 terminal
segment 替换成 relative framed ambient-collar extension，并验证全局 clearance。
重建命令为
`python3 scripts/audit_t73_x_m1_complete_framed_outer_interface_gap.py --write`。
第一版规范修复以严格 fail-closed 的候选形式保存于
`C:\Users\Administrator\.cache\t73_x_m1_framed_outer_interface_collars.jsonl.gz`。
每条旧 terminal segment 被替换为从已保存 source-inner 到 R3 target port 的
直线：phase 1 固定 source normal 移动旧端点，phase 2 固定最终 core 并将端点
normal 线性同伦到 target normal。局部构造与完整重放收据为
[`audit/t73_x_m1_framed_outer_interface_collars_receipt.json`](audit/t73_x_m1_framed_outer_interface_collars_receipt.json)
和
[`audit/t73_x_m1_framed_outer_interface_collars_verification.json`](audit/t73_x_m1_framed_outer_interface_collars_verification.json)。
全部 3,026 条 core/push paths 也通过 GMP 成对 clearance：2,235,099 个
core/core、2,231,193 个 push/push、4,469,079 个 core/push 精确检查，仅保留
4 个规定 dual-passage inner incidences。见
[`audit/t73_x_m1_outer_collar_core_push_clearance_verification.json`](audit/t73_x_m1_outer_collar_core_push_clearance_verification.json)。
该直线 v1 模型现已在 ribbon 层被否证。精确 artifact
[`audit/t73_x_m1_outer_collar_ribbon_self_clearance.json`](audit/t73_x_m1_outer_collar_ribbon_self_clearance.json)
保存 interfaces 3024/3023（`r_zx:z:edge:4`）两张第二三角形共同包含的内部
有理点；该点明确不在允许的公共 inner edge 上。v1 的 core/push 结论继续保留，
但它的 ribbon 不可使用。

修复后的 v2 cache
`C:\Users\Administrator\.cache\t73_x_m1_framed_outer_interface_collars_v2.jsonl.gz`
先保留每条旧 terminal segment 的前 `10^-6`，再路由到 R3 port，从而恢复共享
dual 顶点处原有的反向 germs。它包含 3,026 个候选、core/push 各 6,052 个
segments 与 12,104 个 ribbon triangles。独立局部重放保存于
[`audit/t73_x_m1_framed_outer_interface_collars_v2_verification.json`](audit/t73_x_m1_framed_outer_interface_collars_v2_verification.json)。
v2 在新的全局 core/push/ribbon、isotopy-trace 与 ambient-support 检查完成前仍为
`CANDIDATE_UNVERIFIED`。重建命令：

```bash
python3 scripts/build_t73_x_m1_framed_outer_interface_collars_v2.py
python3 scripts/build_t73_x_m1_framed_outer_interface_collars_v2_verification.py --write
```

v2 one-skeleton 通过：保存的 GMP 重放执行 2,777,976 个 core/core、2,770,948
个 push/push 和 5,191,079 个 core/push 精确检查，没有额外交点。但 v2 在
ribbon 层同样被否证：rectangle 6051（interface 3025，`r_zx:z:edge:0`）与
rectangle 5411（interface 2705，Johnson connector `c2:between:1280`）相交。
同一 obstruction artifact 保存精确 edge 参数、重心坐标及有理交点。因此 v3
必须采用分离 waypoint route；v1、v2 都不能标为 actual。

该 v3 候选现已构造于
`C:\Users\Administrator\.cache\t73_x_m1_framed_outer_interface_collars_v3.jsonl.gz`。
它保留每个 source germ，使用精确泛函 `F=y-1000033*x+2*z` 与 lift direction
`(0,-2,1)`，并给 interface `i` 分配唯一高度 `10000+i` 和 exterior x 坐标
`50000+2*i`。全部 6,052 个 germ/target functional values 互异，精确最小间隔
为 `1/500000`。cache 包含 3,026 条 collars、core/push 各 18,156 个 segments
和 36,312 个 ribbon triangles。独立局部重放保存于
[`audit/t73_x_m1_framed_outer_interface_collars_v3_verification.json`](audit/t73_x_m1_framed_outer_interface_collars_v3_verification.json)。
全局 core/push/ribbon 与 ambient support 检查完成前仍为
`CANDIDATE_UNVERIFIED`。重建命令：

```bash
python3 scripts/build_t73_x_m1_framed_outer_interface_collars_v3.py
python3 scripts/build_t73_x_m1_framed_outer_interface_collars_v3_verification.py --write
```

v3 第一层全局审计是严格 fail-closed 的语义候选矩阵
[`audit/t73_x_m1_outer_collar_v3_core_candidate_matrix.json`](audit/t73_x_m1_outer_collar_v3_core_candidate_matrix.json)。
向外舍入的三维 R-tree 找到 14,254,960 个 core AABB pairs，并记录六种路由
segments 中全部 11 个非零 type pairs。高负载族现已分配精确降维规则：skew
lifts/rays 使用 constant-F 哈希，exterior pieces 使用唯一高度哈希，只有 source
germs 与 3,026 个同高度 first/last-ray pairs 进入直接 GMP。该 artifact 是完整
工作量证明，不是 clearance PASS。重建命令：
`python3 scripts/build_t73_x_m1_outer_collar_v3_core_candidate_matrix.py --write`。

对应的精确 core verifier 现已闭合于
[`audit/t73_x_m1_outer_collar_v3_core_clearance.json`](audit/t73_x_m1_outer_collar_v3_core_clearance.json)。
14,254,960 个 broad pairs 降为 24,208 个同不变量/direct candidates：其中
15,134 个是规定的相邻 waypoint incidences，只有 9,074 个需要 GMP 线段方程；
全部无交。verdict 为 `PASS_X_M1_OUTER_COLLAR_V3_CORE_CLEARANCE`。push 与
ribbon 矩阵仍为 OPEN，不能从 core 结果自动推出。

独立 push 矩阵与 clearance 现保存于
[`audit/t73_x_m1_outer_collar_v3_push_candidate_matrix.json`](audit/t73_x_m1_outer_collar_v3_push_candidate_matrix.json)
和
[`audit/t73_x_m1_outer_collar_v3_push_clearance.json`](audit/t73_x_m1_outer_collar_v3_push_clearance.json)。
push 矩阵同样有 14,254,960 个 broad pairs。类型 1/2/4 保持 exact
constant-F/height 降维；变化法向 end lifts 分成 3,018 个具有严格互斥 F 区间的
Johnson intervals，以及 8 个直接用 GMP 检查的 dual intervals。verifier 执行
75,618 个精确线段方程，保留 15,134 个 waypoint incidences，未发现交点。
verdict 为 `PASS_X_M1_OUTER_COLLAR_V3_PUSH_CLEARANCE`。core/push 交叉矩阵与
ribbons 仍为 OPEN。

有向 core/push 矩阵现已显式保存于
[`audit/t73_x_m1_outer_collar_v3_core_push_candidate_matrix.json`](audit/t73_x_m1_outer_collar_v3_core_push_candidate_matrix.json)。
它覆盖 22 个非空有向语义类型对中的 28,527,996 个向外舍入 AABB candidates，
并分别记录 core 与 push 侧可用的 constant-F/height 类型。当前仍是 matrix-only：
必须应用变化法向 push end-lift 的区间降维与 dual 直接 GMP survivors，才能声明
mutual clearance PASS。

应用这些降维后，v3 在 ribbon 阶段之前即被否证。精确 artifact
[`audit/t73_x_m1_outer_collar_v3_core_push_clearance.json`](audit/t73_x_m1_outer_collar_v3_core_push_clearance.json)
表明 interface 3022 的 core `last_exterior_ray` 与 push `height_bridge` 在高度
13022 相交，两个精确线段参数都严格位于内部。core 与 push 各自的 PASS 仍然
有效，但二者并集不嵌入。V4 必须偏移 end-exterior waypoint 的高度，使该
r_zx y-normal 拐角成为三维局部星。

V4 现对每条 collar 应用该精确修复：把 end-exterior 顶点从 `H` 提高到
`H+1/2`，并重新计算 y 以保持 target-side F。9,339,105-byte cache
`C:\Users\Administrator\.cache\t73_x_m1_framed_outer_interface_collars_v4.jsonl.gz`
包含 3,026 条 collars、core/push 各 18,156 个 segments 和 36,312 个 ribbon
triangles。独立重放检查全部 3,026 个改变的顶点、18,156 个 normal
transversality 方程，并直接确认 interface 3022 的 v3 原碰撞已消失。见
[`audit/t73_x_m1_framed_outer_interface_collars_v4_verification.json`](audit/t73_x_m1_framed_outer_interface_collars_v4_verification.json)。
在重新构造全局矩阵并完成 clearance 前，V4 仍为 `CANDIDATE_UNVERIFIED`。
新的 one-skeleton 矩阵现已保存于
[`audit/t73_x_m1_outer_collar_v4_one_skeleton_candidate_matrices.json`](audit/t73_x_m1_outer_collar_v4_one_skeleton_candidate_matrices.json)：
core/core 与 push/push 各 14,254,960 个、定向 core/push 28,528,020 个 AABB
candidates，非空语义类型对分别为 11、11、22。半层错位后只有 first exterior
rays 仍为 constant-height；constant-F 类型被单独记录。该 artifact 仍是
matrix-only，不声明 V4 全局 clearance。

v4 core 矩阵现已在
[`audit/t73_x_m1_outer_collar_v4_core_clearance.json`](audit/t73_x_m1_outer_collar_v4_core_clearance.json)
中完整消费。constant-F 类使用精确哈希；三个 staggered corner pairs 改用
same-interface 桶，不再使用无效的 v3 height 论证。14,254,960 个 broad pairs
降为 24,208 个候选，其中 15,134 个为规定 incidence、9,074 个进入 GMP 方程；
交点为 0。verdict 为 `PASS_X_M1_OUTER_COLLAR_V4_CORE_CLEARANCE`。V4 push、
mutual 与 ribbon clearance 仍为 OPEN。

V4 push 与有向 mutual clearance 现已闭合于
[`audit/t73_x_m1_outer_collar_v4_push_clearance.json`](audit/t73_x_m1_outer_collar_v4_push_clearance.json)
和
[`audit/t73_x_m1_outer_collar_v4_core_push_clearance.json`](audit/t73_x_m1_outer_collar_v4_core_push_clearance.json)。
push 使用 75,618 个精确方程；有向 core/push 覆盖全部 22 类并使用 93,818 个
精确方程，交点均为 0。原 v3 冲突对包含在 staggered same-interface GMP family
中。至此 V4 完整 one-skeleton 已嵌入；ribbon 与 ambient-support clearance 仍为
OPEN。

全局线性投影探测记录于
[`audit/t73_affine_s3_projection_probe.json`](audit/t73_affine_s3_projection_probe.json)。
xz/yz 会压扁 dotted edges；三个 regular tilts 至少产生258,453,247个 broad
candidates。下一路线改为从已验证的 central、Hopf 与 corridor chart projections
分块组装 diagram。
完整合并后的 x/m1 结果位于
[`geometry/t73_x_m1_complete_framed_cancellation_image.json`](geometry/t73_x_m1_complete_framed_cancellation_image.json)。
它绑定持久化的 overlap full-verification，并组装五条闭合 atlas cycles：68176条
source core edges 经精确细分成为81812条 target core 与86188条 target push
edges。使用 `python3 scripts/verify_t73_x_m1_complete_framed_cancellation_image.py`
验收；verdict 为 `PASS_COMPLETE_X_M1_FRAMED_CANCELLATION_IMAGE_IN_ATLAS`。
下一步是 y/z dotted-handle conversion，随后实现单一 affine-S³ chart。
穷尽的 y/z 替换表位于
[`geometry/t73_yz_dotted_passage_replacement_map.json`](geometry/t73_yz_dotted_passage_replacement_map.json)。
它在1513条 x-replacement middles 中逐一定位两段 base-18--20 z subpath，并绑定
其余272条 Johnson/bottom/dual passages。因此3590条 source core/push segments
将替换为1785条 framed Hopf segments，转换后计数为 core=80007、push=84383。
使用 `python3 scripts/verify_t73_yz_dotted_passage_replacement_map.py` 验收；
下一门是1785个 framed passage mapping cylinders。
这些 cylinders 保存在
`C:\Users\Administrator\.cache\t73_yz_framed_passage_mapping_cylinders.jsonl.gz`
（约1.87 MB），构造与全量验证收据分别为
[`audit/t73_yz_framed_passage_mapping_cylinders_receipt.json`](audit/t73_yz_framed_passage_mapping_cylinders_receipt.json)
和
[`audit/t73_yz_framed_passage_mapping_cylinders_verification.json`](audit/t73_yz_framed_passage_mapping_cylinders_verification.json)。
全部21540个 tetrahedra 与1785个互不相交 supports 通过。得到的七分量 atlas 为
[`geometry/t73_complete_framed_dotted_atlas.json`](geometry/t73_complete_framed_dotted_atlas.json)：
80007条 framed-core edges、84383条 push edges，以及两条各4边的 dotted polygons。
verdict 为 `PASS_COMPLETE_SEVEN_COMPONENT_FRAMED_DOTTED_ATLAS`；单一 affine-S³
chart 及其完整 PD 仍开放。
三个原先缺坐标的 pre-cancellation dual-cell product ribbons 现已显式保存于
[`geometry/t73_actual_dual_product_ribbons.json`](geometry/t73_actual_dual_product_ribbons.json)。
每条平面 dual boundary 都有通向有理法向 push-off 的8个四边形/16个三角形
annulus；平移后的 spanning disk 证明 source self-linking 为0。使用
`python3 scripts/build_t73_actual_dual_product_ribbons.py --write` 重建，以
`python3 scripts/verify_t73_actual_dual_product_ribbons.py` 验收。经 x-slide
送入 post-cancellation source-native PD 的 ribbon transport 仍开放。
全部1513个 post-x framed replacement cells 已从哈希展开为完整坐标，保存在
WSL cache
`/home/lifesize/.cache/t73_post_x_framed_replacement_cells.jsonl.gz`
（约36.3 MB）；仓库内的紧凑收据为
[`audit/t73_post_x_framed_replacement_cells_receipt.json`](audit/t73_post_x_framed_replacement_cells_receipt.json)。
数据覆盖6052个 band triangles，以及77163个精确 normal/push vertices，包含
每个 replacement 的两条 retained source stubs。
使用 `python3 scripts/build_t73_post_x_framed_replacement_cells.py` 重建；以
`python3 scripts/verify_t73_post_x_framed_replacement_cells.py --full
--check-cache-sha` 流式完整验收。这些 cells 仍位于已验证 gluing 的多个
global/local charts；统一 S³ push-off projection 与五个整数对角 framing 是
下一道门。
局部 dotted-handle replacement 现已在
[`geometry/t73_actual_dotted_s3_passage_cells.json`](geometry/t73_actual_dotted_s3_passage_cells.json)
中坐标化。两个互不相交的有向 dotted rectangles 容纳全部1785条有序 framed
Hopf passages 与3570个 ribbon triangles；3570个精确局部 crossings 复现
source-native SQLite 的 m2 linking `(40,269)`、m3 linking `(189,1271)`，三条
dual components 的 dotted linking 为0。使用
`python3 scripts/build_t73_actual_dotted_s3_passage_cells.py --check` 和
`python3 scripts/verify_t73_actual_dotted_s3_passage_cells.py` 重建/验收。
四个将物理 feet 粘到局部 charts 的 framed marked-strip mapping cylinders
保存在
[`geometry/t73_dotted_s3_foot_collars.json`](geometry/t73_dotted_s3_foot_collars.json)。
它们含24个 tetrahedra，并逐一匹配全部3570个 core endpoints 与3570个 push
endpoints，包括 Figure-2a reflections。使用
`python3 scripts/build_t73_dotted_s3_foot_collars.py --check` 与
`python3 scripts/verify_t73_dotted_s3_foot_collars.py` 重建/验收。剩余 gluing
缺口是中央 connector complement，不再是 marked foot strips。
m2/m3 actual connector 与 product push 的完整精确 crossing ledger 保存在
SQLite cache
`C:\Users\Administrator\.cache\t73_actual_source_connector_push_projection.sqlite`
（约579 MB），收据为
[`audit/t73_actual_source_connector_push_projection_receipt.json`](audit/t73_actual_source_connector_push_projection_receipt.json)。
它从6,936,192个 broad candidates 得到2,528,401个 exact crossings；
connector-only signed sums 分别为 m2=`-345`、m3=`-1206`。m2 的奇数结果以
fail-closed 方式证明开放 connector cells 尚不能定义整数 framing，必须加入
band-splice/collar contributions。重建命令为 `python
scripts/build_t73_actual_source_connector_push_projection.py --output
C:\Users\Administrator\.cache\t73_actual_source_connector_push_projection.sqlite`；
完整验收命令为 `python
scripts/verify_t73_actual_source_connector_push_projection.py --full
--check-database-sha`。

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
