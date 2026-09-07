# DataImmo

## Livrable 1 - Ingestion & nettoyage (Python POO + Pandas)

Ce livrable permet de lire un fichier csv et csv compréssé, de nettoyer les enregistrements ainsi que les données mal renseignées. Pour ensuite l'exporter en un fichier .parquet

### Architecture du projet:

- **'script/loader.py'** : Classe qui gère la lecture des fichier CSV et CSV compréssé.
- **'script/cleaner.py'** : Classe permettant de nettoyer les données du fichier csv.
- **'script/exporter.py'** : Classe permettant d'exporter les données du fichier csv en un fichier parquet.
- **'script/main.py'** : Script principal permettant d'exécuter les script précédents.

### Prérequis et installation :

1. Activer votre environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Installer les bibliothèques suivantes :
   '''bash
   pip install pandas
   '''

### Utilisation :

1. Assurez-vous d'avoir l'arboresence requise :

```bash
.
├── data
│   ├── raw
│   └── clean
```

Ainsi qu'un fichier DVF brut dans le dossier 'data/raw'.
Commande pour télécharger les données du département du Nord (59) :

```bash
curl -L -o data/raw/dvf_59_2024.csv.gz "https://files.data.gouv.fr/geo-dvf/latest/csv/2024/departements/59.csv.gz"
```

2. Exécuter le script :

```bash
python3 script/main.py
```

3. Il ne reste plus qu'à consulter le rapport généré dans la console de votre terminal, ainsi que le fichier parquet dans le dossier 'data/clean'.
