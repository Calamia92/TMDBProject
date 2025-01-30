import os
import requests
from flask import Flask, jsonify
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
    return "Bienvenue sur l'API Flask avec TMDB !"

@app.route('/users')
def get_users():
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)


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

@app.route('/movies/<int:movie_id>')
def get_movie_by_id(movie_id):
    """Récupère un film par son ID TMDB"""
    url = f"{TMDB_BASE_URL}/movie/{movie_id}" 
    response = requests.get(url, headers=headers)

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
    
    else:    
        return jsonify({"error": "Erreur TMDB", "status_code": response.status_code, "message": response.text})
        

if __name__ == '__main__':
    app.run(debug=True)