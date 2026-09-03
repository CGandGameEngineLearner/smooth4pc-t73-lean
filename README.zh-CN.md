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
3. 复核边界图见
   [`docs/INDEPENDENT_REVIEW.md`](docs/INDEPENDENT_REVIEW.md)。

## 复现约定

- Lean 工具链：`leanprover/lean4:v4.32.1`
- mathlib 修订：`520045ab14e26149ee970e2e617ca04b09bde5d6`
- Python：3.10 或更高
- 预期公理报告数：`38`
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
