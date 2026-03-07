# Changelog

## [1.0.0] - 2026-03-06

First stable release. Covers all features developed across the 0.x series,
plus new additions in this release.

### Added

- `continuous_numbering` parameter in `generate_citations()`: when `True`,
  citation numbers continue across sections; when `False` (default), numbering
  resets to 1 at the start of each section.
- Examples reorganized by person (`examples/<name>/`), each with its own
  `publications.bib`, `run.py`, and `output/`. A top-level
  `examples/run_all_examples.py` runs all examples via `uv run`.

### Changed

- Missing required fields now use `Unknown` as a placeholder instead of `???`.
- When `volume` is missing, the volume/number part renders as `Unknown(Unknown)`
  to make both gaps explicit, regardless of whether `number` is present.
- `number` is now always validated and reported in warnings; it is silently
  omitted from output only when `volume` is present.
- All missing-field warnings for the same entry are consolidated into a single
  line: `WARNING: missing [field1, field2] in <cite_key>`.

### Core features (carried over from 0.x)

- `generate_citations()` public API: reads a `.bib` file and produces formatted
  citation lists in Word (`.docx`), Markdown, and LaTeX (`.tex`).
- Grouped bibliography: `cite_keys` accepts `dict[str, list[str]]` to produce
  a sectioned output with a level-2 heading per group.
- Custom `bibmark` field for author-role annotations (e.g. co-first `#`,
  corresponding `*`). Supports 1-based positive and negative indices.
- Segment-based intermediate representation: citation data is built once and
  rendered per output format, avoiding logic duplication.
- `my_name` rendered in bold and underline across all output formats.
- Journal name rendered in bold italic across all output formats.
- DOI rendered as a clickable hyperlink in Markdown output.
- LaTeX output includes a complete document wrapper and escapes special chars.

---

## [0.2.2] - 2026-03-05

### Fixed

- Annotation symbols `*` and `_` inside `<sup>` are now escaped as `&#42;`
  and `&#95;` respectively, preventing GitHub Markdown from interpreting them
  as emphasis markers and turning surrounding text italic.
- Underline formatting in Markdown now uses `<ins>…</ins>` instead of
  `<u>…</u>`. GitHub's HTML sanitizer strips `<u>` but allows `<ins>`, which
  browsers render with `text-decoration: underline` by default.
- Bold and underline are now applied in the correct order (`**<ins>…</ins>**`
  instead of `<ins>**…**</ins>`), ensuring both format correctly on GitHub.

---

## [0.2.1] - 2026-03-05

### Fixed

- Markdown superscript now uses `<sup>…</sup>` instead of `^…^` for
  correct rendering on GitHub (CommonMark does not support `^text^`).
- DOI in Markdown output is now formatted as `doi:[10.xxx/yyy](url)` so
  that only the DOI number is hyperlinked, not the `doi:` prefix.

---

## [0.2.0] - 2026-03-05

### Added

- Grouped bibliography: `cite_keys` now accepts `dict[str, list[str]]` to
  produce a sectioned output with a level-2 heading per group (Markdown `##`,
  LaTeX `\subsection*`, Word Heading 2).
- Per-section numbering: citations are numbered from 1 within each section, or
  globally for flat lists.
- Underline formatting support across all three output formats (Markdown:
  `<u>…</u>`, LaTeX: `\underline{}`, Word: `run.underline`).
- `my_name` is now rendered with underline in addition to bold.

### Changed

- Journal name is now rendered as bold italic (previously italic only).

### Fixed

- LaTeX output now includes a complete document wrapper (`\documentclass`,
  `\usepackage`, `\begin{document}`, `\end{document}`) so the `.tex` file
  compiles standalone out of the box.
- Special LaTeX characters (`#`, `%`, `&`, `_`) in text content are now
  properly escaped.
- Paragraph indentation disabled in LaTeX output (`\setlength{\parindent}{0pt}`)
  so all citation numbers align to the left margin.

---

## [0.1.0] - 2026-03-05

Initial release.

### Added

- `generate_citations()` public API: reads a `.bib` file and produces formatted
  citation lists in Word (`.docx`), Markdown, and LaTeX (`.tex`) formats.
- Single-bib design: all entries live in one `.bib` file; output order is
  controlled by the `cite_keys` parameter, not by the order in the file.
- `bibmark` custom field for author-role annotations (e.g. co-first `#`,
  corresponding `*`). Supports 1-based positive indices and negative indices
  (`-1` = last author, useful for corresponding authors at the end of the list).
- Segment-based intermediate representation: citation data is built once as a
  list of formatted segments and then rendered per output format, avoiding
  logic duplication.
- Annotation symbols rendered as superscript (configurable via `superscript`
  parameter).
- User's own name (`my_name`) rendered in bold across all output formats.
- Journal name rendered in italic across all output formats.
- DOI rendered as a clickable hyperlink in Markdown output.
- `Bibliography` heading written at the top of every output file.
- LaTeX protective braces (e.g. `{{China}}`) automatically stripped from all
  field values.
- `number` field treated as optional: omitted from output when absent, with a
  warning printed to stderr.
- Centralised validation via `validate_entry()`: missing required fields,
  missing `number`, and truncated author lists (`and others`) each produce a
  single warning per entry.
- Architecture documentation in both Chinese and English (`docs/`).
