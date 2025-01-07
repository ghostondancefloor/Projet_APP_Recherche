import requests
from bs4 import BeautifulSoup

# URL of the webpage to scrape
url = "https://www.univ-smb.fr/listic/presentation/membres/enseignants-chercheurs/"

# Send a GET request to the webpage
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the webpage content
soup = BeautifulSoup(response.content, "html.parser")

# Find the section containing the researcher names
researcher_section = soup.find("div", class_="entry-content")
researcher_names = [a.text.strip() for a in researcher_section.find_all("a")]

# Define a dictionary for name replacements
name_replacements = {
    "Khadija ARFAOUI": "Khadija BOUSSELMI"
}

# Apply the name replacements
updated_names = [
    name_replacements.get(name, name)  # Replace if the name is in the dictionary
    for name in researcher_names
]

# Function to format names as 'First Name: [First Name], Last Name: [Last Name]'
def format_name(name):
    # Split the name into first and last name
    name_parts = name.split()
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:])  # Join the rest as last name (in case of middle names)
    return f"First Name: {first_name}, Last Name: {last_name}"

# Format the names
formatted_names = [format_name(name) for name in updated_names]

# Save the formatted names to a file
with open("formatted_researchers.txt", "w", encoding="utf-8") as file:
    for name in formatted_names:
        file.write(name + "\n")

print(f"Scraped, formatted, and saved {len(formatted_names)} researcher names.")
