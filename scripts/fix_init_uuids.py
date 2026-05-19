#!/usr/bin/env python3
"""
Fix init.json: replace all short IDs with real UUIDs while preserving referential integrity.
"""
import json
import uuid
from pathlib import Path

INIT_PATH = Path(__file__).parent.parent / "backend" / "data" / "init.json"

def collect_ids(obj, ids: set):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "id" and isinstance(v, str):
                ids.add(v)
            elif k == "blocked_by" and isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        ids.add(item)
            else:
                collect_ids(v, ids)
    elif isinstance(obj, list):
        for item in obj:
            collect_ids(item, ids)

def replace_ids(obj, mapping: dict):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == "id" and isinstance(v, str) and v in mapping:
                new_obj[k] = mapping[v]
            elif k == "blocked_by" and isinstance(v, list):
                new_obj[k] = [mapping.get(item, item) for item in v]
            elif isinstance(v, str) and v in mapping:
                new_obj[k] = mapping[v]
            else:
                new_obj[k] = replace_ids(v, mapping)
        return new_obj
    elif isinstance(obj, list):
        return [replace_ids(item, mapping) for item in obj]
    return obj

def main():
    with open(INIT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    ids = set()
    collect_ids(data, ids)
    print(f"Found {len(ids)} unique IDs to replace: {sorted(ids)}")

    mapping = {old: str(uuid.uuid4()) for old in ids}
    new_data = replace_ids(data, mapping)

    # Write back with pretty formatting
    with open(INIT_PATH, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Updated {INIT_PATH} with UUIDs.")

    # Save mapping for reference
    mapping_path = Path(__file__).parent / "uuid_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"Mapping saved to {mapping_path}")

if __name__ == "__main__":
    main()
