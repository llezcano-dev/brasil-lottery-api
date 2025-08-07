import csv
import json
import os
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

def create_api_structure(csv_file_path: str, api_folder: str = "api"):
    """
    Create static API structure from CSV data.
    
    Args:
        csv_file_path: Path to the CSV file
        api_folder: Name of the API folder to create
    """
    
    # Get CSV filename for nested folder structure
    csv_filename = get_csv_filename_without_extension(csv_file_path)
    
    # Create API directory structure: api/CSV_NAME/contest/
    if not os.path.exists(api_folder):
        os.makedirs(api_folder)
    
    csv_folder = os.path.join(api_folder, csv_filename)
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    
    contest_folder = os.path.join(csv_folder, "contest")
    if not os.path.exists(contest_folder):
        os.makedirs(contest_folder)
    
    # Read and process CSV
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        # Try different delimiters
        sample = csvfile.read(1024)
        csvfile.seek(0)
        
        # Detect delimiter
        sniffer = csv.Sniffer()
        delimiter = ','
        try:
            delimiter = sniffer.sniff(sample).delimiter
        except:
            # Fallback to comma if detection fails
            pass
        
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        
        # Get the actual fieldnames from the first row
        fieldnames = reader.fieldnames
        if not fieldnames:
            print("Error: Could not read CSV headers")
            return
        
        print(f"Detected columns: {fieldnames}")
        
        # Process each row
        for row_num, row in enumerate(reader, 1):
            try:
                # Extract basic info
                extracao_num = clean_value(row.get('Extração', ''))
                if not extracao_num:
                    # Try alternative column names
                    extracao_num = clean_value(row.get('**Extração**', ''))
                
                data_sorteio = clean_value(row.get('Data Sorteio', ''))
                if not data_sorteio:
                    # Try alternative column names
                    data_sorteio = clean_value(row.get('**Data Sorteio**', ''))
                
                if not extracao_num or not data_sorteio:
                    print(f"Warning: Missing basic data in row {row_num}, skipping...")
                    continue
                
                # Create the response structure with new format
                api_response = {
                    "contest": extracao_num,
                    "date": parse_date_to_iso(data_sorteio),
                    "results": []
                }
                
                # Extract prizes (1º to 5º prêmio)
                for i in range(1, 6):
                    premio_key = f"{i}º prêmio"
                    valor_key = f"Valor {i}º prêmio"
                    
                    # Try with and without asterisks
                    premio_variants = [
                        premio_key,
                        f"**{i}º prêmio**",
                        f"{i}° prêmio",
                        f"**{i}° prêmio**"
                    ]
                    
                    valor_variants = [
                        valor_key,
                        f"**Valor {i}º prêmio**",
                        f"Valor {i}° prêmio",
                        f"**Valor {i}° prêmio**"
                    ]
                    
                    premio = ""
                    valor = ""
                    
                    # Find the correct column names
                    for variant in premio_variants:
                        if variant in row and row[variant]:
                            premio = parse_prize_number(row[variant])
                            break
                    
                    for variant in valor_variants:
                        if variant in row and row[variant]:
                            valor = row[variant]
                            break
                    
                    # Only add if both prize number and value exist
                    if premio and valor:
                        api_response["results"].append({
                            "index": i,
                            "value": premio,
                            "reward": parse_monetary_value(valor)
                        })
                
                # Save JSON file for this contest
                filename = f"{extracao_num}.json"
                filepath = os.path.join(contest_folder, filename)
                
                with open(filepath, 'w', encoding='utf-8') as jsonfile:
                    json.dump(api_response, jsonfile, ensure_ascii=False, indent=2)
                
                print(f"Created: {filepath}")
                
            except Exception as e:
                print(f"Error processing row {row_num}: {e}")
                continue
    
    # Create an index file listing all contests
    create_index_file(contest_folder, csv_folder, csv_filename)
    
    print(f"\nAPI generation complete! Files created in '{csv_folder}' folder.")
    print(f"Access individual contests: {csv_folder}/contest/{{number}}.json")
    print(f"Access index: {csv_folder}/index.json")

def create_index_file(contest_folder: str, csv_folder: str, csv_filename: str):
    """Create an index file with all available contests."""
    contests = []
    
    for filename in os.listdir(contest_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(contest_folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    contests.append({
                        "contest": data["contest"],
                        "date": data["date"],
                        "endpoint": f"/api/{csv_filename}/contest/{data['contest']}"
                    })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    # Sort by contest number
    contests.sort(key=lambda x: int(x["contest"]) if x["contest"].isdigit() else 0)
    
    index_data = {
        "contest_type": csv_filename,
        "total_contests": len(contests),
        "contests": contests
    }
    
    index_path = os.path.join(csv_folder, "index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

def main():
    """Main function to run the script."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python csv_to_api.py input.csv")
        print("This will create an 'api' folder with JSON files for each contest.")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
    
    print(f"Processing CSV file: {csv_file}")
    create_api_structure(csv_file)

if __name__ == "__main__":
    main()
