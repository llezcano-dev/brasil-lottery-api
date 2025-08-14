from typing import Dict, Any
from mappers.utils import parse_monetary_value, parse_str_to_int, parse_date_to_iso, parse_prize_number, clean_value

def federal_mapping(row_num: int, row: dict) -> Dict[str, Any]:
    """Process single CSV row and save JSON file."""
    try:
        extracao_num, data_sorteio = extract_basic_info(row)
        if not extracao_num or not data_sorteio:
            print(f"Warning: Missing basic data in row {row_num}, skipping...")
            return

        return {
            "_ID": extracao_num,
            "drawNumber": parse_str_to_int(extracao_num),
            "date": parse_date_to_iso(data_sorteio),
            "results": extract_prizes(row)
        }

    except Exception as e:
        print(f"Error processing row {row_num}: {e}")

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

def extract_basic_info(row: dict):
    """Extract essential draw information from a CSV row."""
    extracao_num = clean_value(row.get('Extração', '')) or clean_value(row.get('**Extração**', ''))
    data_sorteio = clean_value(row.get('Data Sorteio', '')) or clean_value(row.get('**Data Sorteio**', ''))
    return extracao_num, data_sorteio
