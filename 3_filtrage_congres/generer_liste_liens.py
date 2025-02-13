import json
import os

# 📂 Chemins des fichiers
INPUT_FILE = "2_scraping_congres/congres_bruts.json"
OUTPUT_FILE = "3_filtrage_congres/liste_congrès_reformat.json"

# Vérifier si le fichier d'entrée existe
if not os.path.exists(INPUT_FILE):
    print(f"❌ Erreur : Le fichier {INPUT_FILE} n'existe pas.")
    exit(1)

# Charger les données des congrès
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    congres_data = json.load(file)

# Extraire uniquement les liens
liens = [congres.get("lien") for congres in congres_data if "lien" in congres]

if not liens:
    print("❌ Aucun lien trouvé dans le fichier des congrès.")
    exit(1)

# Enregistrer le fichier JSON avec la liste des liens
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(liens, file, indent=4, ensure_ascii=False)

print(f"✅ Liste des liens enregistrée dans : {OUTPUT_FILE}")
