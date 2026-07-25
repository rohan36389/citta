import os
import json
from pathlib import Path

registry_dir = Path("backend/knowledge/registry")
files = sorted(list(registry_dir.glob("*.json")))

for f in files:
    print(f"\nFile: {f.name}")
    try:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                print("  Keys:", list(data.keys()))
                if "metadata" in data:
                    print("  Metadata Keys:", list(data["metadata"].keys()))
                if "entities" in data:
                    print("  Entities count:", len(data["entities"]))
                    if len(data["entities"]) > 0:
                        print("  First entity keys:", list(data["entities"][0].keys()))
            else:
                print("  Type: List, len:", len(data))
                if len(data) > 0:
                    print("  First item keys:", list(data[0].keys()))
    except Exception as e:
        print("  Error:", e)
