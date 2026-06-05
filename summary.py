#!/usr/bin/env python3
import os
from pathlib import Path

summary_path = Path(os.environ["GITHUB_STEP_SUMMARY"])
repo = os.environ["REPO"]
run_id = os.environ["RUN_ID"]

# Extract owner and repo name
owner, repo_name = repo.split("/")

# GitHub Pages base URL
pages_url = f"https://{owner}.github.io/{repo_name}/run-{run_id}"

# Manifest data
manifest = [
    ("Airfoil Pressure Profile Preview", "airfoil_pressure_profile.png"),
    ("Wing Pressure Flow Field Preview", "wing_flow_field_p_3d.png"),
]

with summary_path.open("a", encoding="utf-8") as summary:
    summary.write("## Test Figure Previews\n\n")

    for title, filename in manifest:
        image_url = f"{pages_url}/{filename}"
        summary.write(f"### {title}\n\n")
        summary.write(f"![{title}]({image_url})\n\n")
        summary.write(f"[View on GitHub Pages]({image_url})\n\n")
