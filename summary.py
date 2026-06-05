#!/usr/bin/env python3
import base64
import json
import os
import re
import urllib.request
import zipfile
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
                artifacts[artifact["name"]] = {
                    "id": artifact["id"],
                    "url": f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact['id']}/zip"
                }
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
            filename = Path(image_path_str).name
            try:
                # Download artifact zip and extract image
                zip_url = artifact_url["url"]
                req = urllib.request.Request(
                    zip_url,
                    headers={"Authorization": f"Bearer {token}"},
                )
                with urllib.request.urlopen(req) as response:
                    zip_data = response.read()

                # Extract image from zip
                with zipfile.ZipFile(__import__('io').BytesIO(zip_data)) as zf:
                    # Find the image file in the zip
                    for file_info in zf.filelist:
                        if file_info.filename.endswith(filename):
                            image_data = zf.read(file_info.filename)
                            # Embed as base64
                            b64 = base64.b64encode(image_data).decode()
                            summary.write(f"![{title}](data:image/png;base64,{b64})\n\n")
                            break
            except Exception as e:
                ui_url = f"https://github.com/{repo}/actions/runs/{run_id}"
                summary.write(f"✅ **[Download {filename}]({ui_url})**\n")
                summary.write(f"(Could not embed: {e})\n\n")
        else:
            summary.write(f"❌ Not found: {artifact_name}\n\n")

    summary.write(f"\n**Debug info:**\n")
    summary.write(f"Found {len(artifact_urls)} artifacts\n")
