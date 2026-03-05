"""
Parse .bib files and bibmark annotation fields.
"""

import re
import sys

import bibtexparser


def parse_bib(path: str, keys: list[str]) -> list:
    """
    Parse a .bib file and return entries in the order specified by keys.

    Parameters
    ----------
    path : str
        Path to the .bib file.
    keys : list[str]
        Cite keys specifying which entries to return and in what order.

    Returns
    -------
    list[bibtexparser.model.Entry]
        Entries in the same order as keys. Missing keys are warned and skipped.

    Raises
    ------
    ValueError
        If the file contains no entries.
    """
    library = bibtexparser.parse_file(path)
    if library.failed_blocks:
        print(f"WARNING: failed to parse some blocks in {path}", file=sys.stderr)
    if not library.entries:
        raise ValueError(f"No entries found in {path}")
    entries_by_key = {e.key: e for e in library.entries}
    result = []
    for key in keys:
        if key not in entries_by_key:
            print(f"WARNING: cite key '{key}' not found in {path}", file=sys.stderr)
        else:
            result.append(entries_by_key[key])
    return result


def parse_bibmark_field(value: str, cite_key: str, annotation_map: dict) -> dict:
    """
    Parse a bibmark field string into a structured dict.

    Parameters
    ----------
    value : str
        Raw bibmark field value, e.g. ``"first: {1, 2}, corresponding: {3, 4}"``.
    cite_key : str
        The cite key of the entry, used in warning messages.
    annotation_map : dict
        Maps known bibmark keys to symbols. Unknown keys trigger a warning.

    Returns
    -------
    dict
        Mapping of role name to list of 1-based author indices,
        e.g. ``{"first": [1, 2], "corresponding": [3, 4]}``.
    """
    result = {}
    pattern = r"(\w+)\s*:\s*\{([^}]*)\}"
    for match in re.finditer(pattern, value):
        key = match.group(1)
        raw = match.group(2)
        indices = [int(x.strip()) for x in raw.split(",") if x.strip()]
        if key not in annotation_map:
            known = ", ".join(annotation_map.keys())
            print(
                f"WARNING: unknown bibmark key '{key}' in {cite_key} "
                f"— recommended keys are: {known}",
                file=sys.stderr,
            )
        result[key] = indices
    return result
