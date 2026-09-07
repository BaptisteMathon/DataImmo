import pandas as pd

class DataExporter:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def vers_parquet(self, chemin: str):
        """
            Export en format parquet
        """

        self.df.to_parquet(chemin, index=False)
        print(f"Fichier sauvegardé en format parquet avec succés")