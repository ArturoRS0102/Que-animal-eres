import os
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN ---
API_KEY = os.environ.get('OPENAI_API_KEY')
API_URL = "https://api.openai.com/v1/chat/completions"

# --- CUESTIONARIO (Definido una sola vez) ---
cuestionario = [
    {"pregunta": "¿Cómo prefieres pasar tu tiempo libre?", "opciones": {"A": "En casa relajado y tranquilo.", "B": "Haciendo ejercicio o explorando al aire libre.", "C": "Con amigos o en reuniones sociales.", "D": "Probando algo nuevo o creativo."}},
    {"pregunta": "¿Cómo reaccionas ante una situación de peligro?", "opciones": {"A": "Me escondo y pienso con calma antes de actuar.", "B": "Reacciono rápido y enfrento la situación.", "C": "Busco ayuda o protejo a quienes me rodean.", "D": "Me adapto rápidamente, aunque no sepa qué hacer."}},
    {"pregunta": "¿Qué ritmo de vida llevas?", "opciones": {"A": "Lento y relajado, disfruto cada momento.", "B": "Activo y lleno de energía.", "C": "Equilibrado, según el día y la situación.", "D": "Impredecible, cada día es diferente."}},
    {"pregunta": "¿Cómo te describirían tus amigos?", "opciones": {"A": "Tranquilo y observador.", "B": "Valiente y determinado.", "C": "Leal y protector.", "D": "Curioso y divertido."}},
    {"pregunta": "¿Prefieres estar solo o acompañado?", "opciones": {"A": "Prefiero estar solo, me siento cómodo así.", "B": "Me gusta estar con otros, pero también necesito mi espacio.", "C": "Me encanta estar en grupo, siempre rodeado de gente.", "D": "Depende, a veces solo y a veces con todos."}},
    {"pregunta": "¿Cuál de estas comidas te representa mejor?", "opciones": {"A": "Algo simple pero delicioso, como pan o frutas.", "B": "Carne o platillos intensos.", "C": "Comida casera, tradicional.", "D": "Algo exótico o fuera de lo común."}},
    {"pregunta": "¿Qué paisajes prefieres?", "opciones": {"A": "Bosques o montañas silenciosas.", "B": "Praderas o selvas llenas de vida.", "C": "Lugares cálidos y protegidos.", "D": "Playas, desiertos o lugares inusuales."}},
    {"pregunta": "¿Cuál de estas cualidades valoras más en ti mismo?", "opciones": {"A": "Inteligencia y reflexión.", "B": "Fuerza y determinación.", "C": "Lealtad y compromiso.", "D": "Creatividad y adaptabilidad."}}
]

def analizar_respuestas_con_ia(respuestas_texto):
    if not API_KEY:
        return {"animal": "Gato Doméstico", "descripcion": "Disfrutas de la comodidad de tu hogar. A veces misterioso, pero siempre sabes cómo conseguir lo que quieres.", "lema": "La vida es simple: comer, dormir, y juzgar silenciosamente.", "imagen": "gato"}

    system_prompt = "Eres un experto en zoología y psicología. Analiza las respuestas de un cuestionario y determina el espíritu animal del usuario. Responde únicamente con un objeto JSON válido con las claves 'animal', 'descripcion', 'lema', e 'imagen'."
    user_prompt = f"Respuestas del usuario:\n{respuestas_texto}"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {API_KEY}'}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        # Parseo robusto del contenido
        content = response_data['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"Error en la API o procesando la respuesta: {e}")
        return {"error": "No se pudo contactar al servicio de análisis. Inténtalo de nuevo más tarde."}

@app.route('/')
def index():
    return render_template('quiz.html', cuestionario=cuestionario)

@app.route('/analizar', methods=['POST'])
def analizar():
    respuestas = request.json.get('respuestas', {})
    respuestas_formateadas = []
    for i, (pregunta_obj, opcion_letra) in enumerate(zip(cuestionario, respuestas.values())):
        pregunta_texto = pregunta_obj['pregunta']
        respuesta_texto = pregunta_obj['opciones'].get(opcion_letra, "Sin respuesta")
        respuestas_formateadas.append(f"P{i+1}: {pregunta_texto} -> R: {respuesta_texto}")

    resultado_ia = analizar_respuestas_con_ia("\n".join(respuestas_formateadas))
    return jsonify(resultado_ia)

if __name__ == '__main__':
    app.run(debug=True)