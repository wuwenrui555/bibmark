"""
Write formatted citations to .docx, .md, and .tex files.
"""

from docx import Document


def _build_legend_str(
    used_keys: list[str], annotation_map: dict, legend_labels: dict
) -> str:
    parts = []
    for key in used_keys:
        symbol = annotation_map.get(key, "")
        label = legend_labels.get(key, key)
        parts.append(f"{symbol} {label}")
    return "   ".join(parts)


def _make_superscript_run(paragraph, text: str):
    """Add a superscript run to a python-docx paragraph."""
    run = paragraph.add_run(text)
    run.font.superscript = True
    return run


def write_docx(
    citations: list,
    used_keys: list[str],
    annotation_map: dict,
    legend_labels: dict,
    output_path: str,
):
    doc = Document()
    for segments in citations:
        para = doc.add_paragraph()
        for seg in segments:
            run = para.add_run(seg["text"])
            run.bold = seg["bold"]
            run.italic = seg["italic"]
            if seg["superscript"]:
                run.font.superscript = True

    # Legend paragraph
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
    legend_str = _build_legend_str(used_keys, annotation_map, legend_labels)
    with open(output_path, "w", encoding="utf-8") as f:
        for citation in citations:
            f.write(citation + "\n\n")
        if legend_str:
            f.write(legend_str + "\n")
