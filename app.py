import os
import requests
import time
from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_caching import Cache
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

if not all([os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"), os.getenv("TMDB_API_KEY"), os.getenv("TMDB_READ_ACCESS_TOKEN")]):
    raise ValueError("⚠️ Certaines variables d'environnement sont manquantes ! Vérifiez votre fichier .env")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"}

app = Flask(__name__)
CORS(app)

TMDB_BASE_URL = "https://api.themoviedb.org/3"

cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 3600})

executor = ThreadPoolExecutor(max_workers=20)

MAX_RETRIES = 5


@app.route("/")
def home():
    return jsonify({"message": "Bienvenue sur l'API TMDB avec Flask"})


@app.route("/movies/", methods=["GET"])
def search_movie():
    """Redirige vers la bonne URL avec l'ID du film"""
    movie_id = request.args.get("movie_id")

    if not movie_id or not movie_id.isdigit():
        return jsonify({"error": "Veuillez entrer un ID de film valide."}), 400

    return redirect(url_for("get_movie_by_id", movie_id=int(movie_id)))


@cache.memoize(timeout=3600)
def fetch_movie_from_tmdb(movie_id):
    """Récupère un film par son ID TMDB avec gestion des erreurs et retries"""

    url = f"{TMDB_BASE_URL}/movie/{movie_id}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                return response.json()

            elif response.status_code in [404, 401, 403]:
                error_messages = {
                    404: "Film non trouvé",
                    401: "Clé API invalide ou absente",
                    403: "Accès refusé"
                }
                return {"error": error_messages[response.status_code]}, response.status_code

            elif response.status_code == 429:
                wait_time = 2**attempt
                print(f"⚠️ Trop de requêtes (429), tentative {attempt}/{MAX_RETRIES}, pause {wait_time}s...")
                time.sleep(wait_time)

            elif response.status_code in [500, 503]:
                print(f"⚠️ Serveur TMDB indisponible ({response.status_code}), tentative {attempt}/{MAX_RETRIES}")

            else:
                return {"error": f"Erreur API TMDB ({response.status_code})", "message": response.text}, response.status_code

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout sur l'API TMDB, tentative {attempt}/{MAX_RETRIES}...")
        except requests.exceptions.RequestException as e:
            print(f"🌐 Erreur réseau : {e}, tentative {attempt}/{MAX_RETRIES}")

        time.sleep(2**attempt)

    return {"error": "Impossible de récupérer les données après plusieurs tentatives"}, 503


@app.route("/movies/<int:movie_id>")
def get_movie_by_id(movie_id):
    """Gestionnaire Flask optimisé avec cache et exécution parallèle"""

    future = executor.submit(fetch_movie_from_tmdb, movie_id)
    movie_data = future.result()

    return jsonify(movie_data)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
