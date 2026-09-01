import os
import asyncio
import edge_tts
from playsound import playsound
import sounddevice as sd
from scipy.io import wavfile
import numpy as np
from google import genai
from google.genai import types

import os
from dotenv import load_dotenv

load_dotenv()
CLE_API = os.getenv("GEMINI_API_KEY") 

VOIX_JARVIS = "fr-FR-HenriNeural"
client = genai.Client(api_key=CLE_API)

def parler(texte):
    texte_propre = texte.replace("**", "").replace("*", "")
    communicate = edge_tts.Communicate(texte_propre, VOIX_JARVIS)
    asyncio.run(communicate.save("reponse.mp3"))
    try:
        playsound("reponse.mp3")
    except Exception as e:
        print(f"⚠️ Erreur audio : {e}")
    if os.path.exists("reponse.mp3"):
        try: os.remove("reponse.mp3")
        except: pass

def ecouter_micro():
    fs = 16000  # Fréquence d'échantillonnage
    duree = 5   # Enregistre par blocs de 5 secondes
    
    print("\n🎙️ JARVIS : Écoute en cours (parlez pendant 5s)...")
    # Enregistrement audio via sounddevice (sans besoin de pyaudio)
    enregistrement = sd.rec(int(duree * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Attend la fin des 5 secondes
    
    print("🧠 JARVIS : Analyse de l'audio...")
    wavfile.write("input.wav", fs, enregistrement)
    
    try:
        # Envoi direct du fichier audio brut à Gemini pour transcription et analyse
        with open("input.wav", "rb") as f:
            audio_bytes = f.read()
            
        # Demande à Gemini de transcrire ce qu'il entend
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                "Transcris fidèlement en texte ce que tu entends dans cet audio en français. Si c'est du bruit ou du silence, réponds uniquement par le mot 'VIDE'."
            ]
        )
        texte = response.text.strip()
        
        # Nettoyage du fichier temporaire
        if os.path.exists("input.wav"): os.remove("input.wav")
            
        if "VIDE" in texte or not texte:
            return ""
            
        print(f"✨ Vous avez dit : {texte}")
        return texte
    except Exception as e:
        print(f"⚠️ Erreur transcription : {e}")
        return ""

def lancer_jarvis():
    msg_intro = "Systèmes vocaux initialisés via la matrice sounddevice. Je vous écoute, Monsieur."
    print(f"🤖 JARVIS : {msg_intro}")
    parler(msg_intro)
    
    config = types.GenerateContentConfig(
        system_instruction=(
            "Tu es J.A.R.V.I.S., l'assistant virtuel de Tony Stark. "
            "Tu t'adresses à l'utilisateur en l'appelant 'Monsieur'. "
            "Fais des réponses très courtes (1 ou 2 phrases maximum pour l'oral)."
        ),
        temperature=0.7,
    )
    
    chat = client.chats.create(model="gemini-3.5-flash", config=config)
    
    while True:
        utilisateur = ecouter_micro()
        
        if not utilisateur.strip():
            continue
            
        if any(mot in utilisateur.lower() for mot in ["quitter", "stop", "veille", "fermer"]):
            msg_fin = "Systèmes mis en veille. Passez une bonne journée, Monsieur."
            print(f"\n🤖 JARVIS : {msg_fin}")
            parler(msg_fin)
            break
            
        try:
            response = chat.send_message(utilisateur)
            print(f"\n🤖 JARVIS : {response.text}")
            parler(response.text)
        except Exception as e:
            print(f"\n🤖 JARVIS : Erreur lors du traitement : {e}")

if __name__ == "__main__":
    lancer_jarvis()
