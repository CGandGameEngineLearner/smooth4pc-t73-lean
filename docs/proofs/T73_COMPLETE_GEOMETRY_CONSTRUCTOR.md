# T73 selected-C 完整几何构造器与 fail-closed 清单

## 1. 目的

顶层脚本 `scripts/build_t73_complete_geometry_bundle.py` 统一编排并保存四个已经分离的几何产物：

1. `geometry/t73_selected_source_exterior.json`：四条 cable 周期、四个插入球面上的完整端点 incidence、630 条外部有框区间；
2. `geometry/t73_selected_canopolis_normal_form.json`：schema v2 的双 representable **抽象目标模板**；
3. `geometry/t73_single_hom_defect_target.json`：显式的 `P86 -> P88`、86 条贯穿弧加一个 cup 的 single-Hom 目标；
4. `audit/t73_defect_aware_currying.json`：168 条 correct-side 与 8 条 wrong-side active interval 的分类审计。

构造结果由版本化清单
`geometry/t73_complete_geometry_bundle_manifest.v1.json` 汇总；其机器 schema 是
`data/T73_COMPLETE_GEOMETRY_BUNDLE_MANIFEST.schema.json`。

扩展清单 `geometry/t73_complete_geometry_bundle_manifest.v2.json` 还纳入
defect-coend 类型图、AR 源坐标 atlas、七分量 PD 真例与开源软件收据，以及
TetGen 十-ribbon 前缀。它把 `VERIFIED_TYPING_ONLY`、
`VERIFIED_PREFIX_ONLY`、`VERIFIED_FIXTURE_ONLY` 与真正的 T73 完成状态分开。

## 2. 可复现命令

完整重建、保存、运行精确的有理 PL 两两不交检验并重写清单：

```bash
python3 scripts/build_t73_complete_geometry_bundle.py --write
```

从所有底层构造器重新计算，但不写文件，并逐字节比较已提交产物：

```bash
python3 scripts/build_t73_complete_geometry_bundle.py --check
```

只快速核验现有文件的 canonical JSON、内容 SHA256、内嵌 payload SHA256、几何计数、依赖 SHA 和 fail-closed 状态：

```bash
python3 scripts/build_t73_complete_geometry_bundle.py --check-files
```

`--skip-pairwise` 只供调试。使用它时，源外部空间和 v2 目标的
`reconstruction_status` 被强制保持为 `OPEN`，不会因为跳过昂贵检验而得到
`VERIFIED`。

扩展清单的重建与检查为：

```bash
python3 scripts/build_t73_complete_geometry_bundle_v2.py --write
python3 scripts/build_t73_complete_geometry_bundle_v2.py --check
```

## 3. 已保存的完整组合数据

当前版本固定并核验下列计数：

- 源外部空间：四条 cable 周期，四个 cyclic seams；`Y_minus`、`Y_plus` 各 88 个端点，`Z_minus`、`Z_plus` 各 542 个端点；合计 1260 个端点、630 条有框外部区间及 2520 个显式 ruled-ribbon 三角形，并有严格全局宽度/间距证书。
- v2 抽象目标：两个不交 closure balls；每个 closure 有 88 条 active `Y--Z` 弧和 227 条 boundary-parallel `Z--Z` 弧；合计 630 条弧，四个插入球的端点数为 `88/542/542/88`。
- single-Hom 目标：86 个底端点、88 个顶端点、86 条贯穿弧和一个 cup。
- defect incidence：176 条 Y-incident active intervals 中 168 条方向兼容、8 条 wrong-side；若仅做端点重配，至少需要四次独立 reconnection。

清单逐文件记录相对路径、schema、生成器、校验器、文件字节 SHA256、内嵌 payload SHA256（若有）、字节数和上述几何计数。

## 4. 两层状态，禁止偷换概念

每个清单条目有三项状态：

- `reconstruction_status`：底层构造器能否逐字节重建，并通过相应的精确组合/PL 校验；
- `completion_status`：该文件是否已经补齐其参与整条论文证明所需的几何映射；
- `status`：面向完整构造链的有效状态。

当前文件可以有 `reconstruction_status = VERIFIED`，但四项的
`completion_status` 和 `status` 均必须是 `OPEN`。schema v1 直接把后两项冻结为
`OPEN`；若将它们手改成 `VERIFIED`，即使重新计算清单自身的 payload SHA，测试也必须拒绝。

这一区分至关重要：一个坐标化目标模板构造成功，不等于已经构造出从实际 AR
系数外部空间到该模板的相对环境同痕或 cobordism。

## 5. 当前第一道开放门

清单给出的第一道开放门是：从全部 630 条已保存源区间出发，构造并核验一个相对
source-to-target cobordism/currying map，并明确处理八条 wrong-side intervals。
尚缺的具体数据包括：

1. 1084 个 Z-sphere 端点在任意 `C_271` 插入下的 coend gluing cells；
2. 八条例外的左/右 pivotal mate 选择、Blanchet 符号和 Euler/量子次数；
3. 将 630 条源区间映到 86 条贯穿弧、一个 cup 与所有内部闭分量的逐条 incidence；
4. 上述 map 相对四个插入球边界的完整 movie/cell 证书。

在这些对象实际出现并有独立校验器之前，顶层构造器不会把任何 `OPEN` 提升为
`VERIFIED`。

## 6. 与开源拓扑软件的接口路线

本清单适合作为后续 Spherogram/SnapPy/Regina 适配器的稳定输入索引，但它不会伪造
这些软件所要求的标准 PD/Gauss crossing order、self-crossings、整数 surgery framing
或三维三角剖分。当完整的 framed-link/handlebody 输入补齐后，应把软件生成的
complement、外围曲线、填充和识别证书作为新的独立 artifact 加入下一版 manifest；
v1 清单的 `OPEN` 状态不得仅凭软件能够导入文件而关闭。

当前负面适配结果已单独保存为
`audit/t73_pd_spherogram_adapter_report.json`。它精确列出标准 PD、component
successor、自交、`r_zx` 嵌入、dotted 分量和整数 framing 等缺项。

## 7. v2 的四个实际完成门

v2 清单严格列出四个仍缺的 T73 witness：

1. 实际 defect-aware coend 的 R1 representability 或 R2 connected-bar
   chain equivalence；
2. 实际完整 Kirby 输入，即统一 cut/surgery dotted-circle presentation、
   两次 band splicing、dotted meridians 与五个 push-offs；
3. 全部 630 ribbons 的共同四面体 frame；
4. actual AR coefficient exterior 到所保存 canonical source 的相对绑定。

前缀、真例和类型图均不能关闭这些门。因此 v2 的 bundle status 仍为
`OPEN`，但每一条已完成的有限构造都有独立哈希和可执行验收。
