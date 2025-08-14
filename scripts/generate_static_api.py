#!/usr/bin/env python3
"""
CSV to JSON Converter
Converts CSV files to individual JSON files (one per row) with configurable mapping functions.
"""

import csv
import json
import os
import sys
import shutil
from typing import Dict, Any, List, Callable
from mappers.federal import federal_mapping
from mappers.default import default_mapping

# Mapping registry
MAPPING_FUNCTIONS: Dict[str, Callable[[List[str], List[str]], Dict[str, Any]]] = {
    "default": default_mapping,
    "federal": federal_mapping,
}

def convert_csv_to_json(csv_file_path: str, output_dir: str, mapping_type: str = "default") -> None:
    """
    Convert CSV file to individual JSON files.
    
    Args:
        csv_file_path: Path to the input CSV file
        output_dir: Directory to save JSON files
        mapping_type: Type of mapping function to use
    """
    # Validate inputs
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    if mapping_type not in MAPPING_FUNCTIONS:
        raise ValueError(f"Unknown mapping type: {mapping_type}. Available: {list(MAPPING_FUNCTIONS.keys())}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the mapping function
    mapping_func = MAPPING_FUNCTIONS[mapping_type]
    
    # Process CSV file
    processed_count = 0
    error_count = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: Could not read CSV headers")
                return

            print(f"Processing CSV with {len(fieldnames)} columns...")
            print(f"Headers: {fieldnames}")

            last_file_path = None

            # Process each row
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Apply mapping function
                    json_data = mapping_func(row_num, row)
                    
                    # Extract _ID and remove it from the data to save
                    file_id = json_data.pop("_ID", f"row_{row_num}")

                    # Save JSON file
                    output_file = os.path.join(output_dir, f"{file_id}.json")
                    last_file_path = output_file
                    with open(output_file, 'w', encoding='utf-8') as jsonfile:
                        json.dump(json_data, jsonfile, ensure_ascii=False, indent=2)
                    
                    processed_count += 1
                    
                    # Progress indicator for large files
                    if processed_count % 100 == 0:
                        print(f"Processed {processed_count} rows...")
                        
                except Exception as e:
                    error_count += 1
                    print(f"Error processing row {row_num}: {e}")
                    continue

            # Copy last row's JSON to latest.json
            if last_file_path and os.path.exists(last_file_path):
                latest_path = os.path.join(output_dir, "latest.json")
                shutil.copyfile(last_file_path, latest_path)
                print(f"Copied latest draw JSON to: {latest_path}")

            print(f"\nAPI generation complete! Files created in '{output_dir}' folder.")
            print(f"Access individual draws: {output_dir}/{{number}}.json")
            print(f"Access latest draw: {output_dir}/latest.json")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    print(f"\nConversion complete!")
    print(f"Successfully processed: {processed_count} rows")
    print(f"Errors encountered: {error_count} rows")
    print(f"Output directory: {output_dir}")

def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 3:
        print("Usage: python csv_to_json.py <csv_file_path> <output_dir> <mapping_type>")
        print(f"Available mapping types: {list(MAPPING_FUNCTIONS.keys())}")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    output_dir = sys.argv[2]
    mapping_type = sys.argv[3] if len(sys.argv) > 3 else "default"
    
    try:
        convert_csv_to_json(csv_file_path, output_dir, mapping_type)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
