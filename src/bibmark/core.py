"""
Pipeline: parse → format → write.
"""

import os

from .formatter import format_citation, validate_entry
from .parser import parse_bib
from .writer import write_docx, write_md, write_tex


def generate_citations(
    bib_file: str,
    cite_keys: list[str] | dict[str, list[str]],
    my_name: str,
    annotation_map: dict,
    superscript: bool = True,
    output_dir: str = ".",
    formats: list[str] = ("docx", "md", "tex"),
):
    """
    Generate citation output files from a .bib file.

    Parameters
    ----------
    bib_file : str
        Path to the .bib file containing all entries.
    cite_keys : list[str] or dict[str, list[str]]
        Cite keys specifying which entries to include and in what order.
        Pass a plain list for a flat bibliography, or a dict mapping
        section headings to lists of cite keys to produce a grouped
        bibliography with a level-2 heading per section.
    my_name : str
        Your full name as it appears in bib author fields. Rendered in bold.
    annotation_map : dict
        Maps bibmark keys to annotation symbols, e.g. ``{"first": "#"}``.
    superscript : bool, optional
        Whether to render annotation symbols as superscript. Default is ``True``.
    output_dir : str, optional
        Directory to write output files. Created if it does not exist. Default is ``"."``.
    formats : list[str], optional
        Which formats to generate. Any subset of ``["docx", "md", "tex"]``.
        Default is all three.
    """
    os.makedirs(output_dir, exist_ok=True)

    if isinstance(cite_keys, list):
        entries = parse_bib(bib_file, cite_keys)
        for entry in entries:
            validate_entry(entry)
        sections = [(None, entries)]
    else:
        all_keys = [k for keys in cite_keys.values() for k in keys]
        all_entries = parse_bib(bib_file, all_keys)
        for entry in all_entries:
            validate_entry(entry)
        entries_by_key = {e.key: e for e in all_entries}
        sections = [
            (heading, [entries_by_key[k] for k in keys if k in entries_by_key])
            for heading, keys in cite_keys.items()
        ]

    if "docx" in formats:
        write_docx(
            [(h, [format_citation(e, my_name, annotation_map, superscript, "word") for e in entries]) for h, entries in sections],
            os.path.join(output_dir, "citations.docx"),
        )

    if "md" in formats:
        write_md(
            [(h, [format_citation(e, my_name, annotation_map, superscript, "markdown") for e in entries]) for h, entries in sections],
            os.path.join(output_dir, "citations.md"),
        )

    if "tex" in formats:
        write_tex(
            [(h, [format_citation(e, my_name, annotation_map, superscript, "latex") for e in entries]) for h, entries in sections],
            os.path.join(output_dir, "citations.tex"),
        )
