"""
Script to fix image tags in training JSON files.

This script ensures that the number of <image> tags in the user's value
matches the number of images in the image array for each conversation.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def fix_image_tags(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fix image tags in training data to match the number of images.

    Args:
        data: List of training examples with conversations

    Returns:
        Fixed training data with correct number of image tags
    """
    fixed_data = []

    for item in data:
        if "image" not in item or "conversations" not in item:
            fixed_data.append(item)
            continue

        num_images = len(item["image"])
        fixed_item = item.copy()
        fixed_conversations = []

        for conv in item["conversations"]:
            if conv.get("from") in ["user", "human"]:
                # Count existing image tags
                current_tags = conv["value"].count("<image>")

                if current_tags != num_images:
                    # Remove existing image tags
                    value_without_tags = conv["value"].replace("<image>", "").strip()

                    # Add correct number of image tags at the beginning
                    image_tags = "<image>\n" * num_images
                    new_value = image_tags + value_without_tags

                    fixed_conv = conv.copy()
                    fixed_conv["value"] = new_value
                    fixed_conversations.append(fixed_conv)

                    print(
                        f"Fixed item {item.get('id', 'unknown')}: {current_tags} -> {num_images} image tags"
                    )
                else:
                    fixed_conversations.append(conv)
            else:
                fixed_conversations.append(conv)

        fixed_item["conversations"] = fixed_conversations
        fixed_data.append(fixed_item)

    return fixed_data


def main() -> None:
    """Main function to process training JSON file."""
    parser = argparse.ArgumentParser(
        description="Fix image tags in training JSON to match number of images"
    )
    parser.add_argument("input_file", type=Path, help="Path to input JSON file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to output JSON file (default: overwrites input file)",
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup of original file"
    )

    args = parser.parse_args()

    if not args.input_file.exists():
        print(f"Error: Input file {args.input_file} does not exist")
        return

    # Create backup if requested
    if args.backup:
        backup_path = args.input_file.with_suffix(f"{args.input_file.suffix}.backup")
        backup_path.write_text(args.input_file.read_text())
        print(f"Backup created: {backup_path}")

    # Load JSON data
    try:
        with args.input_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}")
        return
    except Exception as e:
        print(f"Error reading {args.input_file}: {e}")
        return

    # Fix image tags
    fixed_data = fix_image_tags(data)

    # Write output
    output_file = args.output or args.input_file
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        print(f"Fixed JSON written to: {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")


if __name__ == "__main__":
    main()
