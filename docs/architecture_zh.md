# bibmark — 代码逻辑文档

## 整体流程

你调用 `generate_citations()` 之后，代码做了三件事，按顺序串联：

```plain
publications.bib
    ↓  parser.py    — 读取和解析
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
entry.fields_dict["bibmark"].value # → "first: {1, 2}, corresponding: {3}"
```

### `parse_bibmark_field(value, cite_key, annotation_map)`

把 bibmark 字段的字符串解析成结构化的字典：

```plain
"first: {1, 2}, corresponding: {3, 4}"
        ↓
{"first": [1, 2], "corresponding": [3, 4]}
```

用正则表达式匹配 `key: {数字, 数字}` 这个模式。如果 key 不在 `annotation_map`
里（比如你写了个 `typo: {1}`），会打印 warning。

---

## 第二步：`formatter.py` — 格式化引用

这是最复杂的一步。核心思想是**先不管输出格式，把引用拆成一个个带格式标记的
"片段"（Segment），最后再按目标格式渲染**。

### Segment 是什么

一个 Segment 就是一个小字典：

```python
{"text": "Wenrui Wu", "bold": True, "italic": False, "superscript": False}
```

整个引用是一个 Segment 列表，例如：

```python
[
  {"text": "Mingchuan Huang", "bold": False, "italic": False, "superscript": False},
  {"text": "#",               "bold": False, "italic": False, "superscript": True },
  {"text": ", ",              "bold": False, "italic": False, "superscript": False},
  {"text": "Wenrui Wu",       "bold": True,  "italic": False, "superscript": False},  # my_name
  {"text": "#",               "bold": False, "italic": False, "superscript": True },
  # ...
  {"text": "Cancer Cell",     "bold": False, "italic": True,  "superscript": False},
  {"text": ", 41(3):123–145, 2023, doi:...", ...},
]
```

### `format_citation()` 做了什么

1. 从 entry 里取出 author 字符串，用 `_split_authors` 按 ` and ` 切开
2. 用 `_normalize_author` 把 `"Wu, Wenrui"` 变成 `"Wenrui Wu"`
3. 解析 bibmark 字段，知道哪些作者需要加注释符号（`#`、`*` 等）
4. 遍历作者列表，逐个生成 Segment，同时：
   - 如果是 `my_name`，加 `bold=True`
   - 如果有注释符号，根据 `superscript` 决定是否加 `superscript=True`
   - 最后一个作者前面加 `", and "`，其余加 `", "`
5. 拼上 title、journal（italic）、volume/number/pages/year/doi
6. 根据 `output_format` 渲染：
   - `"word"` → 直接返回 Segment 列表（writer.py 自己处理样式）
   - `"markdown"` → `_render_segments_md()`，把 bold 变 `**...**`，superscript 变 `^...^`
   - `"latex"` → `_render_segments_tex()`，把 bold 变 `\textbf{}`，superscript 变 `$^{}$`

---

## 第三步：`writer.py` — 写出文件

三个 `write_*` 函数结构完全一样：把所有引用写进文件，每条之间空一行。

Word 格式稍微特殊：逐个 Segment 创建 `Run` 对象，直接在 Run 上设置
`.bold`、`.italic`、`.font.superscript`，python-docx 负责生成真正的 Word 格式。

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
├── core.py       串联 parser → formatter → writer 的 pipeline
├── parser.py     读 .bib 文件，按 cite_keys 顺序返回 entries
├── formatter.py  构建 Segment 列表，渲染成 md/tex/word 格式
└── writer.py     把格式化结果写进 .docx/.md/.tex 文件
```
