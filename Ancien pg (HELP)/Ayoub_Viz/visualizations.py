import requests
import urllib.parse
import json
import csv
from datetime import datetime, timedelta

def format_name(name):
    """
    Capitalizes the first letter of the name and makes the rest lowercase.
    """
    return name.capitalize()

def parse_and_encode_name(line):
    """
    Parses a line in the format 'First Name: <first name>, Last Name: <last name>'
    and formats the full name with proper capitalization, then encodes it for a URL query.
    """
    # Split the line into parts by comma
    parts = line.split(",")
    
    # Extract and clean the first name and last name
    first_name = parts[0].replace("First Name:", "").strip()
    last_name = parts[1].replace("Last Name:", "").strip()
    
    # Format the first and last names
    formatted_first_name = format_name(first_name)
    formatted_last_name = format_name(last_name)
    
    # Combine the names with a space in between and encode for URL
    full_name = f"{formatted_first_name} {formatted_last_name}"
    encoded_name = urllib.parse.quote(full_name)  # Encode the name for URL
    return full_name, encoded_name

# Path to the text file containing researcher names
file_path = "formatted_researchers.txt"  # Replace with your text file name

# List to store all results
all_results = []

# Read names from the text file
with open(file_path, "r", encoding="utf-8") as file:
    lines = [line.strip() for line in file if line.strip()]  # Ensure empty lines are ignored

# Query the HAL API for each parsed and encoded name
for line in lines:
    try:
        # Parse and encode the name
        full_name, encoded_name = parse_and_encode_name(line)
        print(f"Querying HAL API for: {full_name}")
        
        # Construct the full query URL
        url = f"https://api.archives-ouvertes.fr/search/?q=authFullName_s:%22{encoded_name}%22&fl=title_s,docType_s,primaryDomain_s,openAccess_bool,authFullName_s,instStructName_s,structCountry_s,publicationDate_s,submittedDate_s&wt=json&rows=100"

        # Send the request
        response = requests.get(url)

        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            all_results.append({"name": full_name, "results": data.get("response", {}).get("docs", [])})
        else:
            print(f"Failed to fetch data for {full_name}. Status code: {response.status_code}")
            all_results.append({"name": full_name, "error": f"Status code: {response.status_code}"})
    except Exception as e:
        print(f"Error processing line: {line}. Error: {e}")
        all_results.append({"name": line, "error": str(e)})

# Save all results to a JSON file
output_file_path_json = "hal_results.json"
with open(output_file_path_json, "w", encoding="utf-8") as json_file:
    json.dump(all_results, json_file, ensure_ascii=False, indent=4)

print(f"Results saved to {output_file_path_json}")

# Save all results to a CSV file
csv_columns = ["customAuthorName", "title_s", "docType_s", "primaryDomain_s", "openAccess_bool", "publicationDate_s", "submittedDate_s", "instStructName_s", "structCountry_s"]

with open("hal_results.csv", "w", newline='', encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writeheader()
    
    # Flatten results and add the custom column
    for result in all_results:
        full_name = result["name"]
        if "results" in result:
            for doc in result["results"]:
                # Flatten the fields for CSV output
                row = {
                    "customAuthorName": full_name,
                    "title_s": doc.get("title_s", "N/A"),  # Title of the publication
                    "docType_s": doc.get("docType_s", "N/A"),  # Document type
                    "primaryDomain_s": doc.get("primaryDomain_s", "N/A"),  # Primary research domain
                    "openAccess_bool": doc.get("openAccess_bool", "N/A"),  # Open access status
                    "publicationDate_s": doc.get("publicationDate_s", ""),  # Publication date
                    "submittedDate_s": doc.get("submittedDate_s", ""),  # Submission date
                    "instStructName_s": doc.get("instStructName_s", "N/A"),  # Institution name
                    "structCountry_s": doc.get("structCountry_s", "N/A")  # Country of institution
                }
                writer.writerow(row)

print("Results saved to 'hal_results.csv'")
