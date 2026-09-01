import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

class SpotifyHandler:
    def __init__(self):
        scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope=scope,
            open_browser=False
        ))

    def play(self):
        try:
            self.sp.start_playback()
            return "Lecture reprise sur Spotify."
        except Exception as e:
            return f"Erreur lecture : {e}"

    def pause(self):
        try:
            self.sp.pause_playback()
            return "Spotify mis en pause."
        except Exception as e:
            return f"Erreur pause : {e}"

    def next_track(self):
        try:
            self.sp.next_track()
            return "Piste suivante lancée."
        except Exception as e:
            return f"Erreur changement de piste : {e}"

    def search_and_play(self, query: str):
        try:
            results = self.sp.search(q=query, limit=1, type='track')
            tracks = results.get('tracks', {}).get('items', [])
            if tracks:
                track_uri = tracks[0]['uri']
                track_name = tracks[0]['name']
                artist = tracks[0]['artists'][0]['name']
                self.sp.start_playback(uris=[track_uri])
                return f"Lecture en cours : {track_name} par {artist}."
            return f"Aucun titre trouvé pour : {query}"
        except Exception as e:
            return f"Erreur recherche : {e}"