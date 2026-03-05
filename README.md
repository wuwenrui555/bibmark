# bibmark

Generate formatted citation lists (Word, Markdown, LaTeX) from a `.bib` file,
with support for custom author-role annotations (co-first, corresponding, etc.).

## Setup

Requires [uv](https://github.com/astral-sh/uv).

```bash
git clone <repo>
cd bibmark
uv sync
```

## Usage

Write a script that imports `generate_citations`:

```python
from bibmark import generate_citations

generate_citations(
    bib_file="publications.bib",
    cite_keys=[
        "huang2022kidney",
        "wu2023tls",
    ],
    my_name="Wenrui Wu",
    annotation_map={
        "first":         "#",
        "corresponding": "*",
    },
    superscript=True,
    output_dir="output",
)
```

Run it with:

```bash
uv run python your_script.py
```

This generates `output/citations.docx`, `output/citations.md`, and `output/citations.tex`.

### Grouped output

Pass a `dict` instead of a `list` to group citations under section headings.
Each key becomes a level-2 heading; numbering restarts from 1 within each section.

```python
generate_citations(
    bib_file="publications.bib",
    cite_keys={
        "2025": ["huang2025effect"],
        "2024": ["zhang2024ccl19producing", "feng2024timerestricted"],
        "2022": ["wu2022epletpredicted", "huang2022single"],
    },
    my_name="Wenrui Wu",
    annotation_map={"first": "#", "corresponding": "*"},
    output_dir="output",
)
```

## .bib File Format

Put all entries in a single `.bib` file. Use the custom `bibmark` field to encode
author roles as 1-based (or negative) author indices:

```bibtex
@article{huang2022kidney,
  author  = {Mingchuan Huang and Wenrui Wu and Qiang Zhang and Jun Li and Xiaojun Su and Longshan Liu and Changxi Wang},
  title   = {Single kidney transplantation from pediatric deceased donors in China},
  journal = {Translational Pediatrics},
  year    = {2022},
  volume  = {11},
  number  = {11},
  pages   = {1872885--1871885},
  doi     = {10.21037/tp-22-547},
  bibmark = {first: {1, 2, 3}, corresponding: {-3, -2, -1}}
}
```

Negative indices count from the end of the author list: `-1` is the last author,
`-2` is second to last, and so on. This is convenient for corresponding authors,
who are typically at the end.

The order of entries in the output is determined by `cite_keys`, not by the order
in the `.bib` file.

## Field handling

| Field | Required | Behaviour if missing |
| ----- | -------- | -------------------- |
| `author`, `title`, `journal`, `year`, `volume`, `pages`, `doi` | Yes | Warning printed, `???` in output |
| `number` | No | Warning printed, omitted from output |
| `bibmark` | No | No annotations applied |

LaTeX protective braces (e.g. `{{China}}`) are automatically stripped from all
field values. Truncated author lists ending with `and others` trigger a warning.

## Output Example

```plain
# Bibliography

## 2022

1. Mingchuan Huang^#^, **Wenrui Wu**^#^, Qiang Zhang^#^, Jun Li, Xiaojun Su^*^,
Longshan Liu^*^, and Changxi Wang^*^. Single kidney transplantation ...
*Translational Pediatrics*, 11(11):1872885–1871885, 2022,
[doi:10.21037/tp-22-547](https://doi.org/10.21037/tp-22-547)
```

(Markdown shown; Word and LaTeX use equivalent native formatting.)

## `generate_citations` Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `bib_file` | `str` | — | Path to the `.bib` file |
| `cite_keys` | `list[str]` or `dict[str, list[str]]` | — | Flat list for a simple bibliography; dict for grouped output with section headings |
| `my_name` | `str` | — | Your name as it appears in bib author fields |
| `annotation_map` | `dict` | — | Maps bibmark keys to symbols |
| `superscript` | `bool` | `True` | Render symbols as superscript |
| `output_dir` | `str` | `"."` | Output directory |
| `formats` | `list[str]` | `("docx","md","tex")` | Which formats to generate |
