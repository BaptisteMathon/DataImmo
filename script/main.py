import os
import pandas as pd
from loader import DataLoader
from cleaner import DataCleaner
from exporter import DataExporter

def executer_pipeline():
    entree = "data/raw/dvf_59_2024.csv.gz"
    sortie = "data/clean/dvf_59_2024.parquet"

    # Chargement des données
    loader = DataLoader(entree)
    chunks = loader.charger_par_morceaux()

    chunks_propre = []
    total_lignes_brutes = 0
    total_memoire_brute = 0

    print(f"Démarrage du pipeline de traitement")

    # Nettoyage du fichier d'entrée par chunks de 1000 enregistrements
    for chunk in chunks:
        total_lignes_brutes += len(chunk)
        total_memoire_brute += chunk.memory_usage(deep=True).sum()

        cleaner = DataCleaner(chunk)
        chunk_propre = cleaner.executer_nettoyage()
        chunks_propre.append(chunk_propre)

    print(f"Assemblage des chunks nettoyés...")

    # Assemblage des chunks nettoyés
    df_final = pd.concat(chunks_propre, ignore_index=True)

    total_lignes_propres = len(df_final)
    total_memoire_propre = df_final.memory_usage(deep=True).sum()

    # Exportation du DataFrame en parquet
    exporter = DataExporter(df_final)
    exporter.vers_parquet(sortie)

    # Rapport final
    taille_parquet = os.path.getsize(sortie) / (1024*1024)
    pourcentage_conservation = (total_lignes_propres / total_lignes_brutes) * 100

    print(f"*** RAPPORT APRES EXECUTION ***")
    print(f"Lignes traitées  : {total_lignes_brutes} -> {total_lignes_propres} ({pourcentage_conservation:.2f}% conservées)")
    print(f"RAM              : {total_memoire_brute / (1024*1024):.1f} Mo -> {total_memoire_propre / (1024*1024):.1f} Mo")
    print(f"Poids du parquet : {taille_parquet:.1f} Mo")


if __name__ == "__main__":
    executer_pipeline()
    

    