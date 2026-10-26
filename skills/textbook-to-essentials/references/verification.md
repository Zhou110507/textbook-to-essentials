# 证据账本与交付验收

## 两种检查，分别报告

**内容检查**由阅读原书、数学核对与独立求解完成；**结构检查**由脚本完成。脚本通过不能声称知识内容准确无误。缺少某项输入或未读完时，写明限制。

工作目录中维护 `evidence.json`。最小有效结构如下（真实任务替换示例）：

```json
{
  "documents": [{"id": "T", "role": "textbook", "title": "教材名", "page_count": 120}],
  "scope": {"sections": ["1.1"], "exam_evidence": []},
  "coverage": [{
    "section": "1.1", "decision": "keep", "reason": "提供支配方程",
    "source_refs": [{"document": "T", "pdf_pages": [8], "printed_pages": "1"}],
    "output_ids": ["F01"]
  }],
  "items": [{
    "id": "F01", "kind": "formula", "statement": "支配关系的准确表述",
    "source_refs": [{"document": "T", "pdf_pages": [8], "printed_pages": "1", "section": "1.1"}],
    "verification": "verified", "conditions": ["明确适用模型与前提"],
    "symbols": "各符号定义与单位", "output_anchor": "f:F01"
  }],
  "unresolved": []
}
```

字段约定：

- `scope.sections` 按本次任务范围列教材小节，不能在遗漏后悄悄缩小。`coverage` 必须一一覆盖；决策为 `keep/merge/rewrite/defer/omit`。承接内容的前四种需要 `output_ids`；省略需要理由。
- `pdf_pages` 是实际查看的、从 1 开始的 PDF 页序数组；`printed_pages` 原样记录书内页码，可为罗马数字或区间。不以猜测的固定偏移生成未核对的定位。
- Markdown、文本和网页等非PDF文档在 documents 中声明 `format: "markdown"`（或 `"text"/"html"`），无需 page_count；source_refs 使用 `locator` 写文件／页面及节号、行号，不伪造PDF页码。
- `items.kind` 可用 `concept/formula/derivation/method/example/figure`。每个输出项有原文来源；原创算例或作者推导使用 `origin: "original"` 或 `"derived"`，仍附所用定律的来源。
- 公式项的 `conditions` 与 `symbols` 必填。其他项可按需补充条件。`verification` 为 `verified/pending/unreadable`；不能在未核对时填写 verified。
- `exam_evidence` 仅记真实考纲／试卷定位，不写估计频次。`unresolved` 保存缺页、版本冲突、疑似勘误和无法读取处；未解决时不得称作最终无缺口交付。
- 用户要求逐页阅读时另存 `reading-log.csv`，列 `document,pdf_page,printed_page,status,note`。推荐状态 `read/needs-visual-check/unreadable/non-content`；OCR完成不是 read。脚本只验证登记是否完整，无法证明阅读真实性。

## 内容验收

- 范围内全部小节及实际相关例题、思考题、习题已读；被合并或删去的内容可解释。
- 所有核心结论有来源；没有将教材外知识或考试预测混成原书要求。
- 公式、符号和限制条件逐项回查；图、表、推导的信息没有被压缩掉。
- 每种独立解题路径有可以迁移的方法；算例已复算，结果通过适当检查。
- 一个代表点的数值通过不能代替边界检查。对会改变公式结构的退化参数、零输入、方向反转、等状态等关键分支，按内容需要做符号、极限或反例核验。
- 新增加的解释、推导或勘误与原书观点有明确区分。
- 正文无空栏目、重复小结、无效口号和为压缩而丢失的前提。

## 制版验收

可编辑 `.tex` 与实际编译 `.pdf` 一致；编译日志无错误、缺字、未解析引用和未解决的严重溢出。渲染 PDF 全部页面，检查公式下标、表格换页、图的文字、留白与页码。多文件工程应包含所有本地依赖。不能生成 PDF 或尚有无法确认的内容时，交付源文件并明确状态，不宣称已完成全部验收。
