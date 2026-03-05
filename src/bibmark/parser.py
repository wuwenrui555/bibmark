"""
Parse .bib files and bibmark annotation fields.
"""

import re
import sys

import bibtexparser


def parse_bib_file(path: str):
    """
    Parse a single .bib file and return the first entry.

    Parameters
    ----------
    path : str
        Path to the .bib file.

    Returns
    -------
    bibtexparser.model.Entry
        The first entry found in the file.

    Raises
    ------
    ValueError
        If no entries are found in the file.
    """
    library = bibtexparser.parse_file(path)
    if library.failed_blocks:
        print(f"WARNING: failed to parse some blocks in {path}", file=sys.stderr)
    if not library.entries:
        raise ValueError(f"No entries found in {path}")
    return library.entries[0]


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
