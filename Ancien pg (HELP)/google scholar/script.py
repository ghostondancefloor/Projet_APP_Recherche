import json
import csv

# Load the JSON data from a file
json_file_path = 'google scholar/et.json'  # Path to your JSON file
with open(json_file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Define the output CSV file
csv_file = 'google scholar/data/output16.csv'

# Open the CSV file and write the data
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(["researcher", "title", "authors", "value of cited by", "year"])

    # Write the data rows
    for item in json_data:
        writer.writerow([
            "Emmanuel Trouvé",
            item.get("title", ""),
            item.get("authors", ""),
            item.get("cited_by", {}).get("value", ""),
            item.get("year", "")
        ])

print(f"Data has been successfully written to {csv_file}.")