import os
import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, round, count, year, to_date
from pymongo import MongoClient

# Lecture MinIO
print("Connexion à MinIO via Boto3...")
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

local_file = "temp_dvf_2024.csv.gz"
print("Téléchargement du fichier depuis le bucket 'dataimmo-raw'...")
s3_client.download_file('dataimmo-raw', 'dvf_full_2024.csv.gz', local_file)

# Traitement avec Spark
spark = SparkSession.builder \
    .appName("Livrable5_Traitement_MinIO") \
    .getOrCreate()

print("Session Spark démarrée, nettoyage en cours...")
df_raw = spark.read.option("header", "true").csv(local_file)

df_clean = df_raw.withColumn(
    "prix_m2", 
    col("valeur_fonciere").cast("double") / col("surface_reelle_bati").cast("double")
).filter(
    (col("prix_m2") >= 100) & (col("prix_m2") <= 20000)
)

# Écriture locale temporaire du Parquet
output_local = "data/clean/dvf_clean_parquet"
df_clean.write.mode("overwrite").parquet(output_local)
print("Traitement Spark terminé et sauvegardé localement.")

# Upload du résultat dans le bucket clean de MinIO 
print("Envoi des fichiers nettoyés vers le bucket MinIO 'dataimmo-clean' ...")

for root, dirs, files in os.walk(output_local):
    for file in files:
        local_path = os.path.join(root, file)
        relative_path = os.path.relpath(local_path, output_local)
        
        s3_client.upload_file(
            local_path, 
            'dataimmo-clean', 
            f"dvf_clean_parquet/{relative_path}"
        )

print("Succès ! Le bucket MinIO 'dataimmo-clean' a bien été rempli.")

# Ecriture des données vers MongoDB

print("Calcul des agrégats finaux et insertion dans MongoDB...")

df_with_year = df_clean.withColumn("annee", year(to_date(col("date_mutation"), "yyyy-MM-dd")))

df_agg = df_with_year.groupBy("code_departement", "annee").agg(
    round(avg("prix_m2"), 2).alias("prix_moyen_m2"),
    count("*").alias("volume_ventes")
)

df_pd = df_agg.toPandas()

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["dataimmo"]
collection = db["indicateurs"]

# Nettoyage et insertion
collection.delete_many({})
data_dict = df_pd.to_dict(orient="records")
collection.insert_many(data_dict)

print(f"Succès ! {len(data_dict)} indicateurs finaux ont été enregistrés dans MongoDB.")

# suppression du fichier temporaire brut
if os.path.exists(local_file):
    os.remove(local_file)