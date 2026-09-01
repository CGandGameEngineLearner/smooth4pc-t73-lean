# Smooth4PC T73 反例与证伪材料包

[English](README.md)

本仓库提出一份**等待独立外部复核的光滑四维庞加莱猜想证伪**：候选反例
Cappell--Shaneson 流形 `X(41,189,73)` 是一个与标准 `S^4` 不微分同胚的
同伦四维球。

候选证明构造了一个量子次数为 `494` 的类。它的三次除法检测量为
`-59072`，而标准四维球模在该次数上为零。有限计算与抽象商空间推理已经
由 Lean 检查；候选对象与真实几何之间的识别，以及引用的拓扑定理，仍被
明确列作外部输入，没有藏进形式化代码。

因此，Lean 编译成功所验证的是仓库中编码的蕴涵链，并不自动等于所有几何
输入都已经形式化。精确边界见
[`Smooth4PC/T73External.lean`](Smooth4PC/T73External.lean)。

## 从哪里开始

1. 阅读 [`docs/INDEPENDENT_REVIEW.md`](docs/INDEPENDENT_REVIEW.md)：三步证明链、
   公开文献依赖与复核边界。
2. 按 [`REPRODUCING.md`](REPRODUCING.md) 从全新 clone 编译、检查全部公理报告，
   并独立重算检测量。
3. 从
   [`docs/proofs/T73_COUNTEREXAMPLE_MATERIALS_INDEX.md`](docs/proofs/T73_COUNTEREXAMPLE_MATERIALS_INDEX.md)
   进入完整证明与证据树。

证明正文为
[`docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md`](docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md)。

## 复现约定

- Lean 工具链：`leanprover/lean4:v4.32.1`
- mathlib 版本：`520045ab14e26149ee970e2e617ca04b09bde5d6`
- Python：3.10 或更高
- 预期 `#print axioms` 报告：`38` 条
- 报告中允许出现的公理：`propext`、`Classical.choice`、`Quot.sound`
- `sorryAx`：不得出现
- 检测量预期值：`-59072`

提交的 `lake-manifest.json` 锁定全部 Lean 依赖。编译产物、本机依赖副本与
历史临时探针不属于发布源码。

## 范围声明

这是公开复核材料，不是声称该结果已经得到同行认可。最有价值的对抗复核，
是直接攻击独立复核文档所列的候选几何绑定，而不只是再次运行已经核过的
整数算术。

## 为什么先在 GitHub 发布

先选择 GitHub，是为了让材料尽快公开、便于访问，并让任何人都能直接复现
Lean 与精确计算；这并不是用代码仓库代替学术审查。我的 arXiv 投稿记录目前
在计算机科学领域，我未必已经具备向相应数学分类投稿所需的 endorsement。
因此，我先把完整论证、Lean 源码、精确输入和从零复现步骤公开出来。如果这项
工作得到实质性的数学复核与帮助，我会整理正式预印本，并通过合适的学术渠道
投稿。

## 许可证

本仓库采用 [MIT License](LICENSE) 发布。
