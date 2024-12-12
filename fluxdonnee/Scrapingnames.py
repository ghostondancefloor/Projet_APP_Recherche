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
# The names are within <a> tags under a specific section
researcher_section = soup.find("div", class_="entry-content")
researcher_names = [a.text.strip() for a in researcher_section.find_all("a")]

# Save the names to a file
with open("researchers.txt", "w", encoding="utf-8") as file:
    for name in researcher_names:
        file.write(name + "\n")

print(f"Scraped and saved {len(researcher_names)} researcher names.")
