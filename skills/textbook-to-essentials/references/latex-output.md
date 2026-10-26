# LaTeX 输出

默认使用 `ctexart`、A4、11pt、约 2 cm 页边距，单栏，黑白可打印。中文用 XeLaTeX（模板使用 TeX Live 的 Fandol 字体），Tectonic 也可；其他语言按需求替换文类。避免依赖某一操作系统才有的中文字体。

从 `assets/main.tex` 复制，替换标题、来源、章节及示例。模板是可编译的排版起点，不是必需栏目清单。短精要不必目录／封面；全书精要适合目录和节号。统一定义符号，公式用 `equation/align`，编号仅用于正文需要引用的公式。条件紧贴公式；语义上不同的关系不能为省空间塞在一个无解释的长等式内。

长表使用 `longtable` 或分表，普通宽表用 `tabularx` 自动换行。必要图以 TikZ、PGFPlots 或矢量文件重画；状态点、箭头、图例和比较基准齐全。不能凭示意图伪造数据刻度；引用的数据图注明出处。

脚本用法：

```text
python scripts/build_pdf.py main.tex
python scripts/build_pdf.py main.tex --engine xelatex
python scripts/build_pdf.py main.tex --engine tectonic --compiler /path/to/tectonic
```

编译缓存放入源文件旁的 `build/`，成功的 PDF 复制到源文件旁。自动选择顺序：latexmk＋XeLaTeX → XeLaTeX → Tectonic；第一次 Tectonic 编译可能需要下载 TeX 资源。脚本不自动安装引擎。

无 Python 时可直接运行：

```text
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

或在 Overleaf 选 XeLaTeX 编译。内置 LaTeX 编译器可验证并预览，但最终交付仍应有实际导出的 PDF。

构建通过后仍须检查排版：渲染全部页面，修复缺字、重叠、过长公式和截断的表图。`build_pdf.py` 报告日志中的警告，并对缺字、引用未解析与横向溢出返回失败；日志检查不能代替看页面。
