import json
import requests
from bs4 import BeautifulSoup
import os

# 📂 Chemins des fichiers mis à jour
INPUT_FILE = "3_filtrage_congres/liste_congrès_reformat.json"
OUTPUT_FILE = "2_scraping_congres/congres_bruts.json"
LOG_FILE = "2_scraping_congres/scraping_errors.log"

# Vérifier si le fichier d'entrée existe
if not os.path.exists(INPUT_FILE):
    print(f"❌ Erreur : Le fichier {INPUT_FILE} n'existe pas.")
    exit(1)

# Charger la liste de liens depuis le fichier JSON
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    urls = json.load(file)  # Assurez-vous que le fichier contient une liste de liens

if not urls:
    print("❌ Aucune URL trouvée dans le fichier d'entrée.")
    exit(1)

# Sélecteurs CSS pour extraire les données
SELECTORS = {
    "lieu": "div:nth-of-type(2) > p:nth-of-type(1) > a",
    "pays": "div:nth-of-type(2) > p:nth-of-type(2) > a > span",
    "langue": "div:nth-of-type(2) > p:nth-of-type(3) > span",
    "date_debut": "div:nth-of-type(2) > p:nth-of-type(4) > time > a",
    "date_fin": "div:nth-of-type(2) > p:nth-of-type(5) > time",
    "lien": "div:nth-of-type(2) > p:nth-of-type(6) > a",
    "description": "div:nth-of-type(3)",
    "specialites": "div:nth-of-type(2) > p:nth-of-type(7) > a"
}

# Headers pour éviter d'être bloqué par certains sites
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Fonction pour scraper une page donnée
def scrape_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Vérifier si la requête a réussi
        soup = BeautifulSoup(response.content, "html.parser")

        # Extraire les données avec BeautifulSoup
        data = {}
        for key, selector in SELECTORS.items():
            elements = soup.select(selector)
            if key == "specialites":
                data[key] = [el.get_text(strip=True) for el in elements] or ["Non disponible"]
            elif key == "description":
                data[key] = elements[0].get_text(strip=True) if elements else "Non disponible"
            else:
                data[key] = elements[0].get_text(strip=True) if elements else "Non disponible"

        data["lien_source"] = url  # Ajouter le lien source
        return data

    except requests.RequestException as e:
        # Enregistrer les erreurs dans un fichier
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"⚠️ Erreur lors de l'accès à {url} : {e}\n")
        print(f"⚠️ Erreur lors de l'accès à {url} : {e}")
        return None

# Scraper toutes les pages et stocker les résultats
resultats = []
total_urls = len(urls)

print(f"🔍 Début du scraping de {total_urls} congrès...")

for index, url in enumerate(urls, start=1):
    print(f"➡️ [{index}/{total_urls}] Scraping de {url}...")
    data = scrape_page(url)
    if data:
        resultats.append(data)

# Sauvegarder les résultats dans un fichier JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(resultats, file, indent=4, ensure_ascii=False)

print(f"\n✅ Scraping terminé. Résultats sauvegardés dans '{OUTPUT_FILE}'.")
if os.path.exists(LOG_FILE):
    print(f"⚠️ Des erreurs ont été enregistrées dans '{LOG_FILE}'.")
