# textbook-to-essentials

把理工科教材整理为准确、精练、可追溯的学习精要，输出可编辑的 **LaTeX** 与实际编译的 **PDF**。

本 skill 通过逐页对照《工程热力学》第2版（2011）与《工程热力学精要与题解》（2012）提炼编辑规则。两份扫描件共571页，覆盖12章正文、思考题与习题／题解，另含前置页、附录与归档信息。逐页阅读不代表逐个数字都经过重算，也不代表对所有学科已完成验证。

[下载技能包](dist/textbook-to-essentials.zip) · [查看示范PDF](examples/first-law.pdf) · [查看模板PDF](skills/textbook-to-essentials/assets/main.pdf)

## 用法

将 [skills/textbook-to-essentials](skills/textbook-to-essentials) 整个文件夹放入你的技能目录，例如 `~/.codex/skills/`。该目录内的 `SKILL.md` 是入口；不需要复制研究报告或测试文件才能使用。

示例请求：

> 请使用 $textbook-to-essentials，将这本《电路》教材第1—4章整理为本科复习精要。参考附带精要的内容取舍方法，保留公式条件、概念辨析和可迁移的典型题型。输出可编译的LaTeX、PDF和来源账本。未提供真题，请不要标注考试频次。

只提供教材也能使用；提供考纲或真题后可据真实证据调整优先级。默认提炼代表方法，用户明确要求时才制作配套全题解。

## 关键规则

- 按学习能力取舍，保留概念、条件、支配关系、必要推理与方法分叉。
- 精要正文、辨析、题解、附表整体对齐；移入题解不等于删除。
- 公式条件贴近公式；总式与特例、比较基准、数据与参考态都需明确。
- 教材与优质精要均可有错误，须回看原图并独立检查；不同版本题干与答案不得混用。
- 不固定压缩比例、页数或每章题量；用逐节覆盖与去重控制简练。
- 不凭教材篇幅猜测考试高频，不以OCR或结构校验代替内容核验。

## 内容与构建

| 路径 | 用途 |
|---|---|
| `skills/textbook-to-essentials/SKILL.md` | 技能入口与核心决策 |
| `skills/textbook-to-essentials/references/` | 成对分析、学科适配、证据及制版标准 |
| `skills/textbook-to-essentials/assets/main.tex` | 独立可编译的中文模板，含公式、表格和TikZ示例 |
| `skills/textbook-to-essentials/scripts/` | PDF构建与证据账本结构检查，Python标准库实现 |
| `examples/first-law.tex` | 原创热力学节选示范及3道已复算算例 |
| `research/pair-study.md` | 12章编辑规则与来源异常的研究概述 |
| `research/reading-log.csv` | 571页阅读覆盖记录；没有书籍全文或页图 |
| `tests/` | 工具回归测试与原创RC跨学科测试材料 |

安装 Python 3.9+，以及 XeLaTeX（可配 latexmk）或 Tectonic。脚本不自动安装编译器。

```sh
python skills/textbook-to-essentials/scripts/build_pdf.py examples/first-law.tex
python skills/textbook-to-essentials/scripts/check_ledger.py examples/first-law-evidence.json
python -m unittest discover -s tests -v
```

无本地引擎时，将 `.tex` 上传 Overleaf，选择 XeLaTeX。中文模板使用 Fandol 字体；首次 Tectonic 编译可能下载字体和宏包。编译成功后还需看全部PDF页面，检查缺字、公式和表图。内置预览、未编译源文件或其他排版软件的PDF不能冒充LaTeX导出结果。

## 验证与来源边界

已做12章逐页对照、RC电路内容前向测试、原创热力学示范独立复算、工具回归测试，以及模板与示范的真实LaTeX编译／逐页视觉检查；详见 [validation.md](research/validation.md)。这些检查不能保证任意教材的未来输出绝对无误，因此skill保留逐项来源、条件审计与未决问题登记。

仓库只含独立编写的规则、分析、模板、代码及原创测试材料，不分发原书、扫描页、OCR全文或成套原书题解。原书题名仅用于交代方法校准来源。规则的通用性来自对象、条件、依赖、方法及验证；它不是一套热力学专用公式库。
