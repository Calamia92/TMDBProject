import os
import requests
import time
from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv
from supabase import create_client, Client

# Charger les variables d'environnement
load_dotenv()

# Connexion à Supabase
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Configuration de TMDB
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"}

if not TMDB_API_KEY or not TMDB_READ_ACCESS_TOKEN:
    raise ValueError("⚠️ Les clés API TMDB ne sont pas définies dans .env !")

# Initialisation de Flask
app = Flask(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Paramètres pour le retry des requêtes TMDB
MAX_RETRIES = 5
RETRY_DELAY = 2


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/movies/", methods=["GET"])
def search_movie():
    """Redirige vers la bonne URL avec l'ID du film"""
    movie_id = request.args.get("movie_id")

    if not movie_id or not movie_id.isdigit():
        return jsonify({"error": "Veuillez entrer un ID de film valide."}), 400

    return redirect(url_for("get_movie_by_id", movie_id=int(movie_id)))


@app.route("/movies/<int:movie_id>")
@app.route("/movies/<path:movie_id>")
def get_movie_by_id(movie_id):
    """Récupère un film par son ID TMDB avec gestion des erreurs et retries"""

    # Vérification que l'ID est bien un entier
    try:
        movie_id = int(movie_id)
    except ValueError:
        return jsonify({"error": "L'ID du film doit être un entier valide."}), 400

    url = f"{TMDB_BASE_URL}/movie/{movie_id}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                filtered_data = {
                    "title": data.get("title"),
                    "release_date": data.get("release_date"),
                    "genres": [genre["name"] for genre in data.get("genres", [])],
                    "popularity": data.get("popularity"),
                    "vote_average": data.get("vote_average"),
                }
                return render_template("movie.html", movie=data)

            # Gestion des erreurs HTTP
            elif response.status_code == 404:
                return jsonify({"error": "Film non trouvé"}), 404
            elif response.status_code == 401:
                return jsonify({"error": "Clé API invalide ou absente"}), 401
            elif response.status_code == 403:
                return jsonify({"error": "Accès refusé"}), 403
            elif response.status_code == 429:
                print(f"⚠️ Trop de requêtes (429), tentative {attempt}/{MAX_RETRIES}, pause...")
                time.sleep(RETRY_DELAY * attempt)
            elif response.status_code in [500, 503]:
                print(f"⚠️ Serveur TMDB indisponible ({response.status_code}), tentative {attempt}/{MAX_RETRIES}")

            else:
                return jsonify({"error": f"Erreur API TMDB ({response.status_code})", "message": response.text}), response.status_code

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout sur l'API TMDB, tentative {attempt}/{MAX_RETRIES}...")
        except requests.exceptions.RequestException as e:
            print(f"🌐 Erreur réseau : {e}, tentative {attempt}/{MAX_RETRIES}")

        # Pause exponentielle avant retry
        time.sleep(RETRY_DELAY * attempt)

    return jsonify({"error": "Impossible de récupérer les données après plusieurs tentatives"}), 503


if __name__ == '__main__':
    app.run(debug=True)
