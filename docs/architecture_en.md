# bibmark — Code Architecture

## Overview

When you call `generate_citations()`, the code runs three steps in sequence:

```plain
publications.bib
    ↓  parser.py    — read and parse
    ↓  formatter.py — format data into citation text
    ↓  writer.py    — write text to output files
    ↓
citations.docx / .md / .tex
```

This pipeline is wired together in `core.py`. `__init__.py` simply re-exports
`generate_citations` as the public API.

---

## Step 1: `parser.py` — Read the .bib file

### `parse_bib(path, keys)`

Uses bibtexparser v2 to read the entire `.bib` file, then returns entries in the
order specified by `keys`. This means output order is controlled by the
`cite_keys` list in your calling script, not by the order of entries in the
`.bib` file.

```python
entries_by_key = {e.key: e for e in library.entries}
# retrieve in keys order; warn and skip any key not found
```

Each entry has a `fields_dict` mapping field names to their values, for example:

```python
entry.fields_dict["author"].value  # → "Wenrui Wu and San Zhang"
entry.fields_dict["journal"].value # → "Cancer Cell"
entry.fields_dict["bibmark"].value # → "first: {1, 2}, corresponding: {3}"
```

### `parse_bibmark_field(value, cite_key, annotation_map)`

Parses the bibmark field string into a structured dict:

```plain
"first: {1, 2}, corresponding: {3, 4}"
        ↓
{"first": [1, 2], "corresponding": [3, 4]}
```

Uses a regex to match the `key: {number, number}` pattern. If a key is not in
`annotation_map` (e.g. you wrote `typo: {1}`), a warning is printed to stderr.

---

## Step 2: `formatter.py` — Format citations

This is the most complex step. The core idea is: **build the citation as a list
of text segments with formatting flags first, then render to the target format
at the end**.

### What is a Segment?

A Segment is a small dict:

```python
{"text": "Wenrui Wu", "bold": True, "italic": False, "superscript": False}
```

A full citation is a list of Segments, for example:

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

### What `format_citation()` does

1. Pulls the author string from the entry and splits it on ` and ` via `_split_authors`
2. Normalises each name with `_normalize_author`: `"Wu, Wenrui"` → `"Wenrui Wu"`
3. Parses the bibmark field to know which authors get annotation symbols (`#`, `*`, etc.)
4. Iterates over the author list and builds Segments one by one:
   - If the name matches `my_name`, sets `bold=True`
   - If the author has an annotation symbol, sets `superscript=True` when applicable
   - Inserts `", and "` before the last author and `", "` between all others
5. Appends title, journal (italic), and the volume/number/pages/year/doi body
6. Renders according to `output_format`:
   - `"word"` → returns the Segment list as-is (writer.py applies the styling)
   - `"markdown"` → `_render_segments_md()`: bold → `**...**`, superscript → `^...^`
   - `"latex"` → `_render_segments_tex()`: bold → `\textbf{}`, superscript → `$^{}$`

---

## Step 3: `writer.py` — Write output files

All three `write_*` functions follow the same structure: write each citation to
the file, separated by a blank line.

The Word format is slightly special: each Segment becomes a `Run` object, and
`.bold`, `.italic`, `.font.superscript` are set directly on the Run.
python-docx takes care of producing the actual Word formatting.

---

## Why the Segment design?

It solves a practical problem:

> The same citation data needs to be output in three completely different formats
> (Word objects, a Markdown string, a LaTeX string).

If the formatting logic were written separately for each output format, the
author-ordering, `my_name` detection, and bibmark annotation logic would be
duplicated three times. With Segments, **the construction logic is written once;
the rendering logic is written once per format**. This is a common
Intermediate Representation (IR) pattern.

---

## File structure

```plain
src/bibmark/
├── __init__.py   exposes only generate_citations to the outside
├── core.py       wires parser → formatter → writer into a pipeline
├── parser.py     reads .bib file, returns entries in cite_keys order
├── formatter.py  builds Segment lists and renders to md/tex/word
└── writer.py     writes formatted output to .docx/.md/.tex files
```
