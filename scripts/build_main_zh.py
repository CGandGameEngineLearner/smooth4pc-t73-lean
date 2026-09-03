#!/usr/bin/env python3
"""Build main-zh.tex from main.tex by swapping \\input paths and ctex preamble."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "spc4-t73-candidate"
MAIN = PAPER / "main.tex"
OUT = PAPER / "main-zh.tex"

INPUT_MAP = {
    r"\input{sec-published-results}": r"\input{sec-published-results-zh}",
    r"\input{sec-finite-details}": r"\input{sec-finite-details-zh}",
    r"\input{sec-retired-assumptions}": r"\input{sec-retired-assumptions-zh}",
    r"\input{sec-retired-routes}": r"\input{sec-retired-routes-zh}",
    r"\input{sec-appendices-extra}": r"\input{sec-appendices-extra-zh}",
}

PREAMBLE_OLD = r"""\documentclass[11pt]{amsart}

\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{amsmath,amssymb,mathtools}"""

PREAMBLE_NEW = r"""\documentclass[11pt]{amsart}

\usepackage[UTF8,scheme=plain,fontset=fandol]{ctex}
\usepackage{microtype}
\usepackage{amsmath,amssymb,mathtools}"""

TITLE_OLD = r"""\title[A conditional trace-73 obstruction]
{A conditional skein-lasagna obstruction for a trace-73\\
Cappell--Shaneson sphere}

\author{Anonymous repository audit}
\address{Draft prepared from the public trace-73 repository}
\email{Author information to be supplied before submission}
\date{September 3, 2026}

\subjclass[2020]{Primary 57K40, 57R55; Secondary 57K18, 68V20}
\keywords{smooth Poincare conjecture, Cappell--Shaneson sphere,
skein lasagna module, Khovanov homology, formal verification}"""

TITLE_NEW = r"""\title[trace-73 条件性阻碍]
{trace-73 Cappell--Shaneson 球面的\\
条件 skein-lasagna 阻碍}

\author{匿名仓库审计}
\address{由公开 trace-73 仓库整理的中文对照稿}
\email{投稿前补充作者信息}
\date{2026 年 9 月 3 日}

\subjclass[2020]{主 57K40, 57R55；次 57K18, 68V20}
\keywords{光滑 Poincaré 猜想, Cappell--Shaneson 球面,
skein lasagna 模, Khovanov 同调, 形式化验证}"""

THEOREM_OLD = r"""\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{hypothesis}[theorem]{Hypothesis}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}
\newtheorem{externalresult}[theorem]{External Result}"""

THEOREM_NEW = r"""\newtheorem{theorem}{定理}[section]
\newtheorem{proposition}[theorem]{命题}
\newtheorem{lemma}[theorem]{引理}
\newtheorem{corollary}[theorem]{推论}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{定义}
\newtheorem{hypothesis}[theorem]{假设}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{注}
\newtheorem{externalresult}[theorem]{外部结果}"""

STATUS_OLD = r"""\newcommand{\Open}{\textnormal{\textsc{Open}}}
\newcommand{\Partial}{\textnormal{\textsc{Partial}}}
\newcommand{\Discharged}{\textnormal{\textsc{Discharged}}}
\newcommand{\Unused}{\textnormal{\textsc{Unused}}}"""

STATUS_NEW = r"""\newcommand{\Open}{\textbf{开放}}
\newcommand{\Partial}{\textbf{部分}}
\newcommand{\Discharged}{\textbf{已证}}
\newcommand{\Unused}{\textbf{未用}}"""

HYPersetup_OLD = 'pdftitle={A conditional trace-73 Cappell--Shaneson skein-lasagna obstruction}'
HYPersetup_NEW = 'pdftitle={trace-73 Cappell--Shaneson 条件 skein-lasagna 阻碍（中文版）}'


def build() -> None:
    text = MAIN.read_text(encoding="utf-8")
    text = text.replace(PREAMBLE_OLD, PREAMBLE_NEW)
    text = text.replace(TITLE_OLD, TITLE_NEW)
    text = text.replace(THEOREM_OLD, THEOREM_NEW)
    text = text.replace(STATUS_OLD, STATUS_NEW)
    text = text.replace(HYPersetup_OLD, HYPersetup_NEW)
    for old, new in INPUT_MAP.items():
        text = text.replace(old, new)
    OUT.write_text(text, encoding="utf-8")
    print(f"WROTE {OUT} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    build()
