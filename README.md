# bibmark

Generate formatted citation lists (Word, Markdown, LaTeX) from a `.bib` file,
with support for custom author-role annotations (co-first, corresponding, etc.).

**[→ View Wenrui's Bibliography](examples/wenrui_wu/output/citations.md)**

**[→ View Boyan's Bibliography](examples/boyan_wang/output/citations.md)**

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [.bib File Format](#bib-file-format)
- [Field handling](#field-handling)
- [Output Example](#output-example)

## Introduction

Academic CVs and grant applications often require a publication list that goes
beyond what a reference manager can export out of the box. The standard BibTeX
workflow gives you author names and journal metadata — but it knows nothing
about *your role* in each paper.

The missing pieces typically have to be added by hand:

- **Co-first authorship** (`#`) and **corresponding authorship** (`*`) are
  buried in the PDF or the journal webpage, not in any structured field of a
  `.bib` file.
- Every time you update your CV, you open each paper, check who shares first
  authorship, and manually insert the superscript symbols — then repeat the
  whole process for Word, Markdown, and LaTeX versions.
- Your own name needs to be **bolded** to stand out, which is another
  format-specific step that existing exporters don't handle.

`bibmark` solves this by letting you encode author roles directly in the `.bib`
file using a custom `bibmark` field, and then generating fully-formatted
citation lists in all three formats from a single source of truth. Update your
`.bib` once; every output stays in sync automatically.

## Installation

```bash
pip install git+https://github.com/wenruiwu/bibmark.git
```

## Usage

### Linear output

Write a script that imports `generate_citations`:

```python
from bibmark import generate_citations

generate_citations(
    bib_file="publications.bib",
    cite_keys=[
        "wu2022epletpredicted",
        "huang2022single",
    ],
    my_name="Wenrui Wu",
    annotation_map={"first": "#", "corresponding": "*"},
    superscript=True,
    output_dir="output",
)
```

Run it with:

```bash
python your_script.py
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
        "2024": ["zhang2024ccl19producing", "zhang2024effectiveness"],
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
@article{wu2022epletpredicted,
  author  = {Wu, Wenrui and Zhang, Huanxi and Tan, Jinghong and Fu, Qian and Li, Jun
             and Wu, Chenglin and Huang, Huiting and Xu, Bowen and Ling, Liuting
             and Liu, Longshan and Su, Xiaojun and Wang, Changxi},
  title   = {Eplet-Predicted Antigens: An Attempt to Introduce Eplets into
             Unacceptable Antigen Determination and Calculated Panel-Reactive
             Antibody Calculation Facilitating Kidney Allocation},
  journal = {Diagnostics},
  year    = {2022},
  volume  = {12},
  number  = {12},
  pages   = {2983},
  doi     = {10.3390/diagnostics12122983},
  bibmark = {first: {1, 2}, corresponding: {-2, -3}}
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

1. **<ins>Wenrui Wu</ins>**<sup>#</sup>, Huanxi Zhang<sup>#</sup>, Jinghong Tan, Qian Fu,
Jun Li, Chenglin Wu, Huiting Huang, Bowen Xu, Liuting Ling, Longshan Liu<sup>*</sup>,
Xiaojun Su<sup>*</sup>, and Changxi Wang. Eplet-Predicted Antigens: An Attempt to
Introduce Eplets into Unacceptable Antigen Determination and Calculated Panel-Reactive
Antibody Calculation Facilitating Kidney Allocation. ***Diagnostics***, 12(12):2983,
2022, doi:[10.3390/diagnostics12122983](https://doi.org/10.3390/diagnostics12122983)
```

(Markdown shown; Word and LaTeX use equivalent native formatting.)
