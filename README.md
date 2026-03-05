# bibmark

Generate formatted citation lists (Word, Markdown, LaTeX) from ordered `.bib` files, with support for custom author-role annotations (co-first, corresponding, etc.).

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
    bib_files=["paper1.bib", "paper2.bib"],
    my_name="Wenrui Wu",
    annotation_map={
        "first":         "#",
        "corresponding": "*",
    },
    legend_labels={
        "first":         "Co-first author",
        "corresponding": "Corresponding author",
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

## .bib File Format

Each `.bib` file should contain **one entry**. Use the custom `bibmark` field to encode author roles as 1-based author indices:

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
  bibmark = {first: {1, 2, 3}, corresponding: {5, 6, 7}}
}
```

## Output Example

```plain
Mingchuan Huang^#^, **Wenrui Wu**^#^, Qiang Zhang^#^, Jun Li, Xiaojun Su^*^,
Longshan Liu^*^, and Changxi Wang^*^. Single kidney transplantation ...
*Translational Pediatrics*, 11(11):1872885–1871885, 2022, doi:10.21037/tp-22-547

# Co-first author   * Corresponding author
```

## `generate_citations` Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `bib_files` | `list[str]` | — | Ordered list of `.bib` file paths |
| `my_name` | `str` | — | Your name as it appears in bib author fields |
| `annotation_map` | `dict` | — | Maps bibmark keys to symbols |
| `legend_labels` | `dict` | — | Maps bibmark keys to legend text |
| `superscript` | `bool` | `True` | Render symbols as superscript |
| `output_dir` | `str` | `"."` | Output directory |
| `formats` | `list[str]` | `("docx","md","tex")` | Which formats to generate |
