# 🎬 TMDB Movie API & Streamlit Interface

Ce projet est une application qui permet de rechercher des films via **l'API TMDB** et d'afficher les résultats sur une interface **Streamlit**.  
Le backend est construit avec **Flask** et gère les requêtes à TMDB, tandis que l'interface utilisateur est développée avec **Streamlit**.

---

## 🛠 **Installation des dépendances**
Avant de lancer le projet, assurez-vous d'avoir **Python 3.8+** installé.  
Puis, exécutez les commandes suivantes :

```sh
# 1️⃣ Clonez ce dépôt
git clone https://github.com/Calamia92/TMDBProject
cd tmdb-project

Optionnel
# 2️⃣ Créez et activez un environnement virtuel
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 3️⃣ Installez toutes les dépendances nécessaires
pip install -r requirements.txt

## 🛠 **Demarrer le projet**

python app.py

streamlit run streamlit_app.py     
