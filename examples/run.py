"""
Generate citation files from publications.bib.
"""

from bibmark import generate_citations

generate_citations(
    bib_file="publications.bib",
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
    output_dir="output",
)

print("Done. Output files are in examples/output/")
