"""
Generate citation files from publication.bib.
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
    bib_file=here / "publication.bib",
    cite_keys={
        "2024": [
            "duan2024gdf9his209glnfster6",
            "wei2024ddr1",
        ],
        "2023": [
            "niu2023antiinflammatory",
            "wei2023ipscsderived",
        ],
        "2022": [
            "yao2022nestindependent",
            "wang2022nestina",
            "wang2022nestin",
        ],
        "2021": [
            "wang2021inhibition",
        ],
        "2018": [
            "wang2018cell",
        ],
    },
    my_name="Boyan Wang",
    annotation_map={
        "first": "#",
        "corresponding": "*",
    },
    superscript=True,
    output_dir=output_dir,
)

print(f"Done. Output files are in /{output_dir.relative_to(project_root)}")
