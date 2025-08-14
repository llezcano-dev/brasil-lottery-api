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
