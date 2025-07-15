# Estructura de proyecto Flask: "Que Animal Eres"

import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory

app = Flask(__name__)

API_KEY = os.getenv("OPENAI_API_KEY")
API_URL_CHAT = "https://api.openai.com/v1/chat/completions"
API_URL_IMAGE = "https://api.openai.com/v1/images/generations"

# Cuestionario
cuestionario = [
    {"pregunta": "¿Cómo prefieres pasar tu tiempo libre?",
     "opciones": {"A": "En casa relajado y tranquilo.", "B": "Haciendo ejercicio o explorando al aire libre.", "C": "Con amigos o en reuniones sociales.", "D": "Probando algo nuevo o creativo."}},
    {"pregunta": "¿Cómo reaccionas ante una situación de peligro?",
     "opciones": {"A": "Me escondo y pienso con calma antes de actuar.", "B": "Reacciono rápido y enfrento la situación.", "C": "Busco ayuda o protejo a quienes me rodean.", "D": "Me adapto rápidamente, aunque no sepa qué hacer."}},
    {"pregunta": "¿Qué ritmo de vida llevas?",
     "opciones": {"A": "Lento y relajado, disfruto cada momento.", "B": "Activo y lleno de energía.", "C": "Equilibrado, según el día y la situación.", "D": "Impredecible, cada día es diferente."}},
    {"pregunta": "¿Cómo te describirían tus amigos?",
     "opciones": {"A": "Tranquilo y observador.", "B": "Valiente y determinado.", "C": "Leal y protector.", "D": "Curioso y divertido."}},
    {"pregunta": "¿Prefieres estar solo o acompañado?",
     "opciones": {"A": "Prefiero estar solo, me siento cómodo así.", "B": "Me gusta estar con otros, pero también necesito mi espacio.", "C": "Me encanta estar en grupo, siempre rodeado de gente.", "D": "Depende, a veces solo y a veces con todos."}},
    {"pregunta": "¿Cuál de estas comidas te representa mejor?",
     "opciones": {"A": "Algo simple pero delicioso, como pan o frutas.", "B": "Carne o platillos intensos.", "C": "Comida casera, tradicional.", "D": "Algo exótico o fuera de lo común."}},
    {"pregunta": "¿Qué paisajes prefieres?",
     "opciones": {"A": "Bosques o montañas silenciosas.", "B": "Praderas o selvas llenas de vida.", "C": "Lugares cálidos y protegidos.", "D": "Playas, desiertos o lugares inusuales."}},
    {"pregunta": "¿Cuál de estas cualidades valoras más en ti mismo?",
     "opciones": {"A": "Inteligencia y reflexión.", "B": "Fuerza y determinación.", "C": "Lealtad y compromiso.", "D": "Creatividad y adaptabilidad."}}
]

def generar_imagen_dalle(animal):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "dall-e-3",
        "prompt": f"Un retrato realista y bonito de un {animal} en estilo digital, fondo blanco",
        "n": 1,
        "size": "512x512"
    }
    try:
        response = requests.post(API_URL_IMAGE, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['data'][0]['url']
    except Exception as e:
        print("Error generando imagen:", e)
        return f"https://source.unsplash.com/300x300/?animal,{animal}"

@app.route('/')
def index():
    return render_template("quiz.html", cuestionario=cuestionario)

@app.route('/<path:filename>')
def serve_static_file(filename):
    return send_from_directory('.', filename)

@app.route('/analizar', methods=['POST'])
def analizar():
    respuestas = request.json.get('respuestas', {})
    respuestas_formateadas = []
    for i, (pregunta, opcion) in enumerate(zip(cuestionario, respuestas.values())):
        texto = pregunta['pregunta']
        valor = pregunta['opciones'].get(opcion, "")
        respuestas_formateadas.append(f"{i+1}. {texto} -> {valor}")

    prompt = f"""
    Eres un experto en personalidad animal. Basado en estas respuestas, indica con humor y creatividad qué animal representa a la persona. Responde solo un JSON con esta estructura:
    {{"animal": "nombre", "descripcion": "texto", "lema": "frase", "imagen": "animal"}}
    Respuestas:
    {chr(10).join(respuestas_formateadas)}
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Responde solo con JSON"},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        r = requests.post(API_URL_CHAT, headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
        content = data['choices'][0]['message']['content']
        result = json.loads(content)

        # Generar imagen real con DALL·E
        result['imagen'] = generar_imagen_dalle(result['animal'])

        return jsonify(result)
    except Exception as e:
        print("Error al analizar o generar imagen:", e)
        return jsonify({"animal": "Error", "descripcion": "Hubo un error analizando tus respuestas.", "lema": "La IA se fue a dormir.", "imagen": "error"})

if __name__ == '__main__':
    app.run(debug=True)
