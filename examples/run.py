"""Example script: call bibmark to generate citation files."""

from bibmark import generate_citations

bib_files = [
    "huang2022kidney.bib",
]

generate_citations(
    bib_files=bib_files,
    my_name="Wenrui Wu",
    annotation_map={
        "first":         "#",
        "corresponding": "*",
    },
    legend_labels={
        "first":         "Co-first author",
        "corresponding": "Corresponding author",
    },
    superscript=True,
    output_dir="output",
)

print("Done. Output files are in examples/output/")
