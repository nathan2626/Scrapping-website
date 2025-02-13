import json
import requests
import time
import os
from openai import OpenAI
from bs4 import BeautifulSoup

# 📂 Chemins des fichiers mis à jour
INPUT_FILE = "3_filtrage_congres/liste_congrès_reformat.json"
OUTPUT_FILE = "4_extraction_gpt/congres_enrichis.json"
LOG_FILE = "4_extraction_gpt/gpt_extraction_errors.log"

# Activer ou désactiver le mode debug
DEBUG_MODE = True

# Vérifier si le fichier d'entrée existe
if not os.path.exists(INPUT_FILE):
    print(f"❌ Erreur : Le fichier {INPUT_FILE} n'existe pas.")
    exit(1)

# Lecture de la clé API et de l'ID d'organisation
with open('key.txt', 'r') as file:
    secret_key = file.read().strip()

# Initialisation du client OpenAI
client = OpenAI(api_key=secret_key)

# Charger la liste des congrès
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    congres_data = json.load(file)

if not congres_data:
    print("❌ Aucun congrès trouvé dans le fichier d'entrée.")
    exit(1)

# Vérifier si un fichier de sauvegarde existe déjà (pour reprendre en cas d'arrêt)
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        resultats = json.load(file)
    print(f"🔄 Reprise du traitement : {len(resultats)} congrès déjà traités.")
else:
    resultats = []

traites = {item["lien"] for item in resultats}  # Liens déjà traités

# Fonction pour récupérer et nettoyer le contenu d'une page web
def recuperer_contenu(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except requests.RequestException as e:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"❌ Erreur accès {url}: {e}\n")
        print(f"❌ Erreur accès {url}: {e}")
        return None

# Fonction pour découper un texte en blocs de 5000 caractères
def decouper_texte(texte, taille_bloc=5000):
    return [texte[i:i+taille_bloc] for i in range(0, len(texte), taille_bloc)]

# Fonction pour demander à GPT d'extraire les infos sous format JSON
def extraire_informations(text, url):
    blocs = decouper_texte(text)
    extraction_finale = {
        "contacts": [],
        "personnes": [],
        "lieux": [],
        "dates": [],
        "résumé": ""
    }

    for i, bloc in enumerate(blocs):
        print(f"→ Envoi du bloc {i+1}/{len(blocs)} pour {url}...")

        prompt = f"""
        Voici un extrait d'une page web issue de {url}. Analyse-le et retourne **uniquement** un JSON **valide** en **français**, contenant :

        {{
            "contacts": [
                {{"type": "email", "valeur": "email@example.com", "propriétaire": "Dr Jean Dupont"}},
                {{"type": "téléphone", "valeur": "+33 1 23 45 67 89", "propriétaire": "Université de Paris"}}
            ],
            "personnes": [
                {{"nom": "Dr Jean Dupont", "titre": "Professeur en ophtalmologie", "affiliation": "Université de Paris",
                  "contact": "jean.dupont@example.com", "téléphone": "+33 1 23 45 67 89", "publications": ["Titre publication 1", "Titre publication 2"]}}
            ],
            "lieux": ["Paris, Centre des Congrès"],
            "dates": [
                {{"date": "10-12 mars 2025", "événement": "Conférence sur l'imagerie médicale", "personnes_associees": ["Dr Jean Dupont", "Professeur Martin"]}}
            ],
            "résumé": "Conférence internationale sur les dernières avancées en ophtalmologie."
        }}

        Extrait :
        {bloc}
        """

        # Système de gestion du rate limit avec réessai
        attente = 2
        for tentative in range(5):  # Essaye 5 fois max
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                contenu_gpt = response.choices[0].message.content.strip()

                if DEBUG_MODE:
                    print(f"🧐 Réponse brute de GPT (Bloc {i+1}):\n{contenu_gpt}")

                if contenu_gpt.startswith("{") and contenu_gpt.endswith("}"):
                    resultat = json.loads(contenu_gpt)
                else:
                    raise ValueError("La réponse de GPT n'est pas un JSON valide.")

                extraction_finale["contacts"].extend(resultat.get("contacts", []))
                extraction_finale["personnes"].extend(resultat.get("personnes", []))
                extraction_finale["lieux"].extend(resultat.get("lieux", []))
                extraction_finale["dates"].extend(resultat.get("dates", []))
                extraction_finale["résumé"] += " " + resultat.get("résumé", "")

                break  # Sortir de la boucle en cas de succès

            except Exception as e:
                print(f"⚠️ Erreur avec GPT (tentative {tentative+1}/5) : {e}")
                time.sleep(attente)
                attente *= 2  # Double le temps d'attente à chaque échec

    return extraction_finale

# Processus principal
total_congres = len(congres_data)
for index, item in enumerate(congres_data):
    if isinstance(item, str):
        url = item
    elif isinstance(item, dict) and "lien" in item:
        url = item["lien"]
    else:
        print(f"⚠️ Format invalide détecté : {item}")
        continue

    if url in traites:
        print(f"⏩ {url} déjà traité, passage au suivant...")
        continue

    print(f"\n🔍 [{index+1}/{total_congres}] Traitement de {url}...")
    contenu = recuperer_contenu(url)

    if contenu:
        infos = extraire_informations(contenu, url)
        resultats.append({"lien": url, "extraction": infos})
        traites.add(url)

    # Sauvegarde toutes les 5 requêtes
    if len(resultats) % 5 == 0:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
            json.dump(resultats, output_file, indent=4, ensure_ascii=False)
        print("💾 Sauvegarde intermédiaire effectuée.")

# Sauvegarde finale
with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
    json.dump(resultats, output_file, indent=4, ensure_ascii=False)

print(f"\n✅ Extraction terminée. Résultats sauvegardés dans '{OUTPUT_FILE}'.")
