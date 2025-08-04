#!/usr/bin/env python3
"""
Script to split a JSON dataset into training, validation, and test sets.
Filters entries based on 'checked' and 'use_in_training' fields.
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Any


def load_json_data(file_path: Path) -> List[Dict[str, Any]]:
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_entries(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter entries based on 'checked' and 'use_in_training' fields."""
    filtered = []
    for entry in data:
        if entry.get('checked', False) and entry.get('use_in_training', False):
            # Create new entry without the extra fields
            clean_entry = {
                'id': entry['id'],
                'image': entry['image'],
                'conversations': entry['conversations']
            }
            filtered.append(clean_entry)
    return filtered


def split_data(data: List[Dict[str, Any]], train_pct: float, val_pct: float, test_pct: float) -> tuple:
    """Split data into train, validation, and test sets."""
    if abs(train_pct + val_pct + test_pct - 100.0) > 0.001:
        raise ValueError("Percentages must sum to 100")
    
    # Shuffle data for random splits
    random.shuffle(data)
    
    total = len(data)
    train_size = int(total * train_pct / 100)
    val_size = int(total * val_pct / 100)
    
    train_data = data[:train_size]
    val_data = data[train_size:train_size + val_size]
    test_data = data[train_size + val_size:]
    
    return train_data, val_data, test_data


def save_json_data(data: List[Dict[str, Any]], file_path: Path) -> None:
    """Save data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Split JSON dataset into train/val/test sets')
    parser.add_argument('input_file', type=Path, help='Input JSON file path')
    parser.add_argument('--train-pct', type=float, default=85.0, 
                       help='Training set percentage (default: 80.0)')
    parser.add_argument('--val-pct', type=float, default=0.0,
                       help='Validation set percentage (default: 0.0)')
    parser.add_argument('--test-pct', type=float, default=15.0,
                       help='Test set percentage (default: 10.0)')
    parser.add_argument('--output-dir', type=Path, default=None,
                       help='Output directory (default: same as input file)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducible splits (default: 42)')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    # Validate input file
    if not args.input_file.exists():
        print(f"Error: Input file {args.input_file} does not exist")
        return 1
    
    # Set output directory
    output_dir = args.output_dir if args.output_dir else args.input_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load and filter data
        print(f"Loading data from {args.input_file}")
        data = load_json_data(args.input_file)
        print(f"Total entries: {len(data)}")
        
        filtered_data = filter_entries(data)
        print(f"Filtered entries (checked=True, use_in_training=True): {len(filtered_data)}")
        
        if not filtered_data:
            print("No entries match the filtering criteria")
            return 1
        
        # Split data
        train_data, val_data, test_data = split_data(
            filtered_data, args.train_pct, args.val_pct, args.test_pct
        )
        
        print(f"Split sizes - Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
        
        # Save splits
        train_file = output_dir / 'train.json'
        val_file = output_dir / 'val.json'
        test_file = output_dir / 'test.json'
        
        save_json_data(train_data, train_file)
        save_json_data(val_data, val_file)
        save_json_data(test_data, test_file)
        
        print(f"Saved train set to: {train_file}")
        print(f"Saved validation set to: {val_file}")
        print(f"Saved test set to: {test_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())