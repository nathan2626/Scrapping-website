import os

print("\n🔍 Étape 1 : Scraping des sociétés savantes...")
# os.system("py 1_scraping_societes/scrapping_societes_savantes.py")

print("\n🔍 Étape 2 : Scraping des congrès...")
# os.system("py 2_scraping_congres/scrapping_congre_details.py")

print("\n🔍 Étape 3 : Generer les liens...")
# os.system("py 3_filtrage_congres/generer_liste_liens.py")

print("\n🤖 Étape 4 : Extraction avancée avec GPT...")
os.system("py 4_extraction_gpt/gpt-recovery-data-in-website.py")

print("\n✅ Pipeline terminé ! Les résultats sont dans 4_IA_extraction/results_congrès_données_gpt.json.")
