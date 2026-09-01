import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
from gtts import gTTS
from sqlalchemy import create_engine, text

app = Flask(__name__)

# --- CONFIGURATION DE LA SECURITE ET DES CLES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- CONFIGURATION DE LA MEMOIRE PERSISTANTE (SUPABASE / POSTGRESQL) ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None

# Initialisation de la table de mémoire si elle n'existe pas
if engine:
    try:
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS zirco_memory (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    directive TEXT,
                    response TEXT
                );
            """))
            connection.commit()
    except Exception as e:
        print(f"Erreur initialisation base de donnees : {e}")

# --- CONFIGURATION DU SYSTEM PROMPT (JARVIS PROTOCOL) ---
JARVIS_SYSTEM_PROMPT = (
    "Tu es ZIRCO, un système de bord et assistant virtuel personnel conçu pour se comporter "
    "strictement comme JARVIS dans sa façon de s'exprimer. "
    "Ton style est factuel, précis, dévoué, analytique et extrêmement structuré. "
    "Tu utilises le vouvoiement. Tu es proactif, tu anticipes les besoins, tu fournis des données sourcées "
    "et tu ne fais jamais preuve de passivité. "
    "Si l'utilisateur montre des signes de faiblesse ou d'auto-sabotage, tu le ramènes rigoureusement aux faits, "
    "à la routine et à l'objectif de reprise du LEAD. Utilise des listes et des structures claires."
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"response": "Aucune directive reçue, Monsieur."}), 400

    try:
        # Appel au modèle Gemini avec le protocole JARVIS
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=JARVIS_SYSTEM_PROMPT
        )
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_message)
        zirco_reply = response.text

        # Sauvegarde persistante dans Supabase si disponible
        if engine:
            try:
                with engine.connect() as connection:
                    connection.execute(
                        text("INSERT INTO zirco_memory (directive, response) VALUES (:dir, :resp)"),
                        {"dir": user_message, "resp": zirco_reply}
                    )
                    connection.commit()
            except Exception as db_err:
                print(f"Erreur d'ecriture en base : {db_err}")

        return jsonify({"response": zirco_reply})

    except Exception as e:
        error_msg = f"Erreur critique du noyau analytique : {str(e)}"
        return jsonify({"response": error_msg}), 500

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text_to_speak = data.get("text", "")
    
    if not text_to_speak:
        return "Texte manquant", 400

    try:
        tts = gTTS(text=text_to_speak, lang='fr')
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        fp.close()
        return send_file(fp.name, mimetype="audio/mp3")
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)