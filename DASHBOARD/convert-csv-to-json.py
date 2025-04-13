import csv
import json

# Open your CSV file
csv_file = r"C:\Users\danli\OneDrive\Documentos\USMB\S8\PROJ831 - Projet APP\Projet_APP_Recherche\DASHBOARD\data.csv"  # Replace with your actual CSV file path
json_file = "data.json"  # Replace with your desired output JSON file path


def try_parse_float(value):
    try:
        return float(value)
    except ValueError:
        return None


with open(csv_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    data = []
    for row in reader:
        # Tenta converter os campos numéricos
        row["value of cited by"] = try_parse_float(
            row.get("value of cited by", "").strip()
        )
        row["year"] = try_parse_float(row.get("year", "").strip())
        data.append(row)

with open(json_file, mode="w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Arquivo convertido com sucesso: {json_file}")
