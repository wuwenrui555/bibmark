"""
Pipeline: parse → format → write.
"""

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
    """
    Generate citation output files from an ordered list of .bib files.

    Parameters
    ----------
    bib_files : list[str]
        Ordered list of .bib file paths. Citations are output in this order.
    my_name : str
        Your full name as it appears in bib author fields. Rendered in bold.
    annotation_map : dict
        Maps bibmark keys to annotation symbols, e.g. ``{"first": "#"}``.
    legend_labels : dict
        Maps bibmark keys to legend text, e.g. ``{"first": "Co-first author"}``.
    superscript : bool, optional
        Whether to render annotation symbols as superscript. Default is ``True``.
    output_dir : str, optional
        Directory to write output files. Created if it does not exist. Default is ``"."``.
    formats : list[str], optional
        Which formats to generate. Any subset of ``["docx", "md", "tex"]``.
        Default is all three.
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
