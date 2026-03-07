"""
Generate citation files from publications.bib.
"""

from pathlib import Path

from bibmark import generate_citations

here = Path(__file__).parent


def find_project_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "pyproject.toml").exists():
            return p
    return start


project_root = find_project_root(here)
output_dir = here / "output"

generate_citations(
    bib_file=here / "publications.bib",
    cite_keys={
        "2026": [
            "li2026development",
        ],
        "2023": [
            "zhao2023adaptive",
            "ning2023mutualassistance",
        ],
    },
    my_name="Zhangxin Zhao",
    annotation_map={
        "first": "#",
        "corresponding": "*",
    },
    superscript=True,
    output_dir=output_dir,
)

print(f"Done. Output files are in /{output_dir.relative_to(project_root)}")
