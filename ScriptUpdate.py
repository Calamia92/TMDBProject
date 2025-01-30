import os
import pandas as pd
import requests
import time
import schedule
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Connexion à Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
tmdb_api_key = os.getenv("TMDB_API_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# URL de l'API TMDB (exemple: films populaires)
TMDB_BASE_URL = "https://api.themoviedb.org/3"
headers = {"Authorization": f"Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1MmE5MWU4NWQ4NmFiMWYxNDc2ODEyMGU0MDE5OTc0YSIsIm5iZiI6MTczODIzMTkwNC42MTUsInN1YiI6IjY3OWI1MDYwYzM1NzIxODg1YTM0NTViMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.M54PYjaFzKzjvU5MWlS9nmUM6vVuS56EmE8BLLMHh1o"}

def fetch_tmdb_data():
    """Récupère les films depuis l'API TMDB"""
    url = f"{TMDB_BASE_URL}/movie/popular?language=en-US&page=1"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"❌ Erreur API TMDB: {response.status_code} - {response.text}")
        return []

def update_movies_table():
    """Mise à jour de la table `movies` dans Supabase"""
    print("🔄 Mise à jour des films en cours...")

    # Récupération des données TMDB
    movies_data = fetch_tmdb_data()
    if not movies_data:
        print("⚠️ Aucune donnée récupérée, mise à jour annulée.")
        return

    # Transformation en DataFrame
    df = pd.DataFrame(movies_data)

    # Renommer les colonnes pour correspondre à la table Supabase
    df = df.rename(columns={"id": "id_tmdb"})

    # Sélectionner les colonnes pertinentes
    df = df[["adult", "id_tmdb", "original_title", "popularity", "video"]]

    # Convertir en liste de dictionnaires
    data_to_upsert = df.to_dict(orient="records")

    # Upsert (insérer ou mettre à jour si l'id existe déjà)
    try:
        response = supabase.table("movies").upsert(data_to_upsert, on_conflict=["id_tmdb"]).execute()
        print(f"✅ Mise à jour réussie : {response}")
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")

# Planification automatique tous les 3 mois
# schedule.every(12).weeks.do(update_movies_table)
schedule.every(1).minute.do(update_movies_table)


print("📅 Planification activée : mise à jour tous les 3 mois...")

# Boucle d'exécution
while True:
    schedule.run_pending()
    time.sleep(60)  # Vérifie les tâches toutes les minutes
