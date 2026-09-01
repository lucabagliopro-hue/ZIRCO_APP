import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from gtts import gTTS
from kernel.contracts import FactClaim
from providers.memory.kernel import MemoryKernel

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
memory_kernel = MemoryKernel()

SYSTEM_INSTRUCTION = (
    "Tu es ZIRCO, l'assistant virtuel personnel de Monsieur (façon JARVIS/Wakanda). "
    "Ton style est extrêmement concis, percutant, analytique et direct. "
    "INTERDICTION ABSOLUE de raconter la vie de l'utilisateur, de citer son année de naissance, ses enfants, sa femme ou son historique personnel. "
    "Tu vas droit au but, tu aides dans les choix techniques ou tactiques, et tu réponds en quelques lignes maximum, sans romans. "
    "Appelle-le TOUJOURS 'Monsieur'."
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "ZIRCO Noyau Cognitif",
        "short_name": "ZIRCO",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0b0f19",
        "theme_color": "#111827",
        "icons": [
            {
                "src": "/static/logo_zirco.png",
                "sizes": "192x192",
                "type": "image/png"
            }
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': "Aucune directive reçue, Monsieur.", 'audio_url': ''})
    
    try:
        model = genai.GenerativeModel(
            model_name='gemini-3.5-flash-lite',
            system_instruction=SYSTEM_INSTRUCTION
        )
        response = model.generate_content(user_message)
        bot_response = response.text
        
        memory_kernel.ingest_fact(FactClaim(
            predicate="user_directive",
            category="preferences",
            content=user_message,
            confidence=0.9,
            source_session="web_ui"
        ))
    except Exception as e:
        bot_response = f"Erreur critique du noyau : {str(e)}"
        
    audio_path = "static/response.mp3"
    tts = gTTS(text=bot_response, lang='fr', slow=False)
    tts.save(audio_path)
        
    return jsonify({'response': bot_response, 'audio_url': '/static/response.mp3?t=' + os.urandom(4).hex()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)