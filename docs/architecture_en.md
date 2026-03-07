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

## Step 2: `core.py` — Group and validate

`generate_citations()` converts `cite_keys` into a uniform `sections` list
before passing it to the writers:

```python
# list input: wrap as a single section with heading=None
sections = [(None, entries)]

# dict input: flatten all keys to parse at once, then re-group
all_keys = [k for keys in cite_keys.values() for k in keys]
all_entries = parse_bib(bib_file, all_keys)
entries_by_key = {e.key: e for e in all_entries}
sections = [
    (heading, [entries_by_key[k] for k in keys if k in entries_by_key])
    for heading, keys in cite_keys.items()
]
```

### `validate_entry(entry)` (defined in `formatter.py`)

Before formatting, `core.py` calls `validate_entry()` once per entry to print
all warnings in one place and avoid duplicates:

- Missing required fields (`author`, `title`, `journal`, `year`, `volume`, `pages`, `doi`) → warning; placeholder `Unknown` used in output
- Missing `number` field → always warned; omitted from output when `volume` is present; when `volume` is also missing, the volume/number part renders as `Unknown(Unknown)`
- Author list ending with `others` (truncated list) → warning

---

## Step 3: `formatter.py` — Format citations

This is the most complex step. The core idea is: **build the citation as a list
of text segments with formatting flags first, then render to the target format
at the end**.

### What is a Segment?

A Segment is a small dict:

```python
{"text": "Wenrui Wu", "bold": True, "italic": False, "superscript": False, "underline": True, "url": ""}
```

- `url` is used for DOI hyperlinks; rendered in Markdown only (Word and LaTeX do not render links).
- `underline` is used to underline text; currently applied to `my_name`.

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
| `_get_field(entry, key, cite_key)` | Retrieve a field value (braces stripped); returns `"Unknown"` if absent |
| `_format_pages(pages)` | Replace `--` with an en-dash `–` |
| `_split_authors(author_str)` | Split author string on ` and ` |
| `_normalize_author(author)` | `"Wu, Wenrui"` → `"Wenrui Wu"` |

### What `format_citation()` does

1. Pulls the author string from the entry, splits and normalises each name
2. Parses the bibmark field to build a per-author annotation list
   - Positive indices: `1` = first author, `2` = second, and so on
   - Negative indices: `-1` = last author, `-2` = second-to-last — convenient for corresponding authors
3. Iterates over the author list and builds Segments one by one:
   - If the name matches `my_name`, sets `bold=True` and `underline=True`
   - If the author has an annotation symbol, sets `superscript=True` when applicable
   - Inserts `", and "` before the last author and `", "` between all others
4. Appends title, journal (bold italic), and the volume/number/pages/year body
5. DOI is split into two Segments: a plain `"doi:"` prefix and the DOI number
   with a `url` field
6. Renders according to `output_format`:
   - `"word"` → returns the Segment list as-is (writer.py applies the styling)
   - `"markdown"` → `_render_segments_md()`: bold → `**...**`, italic → `*...*`, superscript → `<sup>...</sup>` (`*`/`_` escaped as HTML entities to avoid emphasis interpretation), underline → `<ins>...</ins>` (GitHub sanitizer strips `<u>`; `<ins>` is allowed and renders with underline), url → `[text](url)`
   - `"latex"` → `_render_segments_tex()`: bold → `\textbf{}`, italic → `\textit{}`, superscript → `$^{}$`, underline → `\underline{}`

---

## Step 4: `writer.py` — Write output files

All three `write_*` functions receive `sections: list[tuple[str | None, list]]`,
a list of `(heading, citations)` pairs. `core.py` guarantees:

- `cite_keys` is a list → `sections = [(None, all_citations)]`
- `cite_keys` is a dict → `sections = [("2025", [...]), ("2024", [...]), ...]`

Each function writes the top-level Bibliography heading, then iterates over
sections — inserting a level-2 heading when `heading is not None` — and writes
each citation prefixed with a per-section number (`1.`, `2.`, …) that resets
at the start of every section.

| Function | Level-1 heading | Level-2 heading (grouped) |
|----------|-----------------|---------------------------|
| `write_docx` | `Heading 1` | `Heading 2` |
| `write_md` | `# Bibliography` | `## <heading>` |
| `write_tex` | `\section*{Bibliography}` | `\subsection*{<heading>}` |

The Word format is slightly special: the number prefix is added as a plain Run
at the start of each paragraph, followed by one Run per Segment with `.bold`,
`.italic`, and `.font.superscript` set directly.

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
