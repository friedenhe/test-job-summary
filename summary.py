#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from pathlib import Path

summary_path = Path(os.environ["GITHUB_STEP_SUMMARY"])
repo = os.environ["GITHUB_REPOSITORY"]
run_id = os.environ["GITHUB_RUN_ID"]
token = os.environ["GITHUB_TOKEN"]

# Manifest data
manifest = [
    ("Airfoil Pressure Profile Preview", "airfoil_cfd_rae2822_aoa1_1cpu_0000/plots/airfoil_pressure_profile.png"),
    ("Wing Pressure Flow Field Preview", "wing_cfd_wing_s809_naca2412_aoa1_0000/plots/wing_flow_field_p_3d.png"),
]

def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:50] or "figure-preview"

def fetch_artifact_urls():
    import time
    api_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100"
    for attempt in range(5):
        try:
            request = urllib.request.Request(
                api_url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            with urllib.request.urlopen(request) as response:
                payload = json.load(response)
            artifacts = {}
            for artifact in payload.get("artifacts", []):
                artifacts[artifact["name"]] = f"https://github.com/{repo}/actions/runs/{run_id}/artifacts/{artifact['id']}"
            if artifacts:
                return artifacts
            if attempt < 4:
                print(f"No artifacts yet, retrying... ({attempt+1}/5)", flush=True)
                time.sleep(2)
        except Exception as e:
            print(f"API error: {e}", flush=True)
            if attempt < 4:
                time.sleep(2)
    return {}

with summary_path.open("a", encoding="utf-8") as summary:
    summary.write("## Test Figure Previews\n\n")
    artifact_urls = fetch_artifact_urls()

    for index, (title, image_path_str) in enumerate(manifest, start=1):
        summary.write(f"### {title}\n")
        summary.write(f"Source: `{image_path_str}`\n\n")

        artifact_name = f"llm-preview-{index:03d}-{slugify(title)}-{run_id}"
        artifact_url = artifact_urls.get(artifact_name, "")

        if artifact_url:
            # Construct direct download URL for the artifact
            download_url = f"{artifact_url}/download"
            summary.write(f"![{title}]({download_url})\n\n")
            summary.write(f"[View artifact]({artifact_url})\n\n")
        else:
            summary.write(f"❌ Not found: {artifact_name}\n\n")

    summary.write(f"\n**Debug info:**\n")
    summary.write(f"Found {len(artifact_urls)} artifacts:\n")
    for name in sorted(artifact_urls.keys()):
        summary.write(f"- {name}\n")
