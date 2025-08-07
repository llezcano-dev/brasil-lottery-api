import requests
import sys
import os
from typing import Optional

def download_lottery_excel(api_slug: str, lottery: str, output_dir: str = ".") -> bool:
    """
    Download lottery Excel file from Caixa API.
    
    Args:
        api_slug: The modalidade parameter for the API (e.g., 'Federal')
        lottery: The filename prefix for the output file (e.g., 'federal')
        output_dir: Directory to save the file (default: current directory)
    
    Returns:
        bool: True if download successful, False otherwise
    """
    
    # Construct the URL
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade={api_slug}"
    
    # Construct output filename
    output_filename = f"{lottery}.xlsx"
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"Downloading from: {url}")
    print(f"Saving to: {output_path}")
    
    try:
        # Make the request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Referer': 'https://loterias.caixa.gov.br/'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Check if the response is actually an Excel file
        content_type = response.headers.get('content-type', '').lower()
        if 'excel' not in content_type and 'spreadsheet' not in content_type:
            print(f"Warning: Content-Type is '{content_type}', expected Excel format")
        
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
    
    if len(sys.argv) < 3:
        print("Usage: python lottery_downloader.py <api_slug> <lottery> [output_dir]")
        print("\nExamples:")
        print("  python lottery_downloader.py Federal federal")
        print("  python lottery_downloader.py Megasena megasena ./downloads")
        print("  python lottery_downloader.py Lotofacil lotofacil")
        print("\nParameters:")
        print("  api_slug:    The modalidade parameter for the API (e.g., 'Federal')")
        print("  lottery:     The filename prefix for the output file (e.g., 'federal')")
        print("  output_dir:  Directory to save the file (optional, default: current directory)")
        sys.exit(1)
    
    api_slug = sys.argv[1]
    lottery = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    
    print(f"API Slug: {api_slug}")
    print(f"Lottery: {lottery}")
    print(f"Output Directory: {output_dir}")
    print("-" * 50)
    
    success = download_lottery_excel(api_slug, lottery, output_dir)
    
    if success:
        print(f"\n✅ Successfully downloaded {lottery}.xlsx")
        print(f"Next steps:")
        print(f"1. Convert to CSV: python xlsx_to_csv.py {lottery}.xlsx {lottery}.csv")
        print(f"2. Generate API: python csv_to_api.py {lottery}.csv")
    else:
        print(f"\n❌ Failed to download {lottery}.xlsx")
        sys.exit(1)

if __name__ == "__main__":
    main()
