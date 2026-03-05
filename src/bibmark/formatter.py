"""
Format parsed bib entries into citation strings or run lists.
"""

import re
import sys
from typing import Union

from .parser import parse_bibmark_field


def _split_authors(author_str: str) -> list[str]:
    """
    Split a bib author string on `` and `` into individual name strings.

    Parameters
    ----------
    author_str : str
        Raw author field value, e.g. ``"Wu, Wenrui and Zhang, San"``.

    Returns
    -------
    list[str]
        Individual author name strings.
    """
    return [a.strip() for a in re.split(r"\s+and\s+", author_str, flags=re.IGNORECASE)]


def _normalize_author(author: str) -> str:
    """
    Convert ``"Last, First Middle"`` to ``"First Middle Last"``.

    Parameters
    ----------
    author : str
        Author name in either ``"Last, First"`` or ``"First Last"`` format.

    Returns
    -------
    str
        Author name in ``"First Last"`` format.
    """
    if "," in author:
        parts = author.split(",", 1)
        last = parts[0].strip()
        first = parts[1].strip()
        return f"{first} {last}"
    return author.strip()


def _get_field(entry, key: str, cite_key: str) -> str:
    """
    Retrieve a field value from an entry, warning and returning ``"???"`` if missing.

    Parameters
    ----------
    entry : bibtexparser.model.Entry
        Parsed bib entry.
    key : str
        Field name to retrieve.
    cite_key : str
        The entry's cite key, used in warning messages.

    Returns
    -------
    str
        Field value as a string, or ``"???"`` if the field is absent.
    """
    val = entry.fields_dict.get(key)
    if val is None:
        return "???"
    return _strip_braces(str(val.value))


def _strip_braces(value: str) -> str:
    """
    Remove LaTeX protective braces from a field value.

    Parameters
    ----------
    value : str
        Raw field value possibly containing brace-protected text,
        e.g. ``"Transplantation from {{China}}"``.

    Returns
    -------
    str
        Value with all curly braces removed,
        e.g. ``"Transplantation from China"``.
    """
    return re.sub(r"\{+([^{}]*)\}+", r"\1", value)


def _format_pages(pages: str) -> str:
    """
    Replace ``--`` with an en-dash in a pages string.

    Parameters
    ----------
    pages : str
        Raw pages field value, e.g. ``"123--145"``.

    Returns
    -------
    str
        Pages string with en-dash, e.g. ``"123–145"``.
    """
    return pages.replace("--", "\u2013")


# ---------------------------------------------------------------------------
# Segment-based rendering
# ---------------------------------------------------------------------------

Segment = dict  # {"text": str, "bold": bool, "italic": bool, "superscript": bool}


def _seg(text: str, bold=False, italic=False, superscript=False) -> Segment:
    """
    Create a text segment with formatting flags.

    Parameters
    ----------
    text : str
        The text content of the segment.
    bold : bool, optional
        Whether the text is bold.
    italic : bool, optional
        Whether the text is italic.
    superscript : bool, optional
        Whether the text is superscript.

    Returns
    -------
    Segment
        Dict with keys ``text``, ``bold``, ``italic``, ``superscript``.
    """
    return {"text": text, "bold": bold, "italic": italic, "superscript": superscript}


def _render_segments_md(segments: list[Segment]) -> str:
    """
    Render a list of segments to a Markdown string.

    Parameters
    ----------
    segments : list[Segment]
        Formatted text segments.

    Returns
    -------
    str
        Markdown-formatted citation string.
    """
    parts = []
    for s in segments:
        text = s["text"]
        if s["superscript"]:
            text = f"^{text}^"
        if s["italic"]:
            text = f"*{text}*"
        if s["bold"]:
            text = f"**{text}**"
        parts.append(text)
    return "".join(parts)


def _render_segments_tex(segments: list[Segment]) -> str:
    """
    Render a list of segments to a LaTeX string.

    Parameters
    ----------
    segments : list[Segment]
        Formatted text segments.

    Returns
    -------
    str
        LaTeX-formatted citation string.
    """
    parts = []
    for s in segments:
        text = s["text"]
        if s["superscript"]:
            text = f"$^{{{text}}}$"
        if s["italic"]:
            text = f"\\textit{{{text}}}"
        if s["bold"]:
            text = f"\\textbf{{{text}}}"
        parts.append(text)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Main formatter
