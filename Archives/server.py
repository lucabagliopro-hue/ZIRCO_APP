import os
import base64
import asyncio
import edge_tts
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from google import genai
from google.genai import types
from spotify_handler import SpotifyHandler

load_dotenv(override=True)
app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
client_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Initialisation du module Spotify
try:
    spotify = SpotifyHandler()
    print("✅ [ZIRCO] Contrôleur Spotify initialisé avec succès.")
except Exception as e:
    spotify = None
    print(f"⚠️ [ZIRCO] Spotify non initialisé : {e}")

system_instruction = (
    "Tu es ZIRCO, le système de bord et assistant virtuel personnel de Monsieur (style JARVIS). "
    "Tu t'adresses à l'utilisateur en l'appelant 'Monsieur'. "
    "Fais des réponses très courtes (1 ou 2 phrases maximum pour l'oral)."
)

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=0.7,
)

chat = client_gemini.chats.create(model="gemini-3.5-flash-lite", config=config) if client_gemini else None

# --- SYNTHÈSE VOCALE EDGE-TTS (Fichiers temporaires convertis en Base64) ---
def generate_audio_edge_tts(text: str) -> str:
    try:
        clean_text = text.replace("**", "").replace("*", "")
        audio_file = "temp_response.mp3"
        
        async def _generate():
            communicate = edge_tts.Communicate(clean_text, "fr-FR-HenriNeural")
            await communicate.save(audio_file)

        asyncio.run(_generate())

        if os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
            os.remove(audio_file)
            return encoded
        return ""
    except Exception as e:
        print(f"⚠️ Erreur Edge-TTS : {e}")
        return ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    try:
        data = request.json or {}
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"error": "Message vide"}), 400

        msg_lower = user_message.lower()
        reply_text = ""

        # --- ROUTEUR SPOTIFY ---
        if spotify:
            if any(mot in msg_lower for mot in ["pause spotify", "stop spotify", "mets en pause", "arrête la musique"]):
                reply_text = f"Affirmatif Monsieur. {spotify.pause()}"
            elif any(mot in msg_lower for mot in ["reprend la musique", "play spotify", "relance spotify", "reprend spotify"]):
                reply_text = f"Tout de suite, Monsieur. {spotify.play()}"
            elif any(mot in msg_lower for mot in ["musique suivante", "piste suivante", "skip", "morceau suivant"]):
                reply_text = f"Bien reçu. {spotify.next_track()}"
            elif "mets" in msg_lower or "lance" in msg_lower or "joue" in msg_lower or "écouter" in msg_lower:
                query = user_message
                for noise in ["lance", "mets", "joue", "écouter", "sur spotify", "de la musique", "du", "de"]:
                    query = query.lower().replace(noise, "").strip()
                
                if query:
                    reply_text = f"Initialisation du flux musical, Monsieur. {spotify.search_and_play(query)}"
                else:
                    reply_text = f"Reprise de la lecture. {spotify.play()}"

        # --- REQUÊTE VIA LE SDK GEMINI ---
        if not reply_text:
            if not chat:
                reply_text = "Erreur critique : Client Gemini non initialisé."
            else:
                response = chat.send_message(user_message)
                reply_text = response.text

        # Génération audio via Edge-TTS
        audio_b64 = generate_audio_edge_tts(reply_text)

        return jsonify({
            "response": reply_text,
            "audio": audio_b64,
            "action": "spotify_executed" if "spotify" in msg_lower else None
        })

    except Exception as e:
        print(f"⚠️ Erreur critique serveur : {e}")
        return jsonify({
            "response": "Mes excuses, Monsieur. Une surcharge temporaire perturbe mes matrices.",
            "audio": "",
            "action": None
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)