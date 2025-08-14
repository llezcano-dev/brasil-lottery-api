from typing import Dict, Any

def default_mapping(row_num: int, row: dict) -> Dict[str, Any]:
    """
    Default mapping function that converts a CSV row to a JSON object.
    
    Args:
        row_num: Row number in the CSV file
        row: List of values from the CSV row
    
    Returns:
        Dictionary with JSON object including mandatory "_ID" field
    """
    # Create a basic mapping using headers as keys
    json_obj = {
        "_ID": f"row_{row_num}",
    }

    for key in row.keys():
        if key.strip():
            json_obj[key.strip()] = row[key].strip() if row[key] else None

    return json_obj