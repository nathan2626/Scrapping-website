import json
import requests
from bs4 import BeautifulSoup

# URL cible
with open('url.txt', 'r') as file:
    URL = file.read().strip()

# Headers pour éviter d'être bloqué par le site
headers = {'User-Agent': 'Mozilla/5.0'}

# Effectuer la requête HTTP
response = requests.get(URL, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Trouver les blocs contenant les sociétés savantes
    societies = soup.find_all("article", class_="article-list-item")

    data = []
    
    for society in societies:
        details = {}

        # Récupérer les informations demandées
        details["Organisation"] = society.find("h2").text.strip() if society.find("h2") else "N/A"
        details["Abréviation"] = society.find("h3").text.strip() if society.find("h3") else "N/A"
        
        # Récupérer spécialité et type
        spans = society.find_all("span", class_="info-label")
        for span in spans:
            label = span.text.strip().lower()
            value = span.find_next_sibling("span").text.strip() if span.find_next_sibling("span") else "N/A"
            if "spécialité" in label:
                details["Spécialité"] = value
            elif "type" in label:
                details["Type"] = value
        
        # Récupérer les liens utiles
        links = society.find_all("a", href=True)
        for link in links:
            href = link["href"]
            text = link.text.strip().lower()
            if "actualités" in text:
                details["Actualités"] = href
            elif "rss" in text:
                details["RSS"] = href
            elif "publications ouvertes" in text:
                details["Publications ouvertes"] = href
            elif "publications rss" in text:
                details["Publications RSS"] = href
            elif "social" in text:
                details["Social"] = href
        
        # Ajouter un contrôle pour les champs manquants
        details.setdefault("Actualités", "N/A")
        details.setdefault("RSS", "N/A")
        details.setdefault("Publications ouvertes", "N/A")
        details.setdefault("Publications RSS", "N/A")
        details.setdefault("Social", "N/A")

        data.append(details)

    # 📂 Sauvegarde dans un fichier JSON
    output_file = "1_scraping_societes/societes_savantes.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"\n✅ Données enregistrées dans : {output_file}")

else:
    print(f"❌ Échec de récupération de la page, code HTTP: {response.status_code}")
