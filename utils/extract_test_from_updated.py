#!/usr/bin/env python3
"""
Script to extract test set IDs from updated ground truth file.
Copies data from Export_2024_Sept_Sample.json that matches test.json IDs to updated_test_str.json.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Set


def load_json_data(file_path: Path) -> List[Dict[str, Any]]:
    """Load JSON data from file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_data(data: List[Dict[str, Any]], file_path: Path) -> None:
    """Save data to JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_test_ids(test_data: List[Dict[str, Any]]) -> Set[str]:
    """Extract all IDs from test data."""
    return {entry["id"] for entry in test_data}


def find_matching_entries(
    updated_data: List[Dict[str, Any]], test_ids: Set[str]
) -> tuple[List[Dict[str, Any]], Set[str]]:
    """Find entries in updated data that match test IDs."""
    matched_entries = []
    found_ids = set()

    for entry in updated_data:
        entry_id = entry.get("id")
        if entry_id in test_ids:
            # Create clean entry following split_dataset.py pattern
            clean_entry = {
                "id": entry["id"],
                "image": entry["image"],
                "conversations": entry["conversations"],
            }
            matched_entries.append(clean_entry)
            found_ids.add(entry_id)

    missing_ids = test_ids - found_ids
    return matched_entries, missing_ids


def main():
    # File paths
    test_file = Path("data/Export_sept_sample/train_str.json")
    updated_file = Path("data/Export_sept_sample/output.json")
    output_file = Path("data/Export_sept_sample/updated_train_str.json")

    # Validate input files exist
    if not test_file.exists():
        print(f"Error: Test file {test_file} does not exist")
        return 1

    if not updated_file.exists():
        print(f"Error: Updated file {updated_file} does not exist")
        return 1

    try:
        # Load data
        print(f"Loading test set from {test_file}")
        test_data = load_json_data(test_file)
        print(f"Test set contains {len(test_data)} entries")

        print(f"Loading updated ground truth from {updated_file}")
        updated_data = load_json_data(updated_file)
        print(f"Updated ground truth contains {len(updated_data)} entries")

        # Extract test IDs
        test_ids = extract_test_ids(test_data)
        print(f"Extracted {len(test_ids)} unique test IDs")

        # Find matching entries
        matched_entries, missing_ids = find_matching_entries(updated_data, test_ids)

        # Report results
        print(f"Found {len(matched_entries)} matching entries in updated file")

        if missing_ids:
            print(f"WARNING: {len(missing_ids)} test IDs not found in updated file:")
            for missing_id in sorted(missing_ids):
                print(f"  - {missing_id}")
        else:
            print("All test IDs found in updated file!")

        # Save results
        save_json_data(matched_entries, output_file)
        print(f"Saved {len(matched_entries)} entries to {output_file}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
