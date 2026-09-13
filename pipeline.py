import argparse
import os
import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, round, count, year, to_date
from pymongo import MongoClient

def run_pipeline(annee):
    try:
        print(f"Début du pipeline pour l'année {annee}")

        # Connexion à MinIO
        print("Connexion à MinIO via Boto3...")
        s3_client = boto3.client(
            's3',
            endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin"
        )

        file_name = f"dvf_full_{annee}.csv.gz"
        local_file = f"temp_{file_name}"

        s3_client.download_file('dataimmo-raw', file_name, local_file)
        
        # Nettoyage et traitement des données avec Spark
        print("Nettoyage et traitement des données avec Spark")
        
        spark =  SparkSession.builder.appName(f"Pipeline DVF {annee}").getOrCreate()

        df_raw = spark.read.option("header", "true").csv(local_file)

        df_no_dup = df_raw.dropDuplicates(["id_mutation"])

        df_clean_nulls = df_no_dup.filter(col("valeur_fonciere").isNotNull() & col("surface_reelle_bati").isNotNull())

        df_clean = df_clean_nulls.withColumn(
            "prix_m2",
            col("valeur_fonciere").cast("double") / col("surface_reelle_bati").cast("double")
        ).filter(
            (col("prix_m2") >= 100) & (col("prix_m2") <= 20000)
        )

        # Export des données nettoyées vers MinIO dans le Bucket Clean Data
        output_local = f"data/clean/dvf_clean_{annee}"
        df_clean.write.mode("overwrite").parquet(output_local)

        print(f"Envoi des fichiers nettoyés vers le bucket MinIO 'dataimmo-clean'...")
        for root, dirs, files in os.walk(output_local):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, output_local)
                s3_client.upload_file(local_path, 'dataimmo-clean', f"parquet_{annee}/{rel_path}")

        # Calcul des agrégats finaux et insertion dans MongoDB
        print(f"Calcul des agrégats finaux et insertion dans MongoDB..")

        df_with_year = df_clean.withColumn("annee", year(to_date(col("date_mutation"), "yyyy-MM-dd")))
        df_agg = df_with_year.groupBy("code_departement", "annee").agg(
            round(avg("prix_m2"), 2).alias("prix_moyen_m2"),
            count("*").alias("volume_ventes")
        )

        df_pd = df_agg.toPandas()

        client = MongoClient("mongodb://localhost:27017/")
        db = client["dataimmo"]
        collection = db["indicateurs"]

        collection.delete_many({"annee": int(annee)})
        collection.insert_many(df_pd.to_dict(orient="records"))

        # Suppression du fichier temporaire
        if os.path.exists(local_file):
            os.remove(local_file)

        print(f"Pipeline terminé avec succès pour l'année {annee}")

        
    except Exception as e:
        print(f"Erreur critique dans le pipeline : {str(e)}")
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline DVF Data Lake & Cloud")
    parser.add_argument("--annee", type=str, required=True, help="Année à traiter (ex: 2024)")
    args = parser.parse_args()
    
    run_pipeline(args.annee)