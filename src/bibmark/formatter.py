"""
Format parsed bib entries into citation strings or run lists.
"""

import re
import sys
from typing import Union

from .parser import parse_bibmark_field


def _split_authors(author_str: str) -> list[str]:
    return [a.strip() for a in re.split(r"\s+and\s+", author_str, flags=re.IGNORECASE)]


def _normalize_author(author: str) -> str:
    """Convert 'Last, First Middle' → 'First Middle Last'."""
    if "," in author:
        parts = author.split(",", 1)
        last = parts[0].strip()
        first = parts[1].strip()
        return f"{first} {last}"
    return author.strip()


def _get_field(entry, key: str, cite_key: str) -> str:
    """Get field value, emit warning and return '???' if missing."""
    val = entry.fields_dict.get(key)
    if val is None:
        print(f"WARNING: missing {key} in {cite_key}", file=sys.stderr)
        return "???"
    return str(val.value)


def _format_pages(pages: str) -> str:
    return pages.replace("--", "\u2013")


# ---------------------------------------------------------------------------
# Segment-based rendering
# ---------------------------------------------------------------------------

Segment = dict  # {"text": str, "bold": bool, "italic": bool, "superscript": bool}


def _seg(text: str, bold=False, italic=False, superscript=False) -> Segment:
    return {"text": text, "bold": bold, "italic": italic, "superscript": superscript}


def _render_segments_md(segments: list[Segment]) -> str:
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
    Parameters
    ----------
    entry         : bibtexparser v2 entry object
    my_name       : full name of document owner, rendered in bold
    annotation_map: dict mapping bibmark keys to symbols
    superscript   : whether to render annotations as superscript
    output_format : "markdown" | "latex" | "word"

    Returns
    -------
    str for "markdown" and "latex", list[Segment] for "word"
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
    used_keys: list[str] = []
    for key, indices in bibmark_dict.items():
        symbol = annotation_map.get(key, "")
        if not symbol:
            continue
        if key not in used_keys:
            used_keys.append(key)
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
    number = _get_field(entry, "number", cite_key)
    pages_raw = _get_field(entry, "pages", cite_key)
    pages = _format_pages(pages_raw)
    year = _get_field(entry, "year", cite_key)
    doi = _get_field(entry, "doi", cite_key)

    body = f", {volume}({number}):{pages}, {year}, doi:{doi}"
    segments.append(_seg(body))

    if output_format == "word":
        return segments
    elif output_format == "markdown":
        return _render_segments_md(segments)
    elif output_format == "latex":
        return _render_segments_tex(segments)
    else:
        raise ValueError(f"Unknown output_format: {output_format!r}")


def collect_used_keys(
    entries,
    annotation_map: dict,
) -> list[str]:
    """Return ordered list of bibmark keys actually used across all entries."""
    seen: list[str] = []
    for entry in entries:
        fields = entry.fields_dict
        bibmark_raw = fields.get("bibmark")
        if bibmark_raw is None:
            continue
        bibmark_dict = parse_bibmark_field(
            str(bibmark_raw.value), entry.key, annotation_map
        )
        for key in bibmark_dict:
            if key in annotation_map and key not in seen:
                seen.append(key)
    return seen
