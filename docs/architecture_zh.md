# bibmark — 代码逻辑文档

## 整体流程

你调用 `generate_citations()` 之后，代码做了四件事，按顺序串联：

```plain
publications.bib
    ↓  parser.py    — 读取和解析
    ↓  core.py      — 验证字段，打印 warning
    ↓  formatter.py — 把数据格式化成引用文本
    ↓  writer.py    — 把文本写进文件
    ↓
citations.docx / .md / .tex
```

这个串联逻辑在 `core.py` 里，`__init__.py` 只是把 `generate_citations` 暴露给外部用。

---

## 第一步：`parser.py` — 读取 .bib 文件

### `parse_bib(path, keys)`

用 bibtexparser v2 读整个 `.bib` 文件，然后按 `keys` 列表的顺序返回对应的 entry。
这样输出顺序由调用脚本里的 `cite_keys` 控制，而不是 `.bib` 文件里的顺序。

```python
entries_by_key = {e.key: e for e in library.entries}
# 按 keys 顺序取出，找不到的 key 打印 warning 并跳过
```

每个 entry 有一个 `fields_dict`，是字段名到值的字典，比如：

```python
entry.fields_dict["author"].value  # → "Wenrui Wu and San Zhang"
entry.fields_dict["journal"].value # → "Cancer Cell"
entry.fields_dict["bibmark"].value # → "first: {1, 2}, corresponding: {-1}"
```

### `parse_bibmark_field(value, cite_key, annotation_map)`

把 bibmark 字段的字符串解析成结构化的字典：

```plain
"first: {1, 2}, corresponding: {-3, -2, -1}"
        ↓
{"first": [1, 2], "corresponding": [-3, -2, -1]}
```

用正则表达式匹配 `key: {数字, 数字}` 这个模式，支持负数索引。如果 key 不在
`annotation_map` 里（比如你写了个 `typo: {1}`），会打印 warning。

---

## 第二步：`core.py` — 分组与验证

`generate_citations()` 在这里把 `cite_keys` 统一转成 `sections`，再交给 writer：

```python
# list 输入：包成单一 section，heading 为 None
sections = [(None, entries)]

# dict 输入：展平所有 key 统一解析，再按分组重组
all_keys = [k for keys in cite_keys.values() for k in keys]
all_entries = parse_bib(bib_file, all_keys)
entries_by_key = {e.key: e for e in all_entries}
sections = [
    (heading, [entries_by_key[k] for k in keys if k in entries_by_key])
    for heading, keys in cite_keys.items()
]
```

### `validate_entry(entry)`（定义在 `formatter.py`）

在格式化之前，`core.py` 对每个 entry 调用一次 `validate_entry()`，集中打印所有
warning，避免重复：

- 缺少必填字段（`author`、`title`、`journal`、`year`、`volume`、`pages`、`doi`）→ warning，输出中以 `Unknown` 占位
- 缺少 `number` 字段 → 仅当 `volume` 同时缺失时才有影响：`volume` 存在时静默省略 `number`；`volume` 缺失时输出 `Unknown(Unknown)`
- author 列表以 `others` 结尾（截断列表）→ warning

---

## 第三步：`formatter.py` — 格式化引用

这是最复杂的一步。核心思想是**先不管输出格式，把引用拆成一个个带格式标记的
"片段"（Segment），最后再按目标格式渲染**。

### Segment 是什么

一个 Segment 就是一个小字典：

```python
{"text": "Wenrui Wu", "bold": True, "italic": False, "superscript": False, "underline": True, "url": ""}
```

- `url` 字段用于 DOI 超链接，在 Markdown 渲染时生效（Word 和 LaTeX 暂不渲染链接）
- `underline` 字段用于下划线，目前用于高亮 `my_name`

整个引用是一个 Segment 列表，例如：

```python
[
  {"text": "Mingchuan Huang", "bold": False, "italic": False, "superscript": False, "url": ""},
  {"text": "#",               "bold": False, "italic": False, "superscript": True,  "url": ""},
  {"text": ", ",              "bold": False, "italic": False, "superscript": False, "url": ""},
  {"text": "Wenrui Wu",       "bold": True,  "italic": False, "superscript": False, "url": ""},  # my_name
  {"text": "#",               "bold": False, "italic": False, "superscript": True,  "url": ""},
  # ...
  {"text": "Cancer Cell",     "bold": False, "italic": True,  "superscript": False, "url": ""},
  {"text": ", 41(3):123–145, 2023, ", ...},
  {"text": "doi:10.1234/abc", "bold": False, "italic": False, "superscript": False, "url": "https://doi.org/10.1234/abc"},
]
```

