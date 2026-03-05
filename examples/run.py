"""
Generate citation files from publications.bib.
"""

from bibmark import generate_citations

generate_citations(
    bib_file="publications.bib",
    cite_keys=[
        "feng2024timerestricted",
        "gao2022bench",
        "huang2022single",
        "huang2025effect",
        "li2022association",
        "li2023genotype",
        "wang2022combining",
        "wu2022epletpredicted",
        "zhang2023outcome",
        "zhang2024ccl19producing",
        "zhang2024effectiveness",
    ],
    my_name="Wenrui Wu",
    annotation_map={
        "first": "#",
        "corresponding": "*",
    },
    superscript=True,
    output_dir="output",
)

print("Done. Output files are in examples/output/")
