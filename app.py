import os
import json
import requests
import uuid
import redis # Importamos la librería de Redis
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, abort, Response
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Configuración de API y Redis ---
API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL") # Obtiene la URL de conexión de Redis
API_URL_CHAT = "https://api.openai.com/v1/chat/completions"
API_URL_IMAGE = "https://api.openai.com/v1/images/generations"

# --- Conexión a Redis ---
# Si no hay URL de Redis, la app no funcionará correctamente en producción.
if not REDIS_URL:
    print("ADVERTENCIA: La variable de entorno REDIS_URL no está configurada. La app no será persistente.")
    # Para pruebas locales, puedes simularlo, pero en Render es necesario.
    db = None 
else:
    # Conectamos a la base de datos de Redis
    db = redis.from_url(REDIS_URL)


# --- Cuestionario (sin cambios) ---
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

def generar_y_obtener_imagen_bytes(animal: str) -> bytes | None:
    if not API_KEY:
        return None
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "dall-e-3",
        "prompt": f"Un retrato artístico y amigable de un {animal}, estilo ilustración digital, con un fondo simple y colorido.",
        "n": 1, "size": "1024x1024", "quality": "standard"
    }
    try:
        response_dalle = requests.post(API_URL_IMAGE, headers=headers, json=data, timeout=45)
        response_dalle.raise_for_status()
        dalle_url = response_dalle.json()['data'][0]['url']
        response_image = requests.get(dalle_url, timeout=30)
        response_image.raise_for_status()
        return response_image.content
    except Exception as e:
        print(f"Error crítico al generar o descargar la imagen: {e}")
        return None

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    return render_template("quiz.html", cuestionario=cuestionario)

@app.route('/resultado/<string:resultado_id>')
def ver_resultado(resultado_id):
    if not db: abort(503, "Base de datos no disponible.")
    
    # Obtenemos los datos desde Redis
    resultado_json = db.get(f"resultado:{resultado_id}:json")
    if not resultado_json:
        abort(404)
    
    resultado = json.loads(resultado_json)
    return render_template('resultado.html', resultado=resultado)

@app.route('/image/<string:resultado_id>.png')
def serve_generated_image(resultado_id):
    if not db: abort(503, "Base de datos no disponible.")

    # Obtenemos los bytes de la imagen desde Redis
    image_content = db.get(f"resultado:{resultado_id}:image")
    if not image_content:
        abort(404)
    
    return Response(image_content, mimetype='image/png')

@app.route('/robots.txt')
def serve_robots():
    content = "User-agent: *\nAllow: /\n\nUser-agent: facebookexternalhit\nAllow: /"
    return Response(content, mimetype='text/plain')

@app.route('/analizar', methods=['POST'])
def analizar():
    if not API_KEY or not db:
        return jsonify({"error": "El servicio no está disponible actualmente."}), 503
    
    respuestas = request.json.get('respuestas', {})
    if not respuestas:
        return jsonify({"error": "No se recibieron respuestas."}), 400

    respuestas_formateadas = [f"{i+1}. {q['pregunta']} -> {q['opciones'].get(respuestas.get(f'q{i+1}'), '')}" for i, q in enumerate(cuestionario)]
    
    system_prompt = (
        'Eres un psicólogo de animales espirituales, divertido y creativo. Analiza las respuestas. '
        'Tu respuesta DEBE ser únicamente un objeto JSON válido con la estructura: '
        '{"animal": "Nombre", "descripcion": "Texto de 2-3 frases", "lema": "Lema divertido"}'
    )
    
    body = {"model": "gpt-3.5-turbo", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": "\n".join(respuestas_formateadas)}], "response_format": {"type": "json_object"}}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(API_URL_CHAT, headers=headers, json=body, timeout=20)
        response.raise_for_status()
        result = response.json()['choices'][0]['message']['content']
        resultado_data = json.loads(result)

        resultado_id = str(uuid.uuid4())
        
        animal_nombre = resultado_data.get("animal", "desconocido")
        image_bytes = generar_y_obtener_imagen_bytes(animal_nombre)
        
        if not image_bytes:
            raise ValueError("No se pudo generar el contenido de la imagen.")

        # Creamos las URLs que usaremos en las plantillas y para compartir
        resultado_data['imagen'] = url_for('serve_generated_image', resultado_id=resultado_id, _external=True)
        resultado_data['share_url'] = url_for('ver_resultado', resultado_id=resultado_id, _external=True)
        
        # Guardamos los datos en Redis con una expiración de 24 horas
        db.set(f"resultado:{resultado_id}:json", json.dumps(resultado_data), ex=86400)
        db.set(f"resultado:{resultado_id}:image", image_bytes, ex=86400)

        return jsonify(resultado_data)

    except Exception as e:
        print(f"Error inesperado en /analizar: {e}")
        return jsonify({"error": "Ocurrió un error misterioso en la selva digital."}), 500

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404 - Página no encontrada</h1>", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

