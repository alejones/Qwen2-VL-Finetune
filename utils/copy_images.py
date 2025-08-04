import argparse
import json
import shutil
from pathlib import Path
from typing import List, Set

from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Process images from JSON and copy them to an output folder.",
        add_help=False,
    )

    # Add custom help message
    parser.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit"
    )

    # Define arguments with both short and long flags
    parser.add_argument(
        "-i",
        "--input_image_folder",
        type=Path,
        required=True,
        help="The path to the input image folder.",
    )
    parser.add_argument(
        "-j", "--json_file", type=Path, required=True, help="The path to the JSON file."
    )
    parser.add_argument(
        "-o",
        "--output_folder",
        type=Path,
        required=True,
        help="The path to the output folder.",
    )
    parser.add_argument(
        "-a",
        "--all_sides",
        action="store_true",
        help="Copy all related image files (e.g., _TO, _BM) for each image",
    )

    return parser.parse_args()


def get_base_filename(filename: str) -> str:
    """Extract the middle part of the filename by removing the first part before the first
    underscore and the last part after the final underscore.

    For example, 'LB808077461GB_1_1529449791_20240924050421_TO.jpg' becomes
    '1_1529449791_20240924050421'

    Args:
        filename: The original filename

    Returns:
        str: The middle part of the filename
    """
    # First remove the last part after the final underscore
    parts = filename.rsplit("_", 1)
    base = parts[0] if len(parts) > 1 else filename

    # Then remove the first part before the first underscore
    if "_" in base:
        _, rest = base.split("_", 1)
        return rest

    return base


def find_related_images(base_name: str, input_folder: Path) -> List[Path]:
    """Find all related image files that start with the base name.

    Args:
        base_name: The base name to search for
        input_folder: The folder to search in

    Returns:
        List[Path]: A list of paths to related image files
    """
    return list(input_folder.glob(f"*{base_name}*.jpg"))


def process_json_and_copy_images(
    input_image_folder: Path,
    json_file: Path,
    output_folder: Path,
    all_sides: bool = False,
) -> None:
    """Process a JSON file and copy the specified images to the output folder.

    Args:
        input_image_folder: Path to the folder containing input images
        json_file: Path to the JSON file with image information
        output_folder: Path to the output folder where images will be copied
        all_sides: Whether to copy all related image files
    """
    # Ensure the output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)

    with open(json_file, "r") as f:
        data = json.load(f)

    total_images = len(data)
    copied_images: Set[Path] = set()

    for item in tqdm(data, total=total_images, desc="Processing Images", unit="image"):
        # If all_sides flag is set, copy related images
        if all_sides:
            base_name = get_base_filename(item["image"])
            related_images = find_related_images(
                base_name, input_folder=input_image_folder
            )

            for related_image in related_images:
                if related_image not in copied_images:
                    dest = output_folder / related_image.name
                    shutil.copy(related_image, dest)
                    copied_images.add(related_image)
        else:
            image_path = input_image_folder / item["image"]

            if not image_path.exists():
                print(f"Image not found: {image_path}")
                continue

            # Copy the original image
            destination_path = output_folder / image_path.name
            if image_path not in copied_images:
                shutil.copy(image_path, destination_path)
                copied_images.add(image_path)

    print(f"Copied {len(copied_images)} images to {output_folder}")


if __name__ == "__main__":
    args = parse_args()
    process_json_and_copy_images(
        args.input_image_folder, args.json_file, args.output_folder, args.all_sides
    )
