import os
import requests
from flask import Flask, render_template,jsonify, request, redirect, url_for
from dotenv import load_dotenv
from supabase import create_client, Client

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


@app.route('/movies/<path:movie_id>')
def get_movie_by_id(movie_id):
    try:
        movie_id = int(movie_id)
    except ValueError:
        return jsonify({"error": "L'ID du film doit être un entier valide."}), 400

    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return render_template("movie.html", movie=data)
    else:
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