# ---------------------------------------------------------------------------


def format_citation(
    entry,
    my_name: str,
    annotation_map: dict,
    superscript: bool,
    output_format: str,
) -> Union[str, list[Segment]]:
    """
    Format a parsed bib entry into a citation.

    Parameters
    ----------
    entry : bibtexparser.model.Entry
        Parsed bib entry.
    my_name : str
        Full name of the document owner, rendered in bold.
    annotation_map : dict
        Maps bibmark keys to annotation symbols, e.g. ``{"first": "#"}``.
    superscript : bool
        Whether to render annotation symbols as superscript.
    output_format : str
        One of ``"markdown"``, ``"latex"``, or ``"word"``.

    Returns
    -------
    str or list[Segment]
        Formatted citation string for ``"markdown"`` and ``"latex"``;
        list of segments for ``"word"``.

    Raises
    ------
    ValueError
        If ``output_format`` is not a recognised value.
    """
    cite_key = entry.key
    fields = entry.fields_dict

    # --- Authors ---
    author_str = _get_field(entry, "author", cite_key)
    authors = [_normalize_author(a) for a in _split_authors(author_str)]

    # --- bibmark annotations ---
    bibmark_raw = fields.get("bibmark")
    bibmark_dict = {}
    if bibmark_raw is not None:
        bibmark_dict = parse_bibmark_field(
            str(bibmark_raw.value), cite_key, annotation_map
        )

    # Build per-author annotation list (list of symbol strings, "" if none)
    author_annotations: list[str] = [""] * len(authors)
    for key, indices in bibmark_dict.items():
        symbol = annotation_map.get(key, "")
        if not symbol:
            continue
        for idx in indices:
            if 1 <= idx <= len(authors):
                author_annotations[idx - 1] += symbol

    # --- Build author segments ---
    segments: list[Segment] = []
    for i, (name, annotation) in enumerate(zip(authors, author_annotations)):
        is_me = name.strip() == my_name.strip()
        is_last = i == len(authors) - 1

        if i > 0:
            if is_last:
                segments.append(_seg(", and "))
            else:
                segments.append(_seg(", "))

        segments.append(_seg(name, bold=is_me))

        if annotation:
            if superscript:
                segments.append(_seg(annotation, superscript=True))
            else:
                segments.append(_seg(annotation))

    # --- Title ---
    title = _get_field(entry, "title", cite_key)
    segments.append(_seg(f". {title}. "))

    # --- Journal (italic) ---
    journal = _get_field(entry, "journal", cite_key)
    segments.append(_seg(journal, italic=True))

    # --- Volume(Number):Pages, Year, doi:DOI ---
    volume = _get_field(entry, "volume", cite_key)
    number_val = entry.fields_dict.get("number")
    number_str = f"({number_val.value})" if number_val is not None else ""
    pages_raw = _get_field(entry, "pages", cite_key)
    pages = _format_pages(pages_raw)
    year = _get_field(entry, "year", cite_key)
    doi = _get_field(entry, "doi", cite_key)

    body = f", {volume}{number_str}:{pages}, {year}, doi:{doi}"
    segments.append(_seg(body))

    if output_format == "word":
        return segments
    elif output_format == "markdown":
        return _render_segments_md(segments)
    elif output_format == "latex":
        return _render_segments_tex(segments)
    else:
        raise ValueError(f"Unknown output_format: {output_format!r}")


def validate_entry(entry) -> None:
    """
    Check an entry for missing or problematic fields and print warnings.

    Parameters
    ----------
    entry : bibtexparser.model.Entry
        Parsed bib entry to validate.
    """
    cite_key = entry.key
    required = ["author", "title", "journal", "year", "volume", "pages", "doi"]
    for field in required:
        if entry.fields_dict.get(field) is None:
            print(f"WARNING: missing {field} in {cite_key}", file=sys.stderr)
    if entry.fields_dict.get("number") is None:
        print(f"WARNING: missing number in {cite_key}", file=sys.stderr)
    author_val = entry.fields_dict.get("author")
    if author_val and "others" in str(author_val.value).lower():
        print(f"WARNING: author list truncated with 'others' in {cite_key}", file=sys.stderr)
