import pandas as pd

class DataCleaner:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def supprimer_doublons(self):
        """
            Suppression des lignes dupliquées
        """

        self.df = self.df.drop_duplicates(subset=["id_mutation"])
        return self

    def supprimer_incomplets(self):
        """
            Suppression des lignes incomplètes
        """

        self.df = self.df.dropna(subset=["valeur_fonciere", "surface_reelle_bati"])
        return self

    def ajouter_prix_m2(self):
        """
            Ajout d'une colonne prix_m2 (calculé selon la valeur foncière / surface_reelle_bati)
        """

        self.df["prix_m2"] = self.df["valeur_fonciere"] / self.df["surface_reelle_bati"]
        return self


    def filtrer_aberrations(self):
        """
            Suppression des prix au m2 extrêmes
        """

        self.df = self.df[(self.df["prix_m2"] >= 100) & (self.df["prix_m2"] <= 20000)]
        return self

    def optimiser_types(self):
        """
            Optimisation des types de données en catégorie pour alléger la RAM
        """

        self.df["type_local"] = self.df["type_local"].astype("category")
        return self

    def executer_nettoyage(self):
        """
            Exécution des méthodes ci-dessus
        """

        return (self.supprimer_doublons()
                    .supprimer_incomplets()
                    .ajouter_prix_m2()
                    .filtrer_aberrations()
                    .optimiser_types()
                    .df)

        