import requests
import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

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

def fetch_latest_federal_result() -> Optional[Dict]:
    """Fetch the latest federal lottery result from Caixa API."""
    
    url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/federal/"
    
    print(f"Fetching latest federal result from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json,*/*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Referer': 'https://loterias.caixa.gov.br/'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Successfully fetched latest federal result")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching latest result: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        return None

def convert_caixa_to_api_format(caixa_data: Dict) -> Dict:
    """Convert Caixa API format to our API format."""
    
    # Extract draw number (assuming it's in the data, or we'll need to get it from somewhere)
    draw_number = caixa_data.get("numero", "")
  
    # Extract and convert date
    data_apuracao = caixa_data.get("dataApuracao", "")
    iso_date = parse_date_to_iso(data_apuracao)
    
    # Extract draw numbers
    dezenas = caixa_data.get("dezenasSorteadasOrdemSorteio", [])
    
    # Extract prizes from listaRateioPremio
    lista_rateio = caixa_data.get("listaRateioPremio", [])
    
    # Convert to our API format
    api_response = {
        "drawNumber": str(draw_number),
        "date": iso_date,
        "results": []
    }
    
    # Map the prizes to our format
    for i, prize_info in enumerate(lista_rateio, 1):
        if i <= len(dezenas):  # Ensure we have a corresponding drawumber
            draw_number = dezenas[i-1] if i-1 < len(dezenas) else ""
            prize_amount = prize_info.get("valorPremio", 0.0)
            
            api_response["results"].append({
                "position": i,
                "winningNumber": draw_number,
                "prizeAmount": float(prize_amount)
            })
    
    return api_response

def save_draw_result(api_data: Dict, draw_number: str, base_dir: str = "v1") -> bool:
    """Save the draw result to the draws folder and update latest."""
    
    try:
        # Create directory structure: v1/lotteries/federal/draws/
        lotteries_dir = os.path.join(base_dir, "lotteries")
        federal_dir = os.path.join(lotteries_dir, "federal")
        draws_dir = os.path.join(federal_dir, "draws")
        
        os.makedirs(draws_dir, exist_ok=True)
        
        # Save individual draw file
        draw_file = os.path.join(draws_dir, f"{draw_number}.json")
        with open(draw_file, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved draw result: {draw_file}")
        
        # Copy to latest.json
        latest_file = os.path.join(draws_dir, "latest.json")
        shutil.copy2(draw_file, latest_file)
        
        print(f"✅ Updated latest draw: {latest_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving draw result: {e}")
        return False

def check_if_result_exists(draw_number: str, base_dir: str = "v1") -> bool:
    """Check if we already have this draw result."""
    
    draw_file = os.path.join(base_dir, "lotteries", "federal", "draws", f"{draw_number}.json")
    return os.path.exists(draw_file)

def update_latest_federal_result(base_dir: str = "v1") -> bool:
    """Main function to update the latest federal lottery result."""
    
    print("🎲 Updating latest federal lottery result...")
    print("=" * 50)
    
    # Fetch latest result from Caixa API
    caixa_data = fetch_latest_federal_result()
    if not caixa_data:
        return False
    
    # Convert to our API format
    api_data = convert_caixa_to_api_format(caixa_data)
    
    draw_number = api_data.get("drawNumber", "")
    if not draw_number:
        print("❌ Could not extract draw number from API response")
        return False
    
    print(f"📊 Latest draw: #{draw_number} from {api_data.get('date', 'unknown date')}")
    
    # Check if we already have this result
    if check_if_result_exists(draw_number, base_dir):
        print(f"ℹ️  Contest #{draw_number} already exists, updating anyway...")
    
    # Save the draw result
    if not save_draw_result(api_data, draw_number, base_dir):
        return False
    
    print(f"\n🎉 Successfully updated federal lottery API!")
    print(f"📁 Files updated in: {base_dir}/lotteries/federal/draws/")
    print(f"🔗 Access latest: /v1/lotteries/federal/draws/latest.json")
    print(f"🔗 Access specific: /v1/lotteries/federal/draws/{draw_number}.json")
    
    return True

def main():
    """Main function to handle command line usage."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python federal_update_latest.py [api_base_dir]")
        print("\nThis script:")
        print("1. Fetches the latest federal lottery result from Caixa API")
        print("2. Converts it to our API format")
        print("3. Saves it as both a specific draw file and latest.json")
        print("\nParameters:")
        print("  api_base_dir: Base directory for API files (default: 'v1')")
        print("\nExample:")
        print("  python federal_update_latest.py")
        print("  python federal_update_latest.py ./my_v1_api")
        sys.exit(0)
    
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "v1"
    
    success = update_latest_federal_result(base_dir)
    
    if success:
        print("\n✅ Update completed successfully!")
    else:
        print("\n❌ Update failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()