import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'URL de l'API Flask
FLASK_API_URL = "http://127.0.0.1:5000"

st.title("🎬 Recherche de films TMDB")

# Champ de saisie pour l'ID du film
movie_id = st.text_input("Entrez l'ID du film :", "")

if movie_id:
    if movie_id.isdigit():
        # Appeler l'API Flask pour récupérer les détails du film
        response = requests.get(f"{FLASK_API_URL}/movies/{movie_id}")

        st.write(f"Statut de la réponse : {response.status_code}")  # Debug

        if response.status_code == 200:
            try:
                movie = response.json()

                # Affichage des détails du film
                st.header(movie["title"])
                if movie.get('poster_path'):
                    st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}")
                st.write(f"📅 **Date de sortie :** {movie['release_date']}")
                st.write(f"⭐ **Note moyenne :** {movie['vote_average']}/10")
                st.write(f"🎭 **Genres :** {', '.join([genre['name'] for genre in movie['genres']])}")
                st.write(f"📜 **Synopsis :** {movie['overview']}")
            except requests.exceptions.JSONDecodeError:
                st.error("❌ Erreur de décodage JSON. L'API ne renvoie pas un format valide.")
        elif response.status_code == 404:
            st.error("❌ Film non trouvé !")
        else:
            st.error(f"Erreur {response.status_code} : {response.text}")
    else:
        st.warning("⚠️ Veuillez entrer un ID numérique valide.")
