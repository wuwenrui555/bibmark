"""Example script: call bibmark to generate citation files."""

from bibmark import generate_citations

generate_citations(
    bib_file="publications.bib",
    cite_keys=[
        "huang2022kidney",
    ],
    my_name="Wenrui Wu",
    annotation_map={
        "first":         "#",
        "corresponding": "*",
    },
    superscript=True,
    output_dir="output",
)

print("Done. Output files are in examples/output/")
