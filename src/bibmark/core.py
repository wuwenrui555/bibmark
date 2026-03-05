"""Pipeline: parse → format → write."""

import os

from .formatter import collect_used_keys, format_citation
from .parser import parse_bib_file
from .writer import write_docx, write_md, write_tex


def generate_citations(
    bib_files: list[str],
    my_name: str,
    annotation_map: dict,
    legend_labels: dict,
    superscript: bool = True,
    output_dir: str = ".",
    formats: list[str] = ("docx", "md", "tex"),
):
    """Generate citation output files from a list of .bib files.

    Parameters
    ----------
    bib_files     : ordered list of .bib file paths
    my_name       : your full name as it appears in bib author fields
    annotation_map: maps bibmark keys to symbols, e.g. {"first": "#"}
    legend_labels : maps bibmark keys to legend text, e.g. {"first": "Co-first author"}
    superscript   : render annotation symbols as superscript
    output_dir    : directory to write output files
    formats       : which formats to generate ("docx", "md", "tex")
    """
    os.makedirs(output_dir, exist_ok=True)

    entries = [parse_bib_file(p) for p in bib_files]
    used_keys = collect_used_keys(entries, annotation_map)

    if "docx" in formats:
        word_citations = [
            format_citation(e, my_name, annotation_map, superscript, "word")
            for e in entries
        ]
        write_docx(
            word_citations,
            used_keys,
            annotation_map,
            legend_labels,
            os.path.join(output_dir, "citations.docx"),
        )

    if "md" in formats:
        md_citations = [
            format_citation(e, my_name, annotation_map, superscript, "markdown")
            for e in entries
        ]
        write_md(
            md_citations,
            used_keys,
            annotation_map,
            legend_labels,
            os.path.join(output_dir, "citations.md"),
        )

    if "tex" in formats:
        tex_citations = [
            format_citation(e, my_name, annotation_map, superscript, "latex")
            for e in entries
        ]
        write_tex(
            tex_citations,
            used_keys,
            annotation_map,
            legend_labels,
            os.path.join(output_dir, "citations.tex"),
        )
