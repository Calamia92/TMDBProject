import os
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")

if not TMDB_API_KEY or not TMDB_READ_ACCESS_TOKEN:
    raise ValueError("⚠️ Les clés API TMDB ne sont pas définies dans .env !")

app = Flask(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"


@app.route("/")
def home():
    return "Bienvenue sur l'API Flask avec TMDB !"

@app.route('/users')
def get_users():
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)

if __name__ == '__main__':
    app.run(debug=True)
@app.route("/trending")
def get_trending_movies():
    """Récupère les films tendances de la semaine"""
    url = f"{TMDB_BASE_URL}/trending/movie/week"
    headers = {"Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Erreur TMDB", "status_code": response.status_code, "message": response.text})


@app.route("/search/<query>")
def search_movie(query):
    """Recherche un film par titre"""
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {"query": query, "api_key": TMDB_API_KEY}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Aucun résultat trouvé"}), response
