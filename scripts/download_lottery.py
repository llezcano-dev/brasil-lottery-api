#!/usr/bin/env python3
import requests
import sys
import os
import pyexcel as pe

API_SLUG_MAP = {
    "federal": "Federal",
    "megasena": "Mega-Sena",
    "lotofacil": "Lotofácil",
    "quina": "Quina",
    "lotomania": "Lotomania",
    "timemania": "Timemania",
    "duplasena": "Dupla Sena",
    "loteca": "Loteca",
    "diadesorte": "Dia de Sorte",
    "supersete": "Super Sete",
    "maismilionaria": "+Milionária",
}

def xlsx_to_csv(input_file, output_file):
    # Load the spreadsheet data
    sheet = pe.get_sheet(file_name=input_file)
    # Save it as CSV
    sheet.save_as(output_file)

def download_lottery_xlsx(api_slug: str, filename: str, output_dir: str = ".") -> bool:
    """
    Download lottery XLSX file from Caixa API.
    
    Args:
        api_slug: The modalidade parameter for the API (e.g., 'Federal')
        lottery: The filename prefix for the output file (e.g., 'federal')
        output_dir: Directory to save the file (default: current directory)
    
    Returns:
        bool: True if download successful, False otherwise
    """
    
    # Construct the URL
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade={api_slug}"
    
    output_path = os.path.join(output_dir, filename)

    print(f"Downloading from: {url}")
    print(f"Saving to: {output_path}")
    
    try:
        # Make the request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/xlsx,*/*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Referer': 'https://loterias.caixa.gov.br/'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Check if the response is actually an XLSX file
        content_type = response.headers.get('content-type', '').lower()
        if 'application/xlsx' not in content_type:
            print(f"Warning: Content-Type is '{content_type}', expected XLSX format")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Download and save the file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(output_path)
        print(f"Download completed successfully!")
        print(f"File size: {file_size:,} bytes")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False
    except IOError as e:
        print(f"Error saving file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Main function to handle command line arguments."""
    
    if len(sys.argv) < 2:
        print("Usage: python lottery_downloader.py <lottery> [output_dir]")
        print("\nExamples:")
        print("  python lottery_downloader.py federal")
        print("  python lottery_downloader.py megasena ./downloads")
        print("  python lottery_downloader.py lotofacil")
        print("\nParameters:")
        print("  lottery:     The filename prefix for the output file (e.g., 'federal')")
        print("  output_dir:  Directory to save the file (optional, default: current directory)")
        sys.exit(1)
    
    lottery = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    print(f"Lottery: {lottery}")
    print(f"Output Directory: {output_dir}")
    print("-" * 50)

    api_slug = API_SLUG_MAP.get(lottery.lower())
    success = download_lottery_xlsx(api_slug, f"{lottery}.xlsx", output_dir)

    if success:
        print(f"\n✅ Successfully downloaded {lottery}.xlsx")
        xlsx_filepath = os.path.join(output_dir, f"{lottery}.xlsx")
        csv_filepath = xlsx_filepath.replace('.xlsx', '.csv')
        print(f"Converting {xlsx_filepath} to {csv_filepath}...")
        xlsx_to_csv(xlsx_filepath, csv_filepath)
        print(f"CSV file '{csv_filepath}' generated successfully.")
    else:
        print(f"\n❌ Failed to download {lottery}.xlsx")
        sys.exit(1)

if __name__ == "__main__":
    main()
