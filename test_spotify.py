import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Chargement des identifiants depuis le .env
load_dotenv()

scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope,
    open_browser=True
))

# Test de connexion et lecture des appareils
devices = sp.devices()
print("[ZIRCO] Appareils détectés :", devices)

current = sp.current_playback()
if current and current.get('is_playing'):
    print(f"[ZIRCO] En cours : {current['item']['name']} - {current['item']['artists'][0]['name']}")
else:
    print("[ZIRCO] Module Spotify connecté. Aucun titre en lecture active.")