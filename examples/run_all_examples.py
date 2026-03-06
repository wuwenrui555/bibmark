"""
Run all per-person example scripts and generate their citation outputs.

Usage (from project root):
    uv run examples/run_all_examples.py
"""

import subprocess
import sys
from pathlib import Path

examples_dir = Path(__file__).parent

person_scripts = sorted(
    p / "run.py"
    for p in examples_dir.iterdir()
    if p.is_dir() and (p / "run.py").exists()
)

for script in person_scripts:
    print(f"--- {script.parent.name} ---", flush=True)
    result = subprocess.run(["uv", "run", str(script)], capture_output=False)
    if result.returncode != 0:
        print(f"Error running {script}", file=sys.stderr)
