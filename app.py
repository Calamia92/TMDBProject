from flask import Flask, jsonify
from supabase import create_client, Client
import config
import requests

app = Flask(__name__)

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


@app.route('/users')
def get_users():
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)
@app.route('/')
def home():
    return "Bienvenue sur l'API Flask avec Supabase!"



if __name__ == '__main__':
    app.run(debug=True)
