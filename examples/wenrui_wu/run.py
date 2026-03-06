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
        "2025": [
            "huang2025effect",
        ],
        "2024": [
            "zhang2024ccl19producing",
            "zhang2024effectiveness",
        ],
        "2023": [
            "zhang2023outcome",
            "li2023genotype",
        ],
        "2022": [
            "wu2022epletpredicted",
            "wang2022combining",
            "huang2022single",
            "gao2022bench",
            "li2022association",
        ],
    },
    my_name="Wenrui Wu",
    annotation_map={
        "first": "#",
        "corresponding": "*",
    },
    superscript=True,
    output_dir=output_dir,
)

print(f"Done. Output files are in /{output_dir.relative_to(project_root)}")
