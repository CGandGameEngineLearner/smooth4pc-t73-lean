# T73 数学漏洞修补大纲

## S：先行纸面审计

目标是证明实际三维柄余等化子的两条全源恒等式

\[
\ell\circ\mu_{A_j}(-\otimes X)=\ell,\qquad
\ell\circ\mu_{A_j}(-\otimes 1)=0
\]

对三个实际附着球 \(A_j\) 都成立。

需要依次建立四个引理：

1. **相对球系引理。** 用 HJ Lemma 5.7，并在切开后的 spotted
   ball 中使用 Lemma 5.5，把 boundary slide 写成外壳中的有限 sphere
   slides；这只证明实际附着系统可换成固定在内球外的标准球系。

2. **MWW 半球识别引理。** 用 MWW Theorem 3.7 的两半球
   \(\Delta^+,\Delta^-\) 和 Theorem 3.10 的二手柄 cut surface，明确写出
   \(\Delta^+\) 的 counit 行及 \(\Delta^-\) 的本质球局部模作用
   \(\mu_{A_j}\)。这一步只识别映射，不计算探测器对 \(\mu_{A_j}\) 的值。

3. **实际 endpoint 交换引理（关键缺口）。** 必须构造实际
   \(W_2\) cut-complex 到 BPW/BHPW endpoint complex 的自然方块，使
   \(\mu_{A_j}\) 的实际 image 等于“旧探测器因子张量一个可计算的
   genus-zero/core-counit 因子”。仅有“球面和 \(B\) 不交”、幺半性或
   \(h=0\) 的 Frobenius 公式不推出此方块；本引理目前没有公开数据或
   纸面证明。

4. **余等化子结论。** 只有在第 3 引理给出后，才能将第 2 引理的两行
   合成到 \(\ell\)，得到六个恒等式并应用 MWW Theorem 3.7。
   因此不能直接写“(32) proves (31)”。

## 判定

在第 3 引理尚未补出前，S 必须保持 \`OPEN\`；P3/E11 及主定理也必须保持
条件。任何只增加 Frobenius 归纳、证书哈希或标准球系移动表的改动，
都不能替代第 3 引理。

## P0/C 同步审计

- P0a：Johnson lift 与 AR handlebody 的实际相对微分同胚；
- P0b：两次完整 framed Kirby \(1/2\)-cancellation，且 \(\varepsilon=0\)；
- P0c：乘积法向与 MWW/lasagna framing 的同一性；
- P0d：93-bit 搜索只确定替代表示中的几何辫词，不能冒充历史 PD；
- C1：实际 MWW \(\KhR_2\) 系数双模与 endpoint quantum trace 的自然同构；
- C2：实际所有 cable level 的 pure-braid \(I+O(h)\) 展开；
- C3：C 的 \(B\) 外自然性不得被用于推出 S 的本质球作用。