### 辅助函数

| 函数 | 作用 |
|------|------|
| `_strip_braces(value)` | 去除 LaTeX 保护花括号，如 `{{China}}` → `China` |
| `_get_field(entry, key, cite_key)` | 取字段值（已去花括号），缺少时返回 `"Unknown"` |
| `_format_pages(pages)` | 把 `--` 替换为 en-dash `–` |
| `_split_authors(author_str)` | 按 ` and ` 切开作者列表 |
| `_normalize_author(author)` | `"Wu, Wenrui"` → `"Wenrui Wu"` |

### `format_citation()` 做了什么

1. 取出 author 字符串，切开并规范化
2. 解析 bibmark 字段，建立每个作者的注释符号列表
   - 正索引：`1` = 第一作者，`2` = 第二作者，依此类推
   - 负索引：`-1` = 最后一位，`-2` = 倒数第二位，方便标注通讯作者
3. 遍历作者列表，逐个生成 Segment：
   - 如果是 `my_name`，加 `bold=True`、`underline=True`
   - 如果有注释符号，根据 `superscript` 决定是否加 `superscript=True`
   - 最后一个作者前面加 `", and "`，其余加 `", "`
4. 拼上 title、journal（bold + italic）、volume/number/pages/year
5. DOI 单独作为一个带 `url` 的 Segment
6. 根据 `output_format` 渲染：
   - `"word"` → 直接返回 Segment 列表（writer.py 自己处理样式）
   - `"markdown"` → `_render_segments_md()`：bold → `**...**`，italic → `*...*`，superscript → `<sup>...</sup>`（`*`/`_` 转义为 HTML entity 避免被解析为斜体），underline → `<ins>...</ins>`（GitHub 白名单不含 `<u>`），url → `[text](url)`；DOI 拆成两个 segment：`doi:` 纯文字 + DOI 号码带 url
   - `"latex"` → `_render_segments_tex()`：bold → `\textbf{}`，italic → `\textit{}`，superscript → `$^{}$`，underline → `\underline{}`

---

## 第四步：`writer.py` — 写出文件

三个 `write_*` 函数的入参都是 `sections: list[tuple[str | None, list]]`，
结构为 `(heading, citations)` 的列表。`core.py` 保证：

- `cite_keys` 是 list 时：`sections = [(None, all_citations)]`
- `cite_keys` 是 dict 时：`sections = [("2025", [...]), ("2024", [...]), ...]`

写出逻辑：先写一级 Bibliography 标题，然后遍历 sections——
如果 heading 不为 `None`，写二级标题；再逐条写引用，并在每条前加序号（`1.`、`2.`……），
序号在每个 section 内独立从 1 开始。

| 函数 | 一级标题 | 二级标题（分组时） |
|------|----------|--------------------|
| `write_docx` | `Heading 1` | `Heading 2` |
| `write_md` | `# Bibliography` | `## <heading>` |
| `write_tex` | `\section*{Bibliography}` | `\subsection*{<heading>}` |

Word 格式稍微特殊：序号单独作为一个普通 Run 插入段落开头，之后逐个 Segment 创建
Run 并设置 `.bold`、`.italic`、`.font.superscript`。

---

## 为什么要用 Segment 这种设计？

直接理解可能会觉得绕，但它解决了一个实际问题：

> 同一份数据，要输出三种完全不同的格式（Word 对象、Markdown 字符串、LaTeX 字符串）。

如果每种格式单独写一遍逻辑，"作者排序、找 my_name、处理 bibmark 注释"这些逻辑就要
重复三遍。用 Segment 的好处是：**构建逻辑只写一次，渲染逻辑各写各的**。这是一种
常见的"中间表示"（IR，Intermediate Representation）模式。

---

## 文件结构总览

```plain
src/bibmark/
├── __init__.py   对外只暴露 generate_citations
├── core.py       串联 parser → validate → formatter → writer 的 pipeline
├── parser.py     读 .bib 文件，按 cite_keys 顺序返回 entries
├── formatter.py  validate_entry 验证字段；构建 Segment 列表并渲染
└── writer.py     把格式化结果写进 .docx/.md/.tex 文件
```
