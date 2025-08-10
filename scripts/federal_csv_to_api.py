import csv
import json
import os
import shutil
from datetime import datetime

def clean_value(value: str) -> str:
    """Clean and normalize string values."""
    return value.strip() if value else ""

def parse_monetary_value(value: str) -> float:
    """Parse monetary values and convert to float."""
    if not value:
        return 0.0
    
    # Remove R$, spaces, and convert comma to dot for decimal
    clean_value_str = value.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    
    try:
        return float(clean_value_str)
    except ValueError:
        return 0.0

def parse_str_to_int(value: str) -> int:
    return int(value) if value.isdigit() else 0

def parse_date_to_iso(date_str: str) -> str:
    """Convert date from DD/MM/YYYY to ISO format YYYY-MM-DD."""
    if not date_str:
        return ""
    
    try:
        # Parse DD/MM/YYYY format
        date_obj = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        # Return ISO format
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        # If parsing fails, return original
        return date_str

def parse_prize_number(value: str) -> str:
    """Parse prize numbers, removing extra formatting."""
    return clean_value(value)

def get_csv_filename_without_extension(csv_path: str) -> str:
    """Extract filename without extension from CSV path."""
    filename = os.path.basename(csv_path)
    return os.path.splitext(filename)[0]

import os
import csv
import json

def ensure_dir_exists(path: str):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def detect_csv_delimiter(csvfile) -> str:
    """Detect CSV delimiter by sniffing the sample of the file."""
    sample = csvfile.read(1024)
    csvfile.seek(0)
    sniffer = csv.Sniffer()
    try:
        return sniffer.sniff(sample).delimiter
    except csv.Error:
        return ','  # Default delimiter

def get_prize_variants(i: int):
    """Generate possible variants for prize and value column names."""
    premio_variants = [
        f"{i}º prêmio",
        f"**{i}º prêmio**",
        f"{i}° prêmio",
        f"**{i}° prêmio**"
    ]
    valor_variants = [
        f"Valor {i}º prêmio",
        f"**Valor {i}º prêmio**",
        f"Valor {i}° prêmio",
        f"**Valor {i}° prêmio**"
    ]
    return premio_variants, valor_variants

def extract_basic_info(row: dict):
    """Extract essential draw information from a CSV row."""
    extracao_num = clean_value(row.get('Extração', '')) or clean_value(row.get('**Extração**', ''))
    data_sorteio = clean_value(row.get('Data Sorteio', '')) or clean_value(row.get('**Data Sorteio**', ''))
    return extracao_num, data_sorteio

def extract_prizes(row: dict):
    """Extract prizes info from a CSV row."""
    results = []
    for i in range(1, 6):
        premio_variants, valor_variants = get_prize_variants(i)
        premio = ""
        valor = ""

        for variant in premio_variants:
            if variant in row and row[variant]:
                premio = parse_prize_number(row[variant])
                break

        for variant in valor_variants:
            if variant in row and row[variant]:
                valor = row[variant]
                break

        if premio and valor:
            results.append({
                "position": i,
                "winningNumber": premio,
                "prizeAmount": parse_monetary_value(valor)
            })
    return results

def process_row(row_num: int, row: dict, draw_folder: str):
    """Process single CSV row and save JSON file."""
    try:
        extracao_num, data_sorteio = extract_basic_info(row)
        if not extracao_num or not data_sorteio:
            print(f"Warning: Missing basic data in row {row_num}, skipping...")
            return

        api_response = {
            "drawNumber": parse_str_to_int(extracao_num),
            "date": parse_date_to_iso(data_sorteio),
            "results": extract_prizes(row)
        }

        filename = f"{extracao_num}.json"
        filepath = os.path.join(draw_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(api_response, jsonfile, ensure_ascii=False, indent=2)
        print(f"Created: {filepath}")

    except Exception as e:
        print(f"Error processing row {row_num}: {e}")

def create_api_structure(csv_file_path: str, api_folder: str = "v1/lotteries"):
    """
    Create static API structure from CSV data.

    Args:
        csv_file_path: Path to the CSV file
        api_folder: Name of the API folder to create
    """
    csv_filename = get_csv_filename_without_extension(csv_file_path)

    # Create directory structure
    ensure_dir_exists(api_folder)
    csv_folder = os.path.join(api_folder, csv_filename)
    ensure_dir_exists(csv_folder)
    draw_folder = os.path.join(csv_folder, "draws")
    ensure_dir_exists(draw_folder)

    # Read and process CSV
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        delimiter = detect_csv_delimiter(csvfile)
        reader = csv.DictReader(csvfile, delimiter=delimiter)

        fieldnames = reader.fieldnames
        if not fieldnames:
            print("Error: Could not read CSV headers")
            return

        print(f"Detected columns: {fieldnames}")

        last_file_path = None
        for row_num, row in enumerate(reader, 1):
            # Process the row and get the path to the created JSON file
            extracao_num, _ = extract_basic_info(row)
            if extracao_num:
                last_file_path = os.path.join(draw_folder, f"{extracao_num}.json")

            process_row(row_num, row, draw_folder)

    # Copy last row's JSON to latest.json
    if last_file_path and os.path.exists(last_file_path):
        latest_path = os.path.join(draw_folder, "latest.json")
        shutil.copyfile(last_file_path, latest_path)
        print(f"Copied latest draw JSON to: {latest_path}")

    print(f"\nAPI generation complete! Files created in '{csv_folder}' folder.")
    print(f"Access individual draws: {csv_folder}/draws/{{number}}.json")
    print(f"Access latest draw: {csv_folder}/draws/latest.json")
    print(f"Access index: {csv_folder}/index.json")

def main():
    """Main function to run the script."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python csv_to_api.py input.csv")
        print("This will create an 'v1' folder with JSON files for each draw.")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
    
    print(f"Processing CSV file: {csv_file}")
    create_api_structure(csv_file)

if __name__ == "__main__":
    main()
