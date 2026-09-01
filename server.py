import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
from gtts import gTTS
from sqlalchemy import create_engine, text

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None

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

JARVIS_SYSTEM_PROMPT = (
    "Tu es ZIRCO, un système de bord et assistant virtuel personnel conçu pour se comporter "
    "strictement comme JARVIS. Ton style est factuel, précis, dévoué, analytique et extrêmement structuré. "
    "Tu utilises le vouvoiement. Tu es proactif, tu anticipes les besoins et tu fournis des données sourcées. "
    "Utilise des listes à puces et des blocs structurés pour une lisibilité instantanée."
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
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=JARVIS_SYSTEM_PROMPT
        )
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_message)
        zirco_reply = response.text

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
        return jsonify({"response": f"Erreur critique du noyau : {str(e)}"}), 500

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text_to_speak = data.get("text", "")
    if not text_to_speak:
        return "Texte manquant", 400

    try:
        # Utilisation d'un texte court ou synthèse optimisée pour la vitesse
        tts = gTTS(text=text_to_speak, lang='fr', slow=False)
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        fp.close()
        return send_file(fp.name, mimetype="audio/mp3")
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)