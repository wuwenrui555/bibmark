"""
Write formatted citations to .docx, .md, and .tex files.
"""

from docx import Document


def _build_legend_str(
    used_keys: list[str], annotation_map: dict, legend_labels: dict
) -> str:
    """
    Build the legend line from the set of used bibmark keys.

    Parameters
    ----------
    used_keys : list[str]
        Ordered list of bibmark keys that appear in the citations.
    annotation_map : dict
        Maps bibmark keys to annotation symbols.
    legend_labels : dict
        Maps bibmark keys to human-readable label text.

    Returns
    -------
    str
        Legend string, e.g. ``"# Co-first author   * Corresponding author"``.
        Empty string if no keys are used.
    """
    parts = []
    for key in used_keys:
        symbol = annotation_map.get(key, "")
        label = legend_labels.get(key, key)
        parts.append(f"{symbol} {label}")
    return "   ".join(parts)



def write_docx(
    citations: list,
    used_keys: list[str],
    annotation_map: dict,
    legend_labels: dict,
    output_path: str,
):
    """
    Write citations and legend to a .docx file.

    Parameters
    ----------
    citations : list[list[Segment]]
        One list of segments per citation.
    used_keys : list[str]
        Ordered bibmark keys used across all citations, for the legend.
    annotation_map : dict
        Maps bibmark keys to annotation symbols.
    legend_labels : dict
        Maps bibmark keys to human-readable label text.
    output_path : str
        Destination file path.
    """
    doc = Document()
    for segments in citations:
        para = doc.add_paragraph()
        for seg in segments:
            run = para.add_run(seg["text"])
            run.bold = seg["bold"]
            run.italic = seg["italic"]
            if seg["superscript"]:
                run.font.superscript = True

    legend_str = _build_legend_str(used_keys, annotation_map, legend_labels)
    if legend_str:
        doc.add_paragraph(legend_str)

    doc.save(output_path)


def write_md(
    citations: list[str],
    used_keys: list[str],
    annotation_map: dict,
    legend_labels: dict,
    output_path: str,
):
    """
    Write citations and legend to a Markdown file.

    Parameters
    ----------
    citations : list[str]
        One Markdown-formatted string per citation.
    used_keys : list[str]
        Ordered bibmark keys used across all citations, for the legend.
    annotation_map : dict
        Maps bibmark keys to annotation symbols.
    legend_labels : dict
        Maps bibmark keys to human-readable label text.
    output_path : str
        Destination file path.
    """
    legend_str = _build_legend_str(used_keys, annotation_map, legend_labels)
    with open(output_path, "w", encoding="utf-8") as f:
        for citation in citations:
            f.write(citation + "\n\n")
        if legend_str:
            f.write(legend_str + "\n")


def write_tex(
    citations: list[str],
    used_keys: list[str],
    annotation_map: dict,
    legend_labels: dict,
    output_path: str,
):
    """
    Write citations and legend to a LaTeX file.

    Parameters
    ----------
    citations : list[str]
        One LaTeX-formatted string per citation.
    used_keys : list[str]
        Ordered bibmark keys used across all citations, for the legend.
    annotation_map : dict
        Maps bibmark keys to annotation symbols.
    legend_labels : dict
        Maps bibmark keys to human-readable label text.
    output_path : str
        Destination file path.
    """
    legend_str = _build_legend_str(used_keys, annotation_map, legend_labels)
    with open(output_path, "w", encoding="utf-8") as f:
        for citation in citations:
            f.write(citation + "\n\n")
        if legend_str:
            f.write(legend_str + "\n")
