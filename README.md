# 🔁 Ordre d’exécution et rôle des fichiers  

💡 Voici comment tu dois exécuter les fichiers dans le bon ordre :  

---

## **1️⃣ Scraping des sociétés savantes**  
📂 **Dossier :** `1_scraping_societes/`  
📌 **Fichier à exécuter en premier :**  

```bash
python 1_scraping_societes/scraping_societes.py
```

📤 **Sortie :** `1_scraping_societes/societes_savantes.json`  
➡ **Récupère les sociétés savantes et leurs informations principales.**  

---

## **2️⃣ Scraping des congrès associés**  
📂 **Dossier :** `2_scraping_congres/`  
📌 **Fichier à exécuter en deuxième :**  

```bash
python 2_scraping_congres/scraping_congres.py
```

📥 **Entrée :** `1_scraping_societes/societes_savantes.json`  
📤 **Sortie :** `2_scraping_congres/congres_bruts.json`  
➡ **Récupère les congrès liés aux sociétés savantes.**  

---

## **3️⃣ Filtrage des congrès pertinents**  
📂 **Dossier :** `3_filtrage_congres/`  
📌 **Fichier manuel :**  

➡ **Tu dois sélectionner les congrès importants et les stocker dans `3_filtrage_congres/filtrage_congres.json`.**  
➡ **Ce fichier est utilisé pour limiter le nombre de congrès traités dans l'étape suivante.**  

📥 **Entrée :** `2_scraping_congres/congres_bruts.json`  
📤 **Sortie :** `3_filtrage_congres/congres_filtres.json`  

---

## **4️⃣ Extraction avancée avec GPT**  
📂 **Dossier :** `4_extraction_gpt/`  
📌 **Fichier à exécuter :**  

```bash
python 4_extraction_gpt/extraction_gpt.py
```

📥 **Entrée :** `3_filtrage_congres/congres_filtres.json`  
📤 **Sortie :** `4_extraction_gpt/congres_enrichis.json`  

➡ **GPT analyse chaque congrès et récupère :**  
✔ **Contacts (avec propriétaires)**  
✔ **Personnes clés (nom, affiliation, email, téléphone)**  
✔ **Dates détaillées (événements et personnes concernées)**  
✔ **Résumé complet en français**  

---

## **🛠️ Exécution automatique du pipeline**  
📂 **Dans la racine du projet :**  

```bash
python run_pipeline.py
```

💡 **Ce fichier exécute toutes les étapes automatiquement dans le bon ordre.**  

