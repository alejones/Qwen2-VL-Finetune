#!/usr/bin/env python3
"""Script to convert JSON strings back to dict values in training data."""

import argparse
import json
from pathlib import Path
from typing import Any


def convert_string_values_to_dict(data: Any) -> Any:
    """Recursively convert JSON string values back to dicts while preserving other types."""
    if isinstance(data, str):
        # Try to parse as JSON, return original string if it fails
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data
    elif isinstance(data, list):
        # Recursively process list items
        return [convert_string_values_to_dict(item) for item in data]
    else:
        # Return other types as-is
        return data


def process_training_data(input_file: Path, output_file: Path) -> None:
    """Process training data file to convert string values back to dicts."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in input file: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Process the data
    if isinstance(data, list):
        processed_data = []
        for entry in data:
            if isinstance(entry, dict) and "conversations" in entry:
                processed_entry = entry.copy()
                processed_conversations = []

                for conversation in entry["conversations"]:
                    processed_conversation = conversation.copy()
                    # Convert string values back to dicts
                    processed_conversation["value"] = convert_string_values_to_dict(
                        conversation["value"]
                    )
                    processed_conversations.append(processed_conversation)

                processed_entry["conversations"] = processed_conversations
                processed_data.append(processed_entry)
            else:
                processed_data.append(entry)
    else:
        # Handle single entry case
        processed_data = convert_string_values_to_dict(data)

    # Write processed data to output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully processed {input_file} -> {output_file}")


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Convert JSON strings back to dict values in training data"
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input_file",
        type=Path,
        required=True,
        help="Path to input JSON file",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        type=Path,
        required=True,
        help="Path to output JSON file",
    )
    parser.add_argument(
        "-f",
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it exists",
    )

    args = parser.parse_args()

    # Validate input file exists
    if not args.input_file.exists():
        print(f"Error: Input file does not exist: {args.input_file}")
        return

    # Check if output file exists
    if args.output_file.exists() and not args.overwrite:
        print(f"Error: Output file already exists: {args.output_file}")
        print("Use --overwrite flag to overwrite existing file")
        return

    try:
        process_training_data(args.input_file, args.output_file)
    except Exception as e:
        print(f"Error processing file: {e}")


if __name__ == "__main__":
    main()