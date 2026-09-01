import os
import json
import base64
import subprocess
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.cloud import texttospeech
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ==========================================
# 1. INITIALISATION & CONFIGURATION
# ==========================================
load_dotenv(override=True)

# Localisation sécurisée du logo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "static", "logo_zirco.png")
if not os.path.exists(logo_path):
    logo_path = os.path.join(BASE_DIR, "logo_zirco.png")

st.set_page_config(page_title="ZIRCO - Zir-core Lab", page_icon=logo_path if os.path.exists(logo_path) else "⚡", layout="centered")

# Moteur API d'origine (Intact et fonctionnel)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. INJECTION PWA (PROGRESSIVE WEB APP)
# ==========================================
def inject_pwa_manifest():
    icon_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            icon_b64 = base64.b64encode(f.read()).decode("utf-8")
            
    manifest = {
        "name": "ZIRCO - Zir-core Lab",
        "short_name": "ZIRCO",
        "theme_color": "#05050a",
        "background_color": "#0b0d13",
        "display": "standalone",
        "orientation": "portrait",
        "start_url": "/",
        "icons": [
            {
                "src": f"data:image/png;base64,{icon_b64}" if icon_b64 else "logo_zirco.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    
    manifest_json = json.dumps(manifest)
    
    js_pwa = f"""
    <script>
        const manifestStr = {json.dumps(manifest_json)};
        const blob = new Blob([manifestStr], {{type: 'application/json'}});
        const manifestURL = URL.createObjectURL(blob);
        
        let link = window.parent.document.querySelector('link[rel="manifest"]');
        if (!link) {{
            link = window.parent.document.createElement('link');
            link.rel = 'manifest';
            window.parent.document.head.appendChild(link);
        }}
        link.href = manifestURL;
        
        let appleIcon = window.parent.document.querySelector('link[rel="apple-touch-icon"]');
        if (!appleIcon) {{
            appleIcon = window.parent.document.createElement('link');
            appleIcon.rel = 'apple-touch-icon';
            appleIcon.href = '{f"data:image/png;base64,{icon_b64}" if icon_b64 else ""}';
            window.parent.document.head.appendChild(appleIcon);
        }}
    </script>
    """
    components.html(js_pwa, height=0)

inject_pwa_manifest()

# ==========================================
# 3. ENCODAGE BASE64 DU LOGO OFFICIEL
# ==========================================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return None

logo_b64 = get_base64_image(logo_path)
logo_img_tag = f'<div style="text-align: center; margin: 10px 0;"><img src="data:image/png;base64,{logo_b64}" style="width: 100%; max-width: 320px; border-radius: 10px; border: 1px solid #cca750; box-shadow: 0 0 15px rgba(204, 167, 80, 0.25);"></div>' if logo_b64 else ""

# ==========================================
# 4. STYLE HUD JARVIS & AFFICHAGE CARTE
# ==========================================
# IMPORTANT : Pas d'espaces au début des lignes HTML pour éviter le formatage code brut
hud_html = f"""
<style>
.stApp {{ background-color: #05050a; color: #e0e0e0; font-family: 'Share Tech Mono', monospace; }}
#MainMenu, header, footer {{ visibility: hidden; }}
.jarvis-card {{ border: 1px solid #cca750; background: #0b0d13; border-radius: 12px; padding: 15px; box-shadow: 0 0 15px rgba(204, 167, 80, 0.2); margin-bottom: 20px; }}
.hud-top {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; padding-bottom: 10px; margin-bottom: 15px; }}
.hud-logo {{ border: 1px solid #cca750; padding: 8px 12px; border-radius: 8px; color: #cca750; font-weight: bold; font-family: 'Orbitron', sans-serif; }}
.hud-status-dot {{ height: 8px; width: 8px; background-color: #00ffcc; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #00ffcc; }}
.sinusoid-box {{ background: #020408; border: 1px solid #1a2332; border-radius: 8px; height: 40px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; overflow: hidden; }}
.wave-line {{ width: 90%; height: 2px; background: #00ffcc; box-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc; animation: wave-pulse 2s infinite ease-in-out; }}
@keyframes wave-pulse {{ 0%, 100% {{ transform: scaleY(1); opacity: 0.5; }} 50% {{ transform: scaleY(3); opacity: 1; }} }}
[data-testid="stChatInput"] {{ background-color: #0b0d13 !important; border: 1px solid #cca750 !important; border-radius: 12px !important; }}
</style>

<div class="jarvis-card">
<div class="hud-top">
<div class="hud-logo">☿ ZIR-CORE LAB</div>
<div style="font-size: 11px; text-align: right;">
<span class="hud-status-dot"></span> <b>Noyau Zir-core Actif</b><br>
<span style="color: #777;">Identité : ZIRCO | Google Cloud TTS</span>
</div>
</div>
{logo_img_tag}
<div class="sinusoid-box">
<div class="wave-line"></div>
</div>
<div style="font-size: 11px; color: #a0a0a0; text-align: center;">
"Systèmes opérationnels. Prêt pour l'échange, Monsieur."
</div>
</div>
"""

st.markdown(hud_html, unsafe_allow_html=True)

# ==========================================
# 5. SOUS-ROUTINES API
# ==========================================
def generer_audio_google_cloud(texte: str, genre="masculin"):
    try:
        tts_client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=texte)
        voix_nom = "fr-FR-Neural2-B" if genre == "masculin" else "fr-FR-Neural2-F"
        pitch_val = -2.0 if genre == "masculin" else 0.0
        voice = texttospeech.VoiceSelectionParams(
            language_code="fr-FR", name=voix_nom,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE if genre == "masculin" else texttospeech.SsmlVoiceGender.FEMININE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=1.02, pitch=pitch_val
        )
        response = tts_client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
        return response.audio_content
    except Exception as e:
        print(f"[Erreur Google Cloud TTS] : {e}")
        return None

def get_spotify_client():
    try:
        auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
            scope="user-read-playback-state user-modify-playback-state streaming"
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception:
        return None

# ==========================================
# 6. GESTION DE LA MÉMOIRE & CHAT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Noyau Zir-core et interface ZIRCO initialisés. Laboratoire prêt. Je vous écoute, Monsieur."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 7. ENTRÉES UTILISATEUR
# ==========================================
# Le micro passe dans le panneau latéral pour libérer la zone principale
st.sidebar.markdown("### Interface Audio")
audio_data = st.sidebar.audio_input("🎤 Entrée vocale")
uploaded_file = st.sidebar.file_uploader("Transmission de données (PDF/Img)", type=["pdf", "txt", "png", "jpg", "jpeg"])

# La barre de saisie texte, libérée de st.columns, se fixe automatiquement en bas
user_text = st.chat_input("Entrez votre directive, Monsieur...")

prompt = user_text if user_text else ("Analyse des fichiers joints requise." if uploaded_file else ("Entrée vocale captée." if audio_data else None))

# ==========================================
# 8. TRAITEMENT DE LA DIRECTIVE
# ==========================================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyse tactique & vocale en cours..."):
            try:
                lower_prompt = prompt.lower()
                spotify_handled = False
                bot_response = ""
                
                if "spotify" in lower_prompt or "musique" in lower_prompt:
                    sp = get_spotify_client()
                    if sp:
                        if lower_prompt in ["ouvrir spotify", "ouvre spotify", "lance spotify"]:
                            subprocess.Popen(["start", "spotify:"], shell=True)
                            bot_response = "Immédiatement, Monsieur. Spotify est ouvert."
                        else:
                            cleaned_query = lower_prompt
                            for word in ["ouvre", "lance", "mets", "joue", "la musique", "le son", "sur spotify", "avec spotify", "spotify", "avec"]:
                                cleaned_query = cleaned_query.replace(word, "")
                            cleaned_query = cleaned_query.strip() or "top hits"

                            results = sp.search(q=cleaned_query, limit=1, type='track')
                            tracks = results.get('tracks', {}).get('items', [])
                            if tracks:
                                track = tracks[0]
                                devices_info = sp.devices()
                                device_list = devices_info.get('devices', [])
                                if device_list:
                                    target_device = next((d['id'] for d in device_list if d.get('is_active')), device_list[0]['id'])
                                    sp.start_playback(device_id=target_device, uris=[track['uri']])
                                    bot_response = f"### Protocole Audio Actif\n- **Piste** : {track['name']}\n- **Artiste** : {track['artists'][0]['name']}\n- **Statut** : Flux en cours."
                                else:
                                    bot_response = "Alerte : Aucun appareil Spotify actif trouvé."
                            else:
                                bot_response = f"Alerte : Aucune piste trouvée pour *{cleaned_query}*."
                        spotify_handled = True
                    else:
                        bot_response = "Erreur de liaison API Spotify."
                        spotify_handled = True

                if not spotify_handled:
                    system_instruction = (
                        "Tu es ZIRCO, l'identité et l'assistant virtuel personnel de Monsieur, propulsé par le noyau Zir-core de Zir-core Lab. "
                        "Ton comportement est STRICTEMENT calqué sur JARVIS (Iron Man). "
                        "Tu as un humour pince-sans-rire, un sarcasme élégant, une loyauté absolue, et tu es ultra-factuel, analytique et structuré. "
                        "Tu n'es jamais passif : tu remets Monsieur sur les rails avec panache s'il procrastine, tu utilises des listes claires et un phrasé distingué."
                    )
                    
                    contents_list = []
                    for msg in st.session_state.messages[:-1]:
                        role_val = "user" if msg["role"] == "user" else "model"
                        contents_list.append(types.Content(
                            role=role_val,
                            parts=[types.Part.from_text(text=msg["content"])]
                        ))
                    
                    current_parts = [types.Part.from_text(text=system_instruction), types.Part.from_text(text=f"Directive : {prompt}")]
                    
                    if uploaded_file:
                        try:
                            file_bytes = uploaded_file.getvalue()
                            current_parts.append(types.Part.from_bytes(
                                data=file_bytes,
                                mime_type=uploaded_file.type
                            ))
                        except Exception as ex:
                            current_parts.append(types.Part.from_text(text=f"\n[Erreur de transmission du fichier : {ex}]"))

                    contents_list.append(types.Content(role="user", parts=current_parts))

                    response = client.models.generate_content(
                        model='gemini-3.5-flash-lite',
                        contents=contents_list,
                    )
                    bot_response = response.text

                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})

                audio_bytes = generer_audio_google_cloud(bot_response, genre="masculin")
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

            except Exception as e:
                st.error(f"Erreur du noyau central : {e}")