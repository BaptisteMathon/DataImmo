from flask import Flask, jsonify, request
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)

# Connexion à MongoDB 
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["dataimmo"]
    collection = db["indicateurs"]
    print("Connexion à MongoDB réussie !")
except Exception as e:
    print(f"Erreur de connexion à MongoDB : {e}")
    collection = None


@app.route("/api/departements/<code>/stats", methods=["GET"])
def get_departement_stats(code):
    if collection is None:
        return jsonify({"error": "Base de données non disponible"}), 503
    
    code = code.zfill(2)
    
    resultats = list(collection.find({"code_departement": code}, {"_id": 0}))

    if not resultats:
        return jsonify({'error': "Département non trouvé"}), 404

    return jsonify({
        "departement": code,
        "resultats": resultats
    })


@app.route("/api/evolution", methods=["GET"])
def get_evolution():
    if collection is None:
        return jsonify({"error": "Base de données non disponible"}), 503

    tous_les_data = list(collection.find({}, {"_id": 0}))
    
    if not tous_les_data:
        return jsonify({"error": "Aucune donnée trouvée"}), 404

    df_agg = pd.DataFrame(tous_les_data)

    if "annee" in df_agg.columns and "prix_moyen_m2" in df_agg.columns:
        evol = df_agg.groupby("annee")["prix_moyen_m2"].mean().reset_index()
        return jsonify(evol.to_dict(orient="records"))

    return jsonify({"error": "Colonnes requises manquantes"}), 500


@app.route("/api/top-communes", methods=["GET"])
def get_top_communes():
    limit = request.args.get("limit", default=10, type=int)

    if collection is None:
        return jsonify({"error": "Base de données non disponible"}), 503

    try:
        tous_les_data = list(collection.find({}, {"_id": 0}))
        if not tous_les_data:
            return jsonify({"error": "Aucune donnée trouvée"}), 404
            
        df_agg = pd.DataFrame(tous_les_data)
        top_deps = df_agg.sort_values(by="prix_moyen_m2", ascending=False).head(limit)
        
        return jsonify({
            "limit": limit,
            "top_departements": top_deps.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True, port=5000)