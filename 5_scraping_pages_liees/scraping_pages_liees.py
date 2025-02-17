import json
import requests
import time
import os
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from selenium import webdriver

# ===========================
# 📂 Chemins et Paramètres
# ===========================
INPUT_FILE = "4_extraction_gpt/congres_enrichis.json"
OUTPUT_DIR = "5_scraping_pages_liees"
LOG_FILE = os.path.join(OUTPUT_DIR, "pages_liees_errors.log")

TIMEOUT = 15
SLEEP_TIME = 2
MAX_PAGES = 300
MAX_CONTENT = 10000

# 🗂️ Mots-clés pour filtrer les pages pertinentes
MOTS_CLES = [
    "congre", "congres", "congress", "congresse", "congresses",
    "2025", "2026", "2027", "event", "events", "planning"
]

# ===========================
# 🖥️ Initialisation Selenium
# ===========================
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

# ===========================
# 📂 Gestion des dossiers
# ===========================
def creer_dossier_domaine(domaine):
    base_path = os.path.join(OUTPUT_DIR, domaine)
    os.makedirs(os.path.join(base_path, "pages_html"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "fichiers"), exist_ok=True)
    return base_path

# ===========================
# 📝 Gestion des logs
# ===========================
def log_erreur(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")
    print(f"❌ {message}")

# ===========================
# 📂 Gestion des pages visitées
# ===========================
def charger_pages_visitees(domaine):
    path = os.path.join(OUTPUT_DIR, domaine, "pages_visitées.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def sauvegarder_pages_visitees(domaine, pages):
    path = os.path.join(OUTPUT_DIR, domaine, "pages_visitées.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(pages), f, indent=4, ensure_ascii=False)

# ===========================
# 📍 Filtre URL et titres avec mots-clés
# ===========================
def contient_mot_cle(texte):
    if not texte:
        return False
    texte = texte.lower()
    return any(mot in texte for mot in MOTS_CLES)

# ===========================
# 📥 Téléchargement de fichiers (Sans Images)
# ===========================
def telecharger_fichier(url, dossier):
    if re.search(r"\.(jpg|jpeg|png|gif|svg|webp)$", url, re.IGNORECASE):
        print(f"🚫 Ignoré (image) : {url}")
        return

    # Filtrer uniquement les fichiers avec mots-clés dans l’URL
    if not contient_mot_cle(url):
        print(f"🚫 Ignoré (pas pertinent) : {url}")
        return

    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        filename = os.path.basename(url)
        filepath = os.path.join(dossier, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"✅ Fichier téléchargé : {filename}")
    except Exception as e:
        log_erreur(f"Erreur téléchargement {url}: {e}")

# ===========================
# 🌐 Scraping complet d'un domaine
# ===========================
def collecter_pages(url):
    domaine = urlparse(url).netloc
    base_path = creer_dossier_domaine(domaine)

    pages_visitees = charger_pages_visitees(domaine)
    pages_a_visiter = {url}
    pages_scrapées = []

    while pages_a_visiter and len(pages_scrapées) < MAX_PAGES:
        page_url = pages_a_visiter.pop()
        if page_url in pages_visitees:
            continue

        try:
            print(f"🌐 Scraping : {page_url}")
            driver.get(page_url)
            time.sleep(3)
            contenu = driver.page_source
            soup = BeautifulSoup(contenu, "html.parser")

            # 🚫 Supprimer les balises <img>
            for img_tag in soup.find_all("img"):
                img_tag.decompose()

            # 📍 Filtrer pages avec mots-clés
            title = soup.title.string if soup.title else ""
            if not contient_mot_cle(page_url) and not contient_mot_cle(title):
                print(f"🚫 Ignoré (titre/URL non pertinent) : {page_url}")
                continue

            # 💾 Enregistrer HTML pertinent
            html_filename = re.sub(r'\W+', '_', urlparse(page_url).path) or "index"
            html_filepath = os.path.join(base_path, "pages_html", f"{html_filename}.html")
            with open(html_filepath, "w", encoding="utf-8") as f:
                f.write(soup.prettify())

            # 📜 Extraire le texte
            texte = soup.get_text(separator="\n", strip=True)

            # 📥 Collecter fichiers téléchargeables (hors images)
            for lien in soup.find_all("a", href=True):
                href = urljoin(page_url, lien["href"])
                if href not in pages_visitees and domaine in urlparse(href).netloc:
                    pages_a_visiter.add(href)

                # Téléchargement sauf images, avec filtre mots-clés
                if re.search(r"\.(pdf|docx|pptx|txt)$", href, re.IGNORECASE):
                    telecharger_fichier(href, os.path.join(base_path, "fichiers"))

            pages_scrapées.append({
                "url": page_url,
                "titre": title,
                "contenu": texte[:MAX_CONTENT]
            })

        except Exception as e:
            log_erreur(f"Erreur scraping {page_url}: {e}")

        pages_visitees.add(page_url)
        sauvegarder_pages_visitees(domaine, pages_visitees)
        time.sleep(SLEEP_TIME)

    return pages_scrapées

# ===========================
# 💾 Fonction principale
# ===========================
def enrichir_congres_avec_pages():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        congres_data = json.load(file)

    for congres in congres_data:
        url_principale = congres.get("lien")
        print(f"\n🚀 Scraping des pages pour : {url_principale}")
        pages = collecter_pages(url_principale)
        congres["pages_liées"] = pages

    # 💾 Sauvegarde finale
    output_file = os.path.join(OUTPUT_DIR, "congres_enrichis_avec_pages.json")
    with open(output_file, "w", encoding="utf-8") as output_file:
        json.dump(congres_data, output_file, indent=4, ensure_ascii=False)

    print(f"\n✅ Scraping terminé ! Résultats dans '{output_file}'.")

# ===========================
# ▶️ Exécution
# ===========================
if __name__ == "__main__":
    enrichir_congres_avec_pages()
    driver.quit()
