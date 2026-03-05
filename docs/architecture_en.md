# bibmark — Code Architecture

## Overview

When you call `generate_citations()`, the code runs four steps in sequence:

```plain
publications.bib
    ↓  parser.py    — read and parse
    ↓  core.py      — validate fields, print warnings
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
entry.fields_dict["bibmark"].value # → "first: {1, 2}, corresponding: {-1}"
```

### `parse_bibmark_field(value, cite_key, annotation_map)`

Parses the bibmark field string into a structured dict:

```plain
"first: {1, 2}, corresponding: {-3, -2, -1}"
        ↓
{"first": [1, 2], "corresponding": [-3, -2, -1]}
```

Uses a regex to match the `key: {number, number}` pattern, supporting negative
indices. If a key is not in `annotation_map` (e.g. you wrote `typo: {1}`), a
warning is printed to stderr.

---

## Step 2: `core.py` — Validate entries

### `validate_entry(entry)` (defined in `formatter.py`)

Before formatting, `core.py` calls `validate_entry()` once per entry to print
all warnings in one place and avoid duplicates:

- Missing required fields (`author`, `title`, `journal`, `year`, `volume`, `pages`, `doi`) → warning
- Missing `number` field → warning (optional field; the `(number)` part is simply omitted from output)
- Author list ending with `others` (truncated list) → warning

---

## Step 3: `formatter.py` — Format citations

This is the most complex step. The core idea is: **build the citation as a list
of text segments with formatting flags first, then render to the target format
at the end**.

### What is a Segment?

A Segment is a small dict:

```python
{"text": "Wenrui Wu", "bold": True, "italic": False, "superscript": False, "url": ""}
```

The `url` field is used for DOI hyperlinks; it is rendered in Markdown output
(Word and LaTeX do not render links).

A full citation is a list of Segments, for example:

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

### Helper functions

| Function | Purpose |
|----------|---------|
| `_strip_braces(value)` | Remove LaTeX protective braces, e.g. `{{China}}` → `China` |
| `_get_field(entry, key, cite_key)` | Retrieve a field value (braces stripped); returns `"???"` if absent |
| `_format_pages(pages)` | Replace `--` with an en-dash `–` |
| `_split_authors(author_str)` | Split author string on ` and ` |
| `_normalize_author(author)` | `"Wu, Wenrui"` → `"Wenrui Wu"` |

### What `format_citation()` does

1. Pulls the author string from the entry, splits and normalises each name
2. Parses the bibmark field to build a per-author annotation list
   - Positive indices: `1` = first author, `2` = second, and so on
   - Negative indices: `-1` = last author, `-2` = second-to-last — convenient for corresponding authors
3. Iterates over the author list and builds Segments one by one:
   - If the name matches `my_name`, sets `bold=True`
   - If the author has an annotation symbol, sets `superscript=True` when applicable
   - Inserts `", and "` before the last author and `", "` between all others
4. Appends title, journal (italic), and the volume/number/pages/year body
5. DOI is a separate Segment with a `url` field
6. Renders according to `output_format`:
   - `"word"` → returns the Segment list as-is (writer.py applies the styling)
   - `"markdown"` → `_render_segments_md()`: bold → `**...**`, superscript → `^...^`, url → `[text](url)`
   - `"latex"` → `_render_segments_tex()`: bold → `\textbf{}`, superscript → `$^{}$`

---

## Step 4: `writer.py` — Write output files

All three `write_*` functions follow the same structure: write a Bibliography
heading, then write each citation separated by a blank line.

| Function | Heading |
|----------|---------|
| `write_docx` | `doc.add_heading("Bibliography", level=1)` |
| `write_md` | `# Bibliography` |
| `write_tex` | `\section*{Bibliography}` |

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
├── core.py       wires parser → validate → formatter → writer into a pipeline
├── parser.py     reads .bib file, returns entries in cite_keys order
├── formatter.py  validate_entry checks fields; builds Segment lists and renders
└── writer.py     writes formatted output to .docx/.md/.tex files
```
