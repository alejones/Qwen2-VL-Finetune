
"""
Script to validate that all images referenced in str_updated_train.json exist in the image folder.
Can also copy missing images from a source folder to destination folder.
"""

import json
import os
import shutil
import argparse
from pathlib import Path

def validate_and_copy_images(copy_missing=False):
    # Paths
    json_file = "/home/l-ajones/source/Qwen2-VL-Finetune/data/Export_sept_sample/str_updated_train.json"
    image_folder = "/home/l-ajones/source/Qwen2-VL-Finetune/data/Export_sept_sample/images"
    source_folder = "/home/l-ajones/laxnas/pa/test_data/RoyalMailCustoms/RoyalMail-Images/Export_CN_Labels/2024_Sept_Sample/JPG"
    destination_folder = "/home/l-ajones/source/Qwen2-VL-Finetune/data/Export_sept_sample/iod"
    
    # Load the JSON file
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} entries from {json_file}")
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file}")
        return
    
    # Check if image folder exists
    if not os.path.exists(image_folder):
        print(f"Error: Image folder not found at {image_folder}")
        return
    
    # Collect all referenced images
    referenced_images = set()
    missing_images = []
    
    for entry in data:
        if "image" in entry:
            images = entry["image"]
            if isinstance(images, list):
                referenced_images.update(images)
            elif isinstance(images, str):
                referenced_images.add(images)
    
    print(f"Found {len(referenced_images)} unique image references")
    
    # Check if each referenced image exists in the folder
    for image_name in referenced_images:
        image_path = os.path.join(image_folder, image_name)
        if not os.path.exists(image_path):
            missing_images.append(image_name)
    
    # Report results
    if missing_images:
        print(f"\n{len(missing_images)} MISSING IMAGES FOUND:")
        print("=" * 50)
        for missing_image in sorted(missing_images):
            print(missing_image)
    else:
        print("\n✓ All referenced images exist in the image folder!")
    
    # Copy missing images if requested
    if copy_missing and missing_images:
        print(f"\nCopying missing images from source to destination folder...")
        
        # Check if source and destination folders exist
        if not os.path.exists(source_folder):
            print(f"Error: Source folder not found at {source_folder}")
            return
        
        # Create destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)
        print(f"Destination folder: {destination_folder}")
        
        copied_count = 0
        not_found_in_source = []
        
        for missing_image in missing_images:
            source_path = os.path.join(source_folder, missing_image)
            destination_path = os.path.join(destination_folder, missing_image)
            
            if os.path.exists(source_path):
                try:
                    shutil.copy2(source_path, destination_path)
                    copied_count += 1
                    if copied_count <= 10:  # Show first 10 copies
                        print(f"✓ Copied: {missing_image}")
                    elif copied_count == 11:
                        print("... (showing first 10, continuing to copy remaining files)")
                except Exception as e:
                    print(f"✗ Failed to copy {missing_image}: {e}")
            else:
                not_found_in_source.append(missing_image)
        
        print(f"\nCopy Summary:")
        print(f"- Images successfully copied: {copied_count}")
        print(f"- Images not found in source folder: {len(not_found_in_source)}")
        
        if not_found_in_source:
            print(f"\nImages not found in source folder (first 10):")
            for img in sorted(not_found_in_source)[:10]:
                print(f"  {img}")
            if len(not_found_in_source) > 10:
                print(f"  ... and {len(not_found_in_source) - 10} more")
    
    print(f"\nFinal Summary:")
    print(f"- Total entries in JSON: {len(data)}")
    print(f"- Unique images referenced: {len(referenced_images)}")
    print(f"- Missing images: {len(missing_images)}")
    if copy_missing and missing_images:
        print(f"- Images copied: {copied_count}")

def main():
    parser = argparse.ArgumentParser(description='Validate and optionally copy missing images')
    parser.add_argument('--copy', action='store_true', 
                       help='Copy missing images from source to destination folder')
    
    args = parser.parse_args()
    validate_and_copy_images(copy_missing=args.copy)

if __name__ == "__main__":
    main()