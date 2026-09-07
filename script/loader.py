import pandas as pd

class DataLoader:

    def __init__(self, chemin: str):
        self.chemin = chemin

    def charger_par_morceaux(self, taille_chunk: int = 1000):
        """
            Lecture du fichier csv par morceaux de 1000 enregistrements
        """

        print(f"Début de la lecture par lots de {taille_chunk} enregistrement à partir du fichier {self.chemin}")

        return pd.read_csv(
            self.chemin,
            chunksize=taille_chunk,
            dtype={"code_postal": str, "code_commune": str, "code_departement": str},
            parse_dates=["date_mutation"]
        )

# if __name__ == "__main__":
#     loader = DataLoader("data/raw/dvf_59_2024.csv.gz")
#     for chunk in loader.charger_par_morceaux():
#         print(chunk.head())
#         break