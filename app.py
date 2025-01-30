import os
import requests
from flask import Flask, render_template,jsonify, request, redirect, url_for
from dotenv import load_dotenv
from supabase import create_client, Client
import time


load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"}

if not TMDB_API_KEY or not TMDB_READ_ACCESS_TOKEN:
    raise ValueError("⚠️ Les clés API TMDB ne sont pas définies dans .env !")

app = Flask(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"


@app.route("/")
def home():
    return render_template("home.html")


    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Erreur TMDB", "status_code": response.status_code, "message": response.text})

MAX_RETRIES = 5
RETRY_DELAY = 2

@app.route('/movies/<int:movie_id>')
@app.route('/movies/<path:movie_id>')
def get_movie_by_id(movie_id):
    """Récupère un film par son ID TMDB avec gestion des erreurs et retries"""
    try:
        movie_id = int(movie_id)
    except ValueError:
        return jsonify({"error": "L'ID du film doit être un entier valide."}), 400

    url = f"{TMDB_BASE_URL}/movie/{movie_id}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)

            # Si la requête réussit, on retourne les données filtrées
            if response.status_code == 200:
                data = response.json()
                filtered_data = {
                    "title": data.get("title"),
                    "release_date": data.get("release_date"),
                    "genres": [genre["name"] for genre in data.get("genres", [])],
                    "popularity": data.get("popularity"),
                    "vote_average": data.get("vote_average"),
                }
                return jsonify(filtered_data)

            # Gestion des erreurs HTTP courantes
            elif response.status_code == 404:
                return jsonify({"error": "Film non trouvé"}), 404
            elif response.status_code == 401:
                return jsonify({"error": "Clé API invalide ou absente"}), 401
            elif response.status_code == 403:
                return jsonify({"error": "Accès refusé"}), 403
            elif response.status_code in [500, 503]:
                print(f"⚠️ Serveur TMDB indisponible ({response.status_code}), tentative {attempt}/{MAX_RETRIES}")
            elif response.status_code == 429:
                print(f"⚠️ Trop de requêtes (429), tentative {attempt}/{MAX_RETRIES}, pause...")
                time.sleep(RETRY_DELAY * attempt)  # Pause exponentielle
        return render_template("movie.html", movie=data)
            else:
                return jsonify({"error": f"Erreur API TMDB ({response.status_code})", "message": response.text}), response.status_code

        except requests.exceptions.Timeout:
            print(f"Timeout sur l'API TMDB, tentative {attempt}/{MAX_RETRIES}...")
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau : {e}, tentative {attempt}/{MAX_RETRIES}")

        time.sleep(RETRY_DELAY * attempt)  # Pause exponentielle

    return jsonify({"error": "Impossible de récupérer les données après plusieurs tentatives"}), 503

        return render_template("movie.html", movie=None, error="Film non trouvé.")


@app.route("/movies/", methods=["GET"])
def search_movie():
    """Redirige vers la bonne URL avec l'ID du film"""
    movie_id = request.args.get("movie_id")

    if not movie_id or not movie_id.isdigit():
        return jsonify({"error": "Veuillez entrer un ID de film valide."}), 400

    return redirect(url_for("get_movie_by_id", movie_id=int(movie_id)))

if __name__ == '__main__':
    app.run(debug=True)
