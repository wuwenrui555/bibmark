# Changelog

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
