"""
Write formatted citations to .docx, .md, and .tex files.
"""

from docx import Document


def write_docx(citations: list, output_path: str):
    """
    Write citations to a .docx file.

    Parameters
    ----------
    citations : list[list[Segment]]
        One list of segments per citation.
    output_path : str
        Destination file path.
    """
    doc = Document()
    doc.add_heading("Bibliography", level=1)
    for segments in citations:
        para = doc.add_paragraph()
        for seg in segments:
            run = para.add_run(seg["text"])
            run.bold = seg["bold"]
            run.italic = seg["italic"]
            if seg["superscript"]:
                run.font.superscript = True
    doc.save(output_path)


def write_md(citations: list[str], output_path: str):
    """
    Write citations to a Markdown file.

    Parameters
    ----------
    citations : list[str]
        One Markdown-formatted string per citation.
    output_path : str
        Destination file path.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Bibliography\n\n")
        for citation in citations:
            f.write(citation + "\n\n")


def write_tex(citations: list[str], output_path: str):
    """
    Write citations to a LaTeX file.

    Parameters
    ----------
    citations : list[str]
        One LaTeX-formatted string per citation.
    output_path : str
        Destination file path.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\\section*{Bibliography}\n\n")
        for citation in citations:
            f.write(citation + "\n\n")
