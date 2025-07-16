import os
import json
import requests
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, abort
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Configuración de API ---
API_KEY = os.getenv("OPENAI_API_KEY")
API_URL_CHAT = "https://api.openai.com/v1/chat/completions"
API_URL_IMAGE = "https://api.openai.com/v1/images/generations"

# --- Almacenamiento de Resultados ---
# En una aplicación real, usarías una base de datos (SQLite, Redis, etc.).
# Para este ejemplo, un diccionario en memoria es suficiente.
resultados_store = {}

# --- Cuestionario ---
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

def generar_imagen_dalle(animal: str) -> str:
    if not API_KEY:
        return f"https://source.unsplash.com/512x512/?animal,{animal}"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "dall-e-3",
        "prompt": f"Un retrato artístico y amigable de un {animal}, estilo ilustración digital, con un fondo simple y colorido.",
        "n": 1, "size": "1024x1024", "quality": "standard"
    }
    try:
        response = requests.post(API_URL_IMAGE, headers=headers, json=data, timeout=45)
        response.raise_for_status()
        result = response.json()
        return result.get('data', [{}])[0].get('url', f"https://source.unsplash.com/512x512/?animal,{animal}")
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a DALL-E: {e}")
        return f"https://source.unsplash.com/512x512/?animal,{animal}"

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    """Renderiza la página principal del cuestionario."""
    return render_template("quiz.html", cuestionario=cuestionario)

@app.route('/resultado/<string:resultado_id>')
def ver_resultado(resultado_id):
    """Muestra una página de resultado permanente y compartible."""
    resultado = resultados_store.get(resultado_id)
    if not resultado:
        abort(404, description="Resultado no encontrado")
    return render_template('resultado.html', resultado=resultado)

@app.route('/sw.js')
def serve_sw():
    """Sirve el archivo del Service Worker."""
    return send_from_directory('.', 'sw.js')

@app.route('/analizar', methods=['POST'])
def analizar():
    """Analiza las respuestas, guarda el resultado y devuelve la URL para compartir."""
    if not API_KEY:
        return jsonify({"error": "La API key no está configurada."}), 500
    
    respuestas = request.json.get('respuestas', {})
    if not respuestas:
        return jsonify({"error": "No se recibieron respuestas."}), 400

    respuestas_formateadas = [f"{i+1}. {q['pregunta']} -> {q['opciones'].get(respuestas.get(f'q{i+1}'), '')}" for i, q in enumerate(cuestionario)]
    
    system_prompt = (
        "Eres un psicólogo de animales espirituales, divertido y creativo. Analiza las siguientes respuestas. "
        "Tu respuesta DEBE ser únicamente un objeto JSON válido con la estructura: "
        '{"animal": "Nombre", "descripcion": "Texto de 2-3 frases", "lema": "Lema divertido"}'
    )
    
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "\n".join(respuestas_formateadas)}
        ],
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(API_URL_CHAT, headers=headers, json=body, timeout=20)
        response.raise_for_status()
        result = response.json()['choices'][0]['message']['content']
        resultado_data = json.loads(result)

        # Generar imagen y guardarla en el resultado
        animal_nombre = resultado_data.get("animal", "desconocido")
        resultado_data['imagen'] = generar_imagen_dalle(animal_nombre)

        # Guardar el resultado y generar una URL única
        resultado_id = str(uuid.uuid4())
        resultados_store[resultado_id] = resultado_data
        
        # Añadir la URL para compartir a la respuesta
        resultado_data['share_url'] = url_for('ver_resultado', resultado_id=resultado_id, _external=True)

        return jsonify(resultado_data)

    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a la API: {e}")
        return jsonify({"error": "No se pudo comunicar con el analizador de almas."}), 503
    except Exception as e:
        print(f"Error inesperado en /analizar: {e}")
        return jsonify({"error": "Ocurrió un error misterioso en la selva digital."}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
