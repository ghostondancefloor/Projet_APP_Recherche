import requests
import urllib.parse
import json

def parse_and_encode_name(line):
    """
    Parses a line in the format 'First Name: Ilham , Last Name: A L L O U I'
    and encodes the full name for a URL query.
    """
    # Split the line into parts
    parts = line.split(",")
    
    # Extract and clean the first name
    first_name = parts[0].replace("First Name:", "").strip()
    
    # Extract and clean the last name
    last_name = parts[1].replace("Last Name:", "").strip()
    
    # Combine and encode the full name
    full_name = f"{first_name} {last_name}"
    encoded_name = urllib.parse.quote(full_name)
    return full_name, encoded_name

# Path to the text file containing researcher names
file_path = "labeled_researchers.txt"  # Replace with your text file name

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
        url = f"https://api.archives-ouvertes.fr/search/?q=authFullName_s:%22{encoded_name}%22%20AND%20instStructName_s:%22Universit%C3%A9%20Savoie%20Mont%20Blanc%22&fl=instStructName_s,title_s,authFullName_s,publicationDate_s"

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
output_file_path = "hal_results.json"
with open(output_file_path, "w", encoding="utf-8") as json_file:
    json.dump(all_results, json_file, ensure_ascii=False, indent=4)

print(f"Results saved to {output_file_path}")
