import json
import re
import time
import random
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from Levenshtein import distance as levenshtein_distance

def normalize_text(input_text):
    """Normaliser le texte en ASCII et en minuscules."""
    text = unicodedata.normalize('NFKD', input_text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'\s*-\s*', '-', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def random_sleep(min_time=1, max_time=3):
    """Fonction pour dormir un temps aléatoire entre min_time et max_time secondes."""
    time.sleep(random.randint(min_time, max_time))

def scrape_HAL():
    """Fonction pour le scraping du site HAL."""
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    with open("ListeEnseignant.txt", "r", encoding='utf-8') as f:
        for line in f:
            # Séparer le nom de l'enseignant et le titre
            parts = line.strip().split(', ')
            if len(parts) != 2:
                print(f"Ignorer la ligne mal formatée : {line.strip()}")
                continue
            name, title = parts

            # Préparer le nom de l'enseignant pour la recherche sur HAL
            search_name = '+'.join(name.split())

            # Ouvrir un fichier JSON pour enregistrer les résultats pour chaque enseignant
            with open(f"{name}_HAL.json", "w", encoding='utf-8') as json_file:
                results = []

                # Recherche sur HAL pour chaque page de résultats
                for i in range(1, 6):
                    # Construire l'URL avec le nom de l'enseignant en cours
                    url = f"https://hal.science/search/index/?q={search_name}&rows=30&page={i}"

                    driver.get(url)
                    time.sleep(random.uniform(5, 10))
                    soup = BeautifulSoup(driver.page_source, 'html.parser')

                    error_content = soup.find('div', class_='error-content')
                    if error_content and "Pas de résultat" in error_content.text:
                        break

                    items = soup.select('.pl-4.pl-sm-0')

                    for item in items:
                        result = {}
                        result['titre'] = item.select_one('.title-results').text.strip().lower()
                        result['auteur'] = name
                        authors = [author.text.strip() for author in item.select('.authors-results a')]
                        result['contributeurs'] = [author for author in authors if author != name]
                        result['lieu de publication'] = item.select_one('.citation-results').text.strip().lower()
                        results.append(result)

                if not results:
                    no_result = {"auteur": name, "message": "Pas de résultat pour cet enseignant"}
                    json.dump(no_result, json_file, ensure_ascii=False, indent=4)
                else:
                    json.dump(results, json_file, ensure_ascii=False, indent=4)

    driver.quit()

def scrape_Google_Scholar(urls_file='links.txt'):
    """Fonction pour le scraping du site Google Scholar."""
    def read_urls_from_file(file_path):
        """Lire les URLs stockées dans un fichier texte."""
        with open(file_path, 'r') as file:
            urls = file.read().splitlines()
        return urls

    def get_article_links(urls):
        """Extraire les liens des articles à partir d'une liste d'URLs de pages de profil Google Scholar."""
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)
        all_articles_links = []

        for url in urls:
            driver.get(url)
            random_sleep()
            while True:
                try:
                    more_button = driver.find_element(By.ID, "gsc_bpf_more")
                    if not more_button.is_enabled():
                        break
                    more_button.click()
                    random_sleep()
                except Exception as e:
                    print("Erreur lors du clic sur Plus : ", e)
                    break
                
            articles = driver.find_elements(By.XPATH, '//*[@id="gsc_a_b"]/tr/td[1]/a')
            for article in articles:
                all_articles_links.append(article.get_attribute('href'))
            random_sleep()

        driver.quit()
        return all_articles_links

    def scrap_articles(articles_links):
        """Scrapper les détails des articles en utilisant les liens récupérés."""
        driver = webdriver.Chrome()
        articles_data = []
        
        for article_url in articles_links:
            driver.get(article_url)
            random_sleep()
            article_data = {
                'titre article': find_text(driver, '//*[@id="gsc_oci_title"]/a'),
                'Contributeurs': find_text(driver, '//*[@id="gsc_oci_table"]/div[1]/div[2]'),
                'Date de publication': find_text(driver, '//*[@id="gsc_oci_table"]/div[2]/div[2]'),
                'Type de publication': find_text(driver, '//*[@id="gsc_oci_table"]/div[3]/div[1]'),
                'Lieu': find_text(driver, '//*[@id="gsc_oci_table"]/div[3]/div[2]'),
                'Description': find_text(driver, '//*[@id="gsc_oci_descr"]/div')
            }
            articles_data.append(article_data)
        
        driver.quit()
        return articles_data

    def find_text(driver, xpath):
        """Tenter de trouver et retourner le texte à partir d'un élément spécifié par XPath."""
        try:
            return driver.find_element(By.XPATH, xpath).text.strip().lower()
        except:
            return ""

    def save_to_json(articles_data, filename='articles.json'):
        """Sauvegarder les données des articles dans un fichier JSON."""
        with open(filename, 'w', encoding='UTF-8') as json_file:
            json.dump(articles_data, json_file, ensure_ascii=False, indent=4)

    urls = read_urls_from_file(urls_file)
    articles_links = get_article_links(urls)
    articles_data = scrap_articles(articles_links)
    save_to_json(articles_data)

def compare_titles_with_tolerance(titles1, titles2, tolerance=3):
    """Comparer les titres avec une tolérance donnée."""
    matched_titles = set()
    for title1 in titles1:
        for title2 in titles2:
            if levenshtein_distance(title1, title2) <= tolerance:
                matched_titles.add((title1, title2))
    return matched_titles

def compare_json_titles(file1, file2):
    """Comparer les titres de deux fichiers JSON."""
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    titles1 = {normalize_text(article['titre']) for article in data1}
    titles2 = {normalize_text(article['titre article']) for article in data2}

    # Find matching titles considering the tolerance
    matched_titles = compare_titles_with_tolerance(titles1, titles2)

    # Finding unmatched titles
    unmatched_titles1 = titles1 - {title1 for title1, title2 in matched_titles}
    unmatched_titles2 = titles2 - {title2 for title1, title2 in matched_titles}

    results = {
        'matched_titles': list(matched_titles),
        'missing_in_file1': list(unmatched_titles1),
        'missing_in_file2': list(unmatched_titles2)
    }

    with open('comparison_results.json', 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, ensure_ascii=False, indent=4)

    return results

def main():
    """Fonction principale pour appeler les fonctions de scraping et de comparaison."""
    scrape_HAL()
    scrape_Google_Scholar()
    compare_json_titles("Flavien VERNIER_HAL.json", "articles.json")

# Appel de la fonction principale
if __name__ == "__main__":
    main()
