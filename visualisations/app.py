from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

PATH_PARQUET = "../data/clean/dvf_agg_parquet"

try:
    df_agg = pd.read_parquet(PATH_PARQUET)
    if "code_departement" in df_agg.columns:
        df_agg["code_departement"] = df_agg["code_departement"].astype(str).str.zfill(2)
except Exception as e:
    print(f"Erreur lors du chargement des données : {e}")
    df_agg = pd.DataFrame()


@app.route("/api/departements/<code>/stats", methods=["GET"])
def get_departement_stats(code):
    if df_agg.empty:
        return jsonify({"error": "Données indisponibles"}), 503
    
    code = code.zfill(2)
    df_filtre = df_agg[df_agg["code_departement"] == code]

    if df_filtre.empty:
        return jsonify({'error': "Département non trouvé"}), 404

    return jsonify({
        "departement": code,
        "resultats": df_filtre.to_dict(orient="records")
    })

@app.route("/api/evolution", methods=["GET"])
def get_evolution():
    if df_agg.empty:
        return jsonify({"error": "Données indisponibles"}), 503

    if "annee" in df_agg.columns and "prix_moyen_m2" in df_agg.columns:
        evol = df_agg.groupby("annee")["prix_moyen_m2"].mean().reset_index()
        return jsonify(evol.to_dict(orient="records"))

    return jsonify({"error": "Colonne 'annee' ou 'prix_moyen_m2' manquante"}), 500

@app.route("/api/top-communes", methods=["GET"])
def get_top_communes():
    limit = request.args.get("limit", default = 10, type = int)

    if df_agg.empty:
        return jsonify({"error": "Données non disponibles"}), 503

    try:
        top_deps = df_agg.sort_values(by="prix_moyen_m2", ascending=False).head(limit)
        
        return jsonify({
            "limit": limit,
            "top_departements": top_deps.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True, port=5000)
