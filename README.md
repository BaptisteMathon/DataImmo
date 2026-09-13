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

2. Installation de toutes les bibliothèques du projet:

```bash
pip install -r requirements.txt
```

3. Bibliothèques utiliser pour ce livrable : **Pandas**

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

## Livrable 2 - Passage à Spark

Lors de ce livrable les bibliothèques suivantes seront utilisées : **pyspark** **jupyter** **ipykernel**

Capture d'écran du résultat de l'agrégation et du plan d'éxecution :

![alt text](<Img/Capture d’écran 2026-09-08 à 20.18.18.png>)

- Le tableau affiche le prix moyen au m2 agrégé par commune et par type de bien
- Le "== Physical Plan ==" est déclenché par l'instruction .explain(). Il permet de visualiser comment Spark exécute le code. On y retrouve :
  - La lecture du fichier (FileScan csv)
  - L'application des filtres pour écarter les données non pertinentes (Filter)
  - La préparation des colonnes (Project)
  - Les opérations d'agrégation et de jointure (HashAggregate)

Capture d'écran de l'interface web Spark :

![alt text](Img/spark.png)

Cette interface de Spark nous permet de visualiser comment Spark exécute le code. Ce sont comme des logs, de chaque exécution / utilisation de Spark.

## Livrable 3 - Analyse massive & performance

Voir le README suivant : [text](benchmark.md)

Voici la commande a effectuer afin de récupérer les fichier dvf de 2021 à 2024 :

```bash
for annee in 2020 2021 2022 2023 2024; do
   curl -L -o "data/raw/dvf_full_${annee}.csv.gz" "https://files.data.gouv.fr/geo-dvf/latest/csv/${annee}/full.csv.gz"
done
```

Et la commande pour récupérer le fichier communes_france :

```bash
curl -L -o data/raw/communes_france.csv "https://www.data.gouv.fr/fr/datasets/r/dbe8a621-a9c4-4bc3-9cae-be1699c5ff25"
```

## Livrable 4 - Visualisation & API

Ce livrable permet de représenter des données agrégées de 2021 à 2024 à travers plusieurs graphique et une API Flask.

Lors de livrable les bibliothèques suivantes seront utilisées : **folium** **seaborn** **flask**

Et Voici le résultat de ce livrable avec des captures d'écrans.

### 1ere partie du livrable - Visualisations des données via des graphiques et une carte de la France

- _Premier graphique :_ Evolution des prix au m2 (via Matplotlib)

![alt text](<visualisations/Evolution prix moyen au m2.png>)

- _Deuxieme graphique :_ Volumes de ventes par mois (via Matplotlib)

![alt text](<visualisations/Volume de ventes par mois.png>)

- _Troisième graphique :_ Distribution Maison VS Appartement (via Seaborn)

![alt text](<visualisations/Distribution des prix au m2.png>)

- _Carte interactive :_ Carte choroplèthe de la France du prix au m2 par département (via Folium)

![alt text](<visualisations/Carte de la France.png>)

### 2e partie du livrable - API Flask

3 requètes ont été implémenté dans l'API Flask:

- 1ere requete : Statistique d'un département

![alt text](<visualisations/requete 1.png>)

- 2e requete : Evolution nationale par année

![alt text](<visualisations/requete 2.png>)

- 3e requete : Un top des communes (possiblité de choisir le nombre de communes dans le top)

![alt text](<visualisations/requete 3.png>)

## Livrable 5 - Stockage distribué

Le but de ce Livrable est de stocker des données de manière distribuée.

Lors de ce livrable nous utiliserons les bibliothèques suivantes : **pymongo** **boto3**

Lors de ce livrable nous avons mis en place MinIO grâce à Docker.
MinIO nous a permis de créer différents Buckets.
1er Bucket 'dataimmo_raw' où nous retrouverons toutes nos données 'non trié/filtré...'
Le code du MinIO/main.py : lis le contenu du fichier dvf_full_2024.csv.gz présent dans le bucket 'dataimmo_raw'.
Ce fichier est ensuite manipulé pour être filtré, afin d'y garder seulement les données pertinentes.
Lorsque ce fichier a été filtré, il est exporté vers un nouveau bucket 'dataimmo_clean'.
Et pour finir, un dernier calcul des agrégats finaux est effectué, et stocké dans MongoDB.

Afin de lancer MinIO via Docker, il faudra exécuter la commande suivante à la racine du projet :

```bash
docker compose up -d
```

Et pour l'arrêter :

```bash
docker compose down
```

Voici le lien de l'interface web de MinIO : http://localhost:9001/minio/login
user : minioadmin
password : minioadmin

Et il faudra également démarrer MongoDB afin d'y stocker les agrégats finaux qui seront utilisé par l'API:

Si MongoDB est installé localement sur votre machine : Assuez-vous que le service mongod est démarré (par défaut sur le port 27017)

Sinon faire la commande suivante (avec Docker):

```bash
docker run -d -p 27017:27017 --name mongodb mongo
```

Nous avons par la suite adapter notre api du livrable 4 pour qu'elle puisse communiquer avec MongoDB. Présente dans MinIO/api.py.

<u>Dans quels cas Spark est-il le mauvais outil : </u>

Comme vu lors du benchmark, Spark est intéressant pour des calculs avec de grosses données, cependant il n'est pas toujours nécessaire.
Si l'on essaie de traiter un petit fichier de quelques centaines/milier de lignes Spark devient une mauvaise idée. Le temps que met Spark à démarrer et à distribuer des tâches sur la machines, fait qu'il est beaucoup plus lent qu'un script Pandas.
Spark est également inadapté pour faire des caluls en temps réel ou répondre instantanément aux intéractions d'un utilisateur (sur un site web ou une application par exemple). Il est plus utile et intéressant de l'utiliser sur des gros fichiers de données en arrière plan (par exemple le faire tourner la nuit pour mettre à jour une base de données selon les données/informations du jour). Mais lorsque l'on souhaite rechercher une information précise instantanément (ou quasiment), on se rend compte qu'une base de donnée comme MongoDB est plus efficace.
