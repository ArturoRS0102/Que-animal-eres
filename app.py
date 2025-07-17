import os
import json
import requests
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, abort
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# --- CREAR CARPETAS NECESARIAS ---
# Aseguramos que la carpeta para guardar las imágenes exista.
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
IMAGE_DIR = os.path.join(STATIC_FOLDER, 'generated_images')
os.makedirs(IMAGE_DIR, exist_ok=True)


# --- Configuración de API ---
API_KEY = os.getenv("OPENAI_API_KEY")
API_URL_CHAT = "https://api.openai.com/v1/chat/completions"
API_URL_IMAGE = "https://api.openai.com/v1/images/generations"

# --- Almacenamiento de Resultados ---
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

def generar_y_guardar_imagen(animal: str, resultado_id: str) -> str:
    """
    Genera una imagen con DALL-E, la descarga y guarda localmente,
    y devuelve la URL pública del archivo guardado.
    """
    # Imagen de respaldo por si todo falla
    fallback_image = url_for('static', filename='placeholder.png', _external=True)
    
    if not API_KEY:
        print("ADVERTENCIA: No hay API Key. Usando imagen de fallback.")
        return fallback_image

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "dall-e-3",
        "prompt": f"Un retrato artístico y amigable de un {animal}, estilo ilustración digital, con un fondo simple y colorido.",
        "n": 1, "size": "1024x1024", "quality": "standard"
    }
    
    try:
        # 1. Generar la URL de la imagen con DALL-E
        print("Paso 1: Solicitando URL a DALL-E...")
        response_dalle = requests.post(API_URL_IMAGE, headers=headers, json=data, timeout=45)
        response_dalle.raise_for_status()
        dalle_url = response_dalle.json().get('data', [{}])[0].get('url')
        if not dalle_url:
            raise ValueError("La respuesta de DALL-E no contenía una URL.")
        print(f"Paso 1 Exitoso. URL de DALL-E obtenida.")

        # 2. Descargar la imagen desde la URL de DALL-E
        print("Paso 2: Descargando contenido de la imagen...")
        response_image = requests.get(dalle_url, timeout=30)
        response_image.raise_for_status()
        
        image_content = response_image.content
        if not image_content:
            raise ValueError("El contenido de la imagen descargada está vacío.")
        print(f"Paso 2 Exitoso. Tamaño de la imagen descargada: {len(image_content)} bytes.")

        # 3. Guardar la imagen en nuestro servidor
        local_filename = f"{resultado_id}.png"
        local_filepath = os.path.join(IMAGE_DIR, local_filename)
        print(f"Paso 3: Guardando imagen en: {local_filepath}")
        with open(local_filepath, 'wb') as f:
            f.write(image_content)
        
        # Verificación de que el archivo se escribió y no está vacío
        if not os.path.exists(local_filepath) or os.path.getsize(local_filepath) == 0:
            raise IOError("El archivo no se guardó correctamente en el servidor o está vacío.")
        print("Paso 3 Exitoso. Archivo guardado.")

        # 4. Devolver la URL pública de nuestra imagen local
        final_url = url_for('static', filename=f'generated_images/{local_filename}', _external=True)
        print(f"Paso 4: URL final generada: {final_url}")
        return final_url

    except requests.exceptions.Timeout:
        print("Error crítico: Timeout durante la comunicación con la API de OpenAI.")
        return fallback_image
    except requests.exceptions.RequestException as e:
        print(f"Error crítico de red al contactar OpenAI: {e}")
        return fallback_image
    except (ValueError, IOError, Exception) as e:
        print(f"Error crítico al generar o guardar la imagen: {e}")
        return fallback_image

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    return render_template("quiz.html", cuestionario=cuestionario)

@app.route('/resultado/<string:resultado_id>')
def ver_resultado(resultado_id):
    resultado = resultados_store.get(resultado_id)
    if not resultado:
        abort(404)
    return render_template('resultado.html', resultado=resultado)

# Rutas para archivos en la raíz
@app.route('/sw.js')
def serve_sw():
    return send_from_directory('.', 'sw.js')

@app.route('/robots.txt')
def serve_robots():
    return send_from_directory('.', 'robots.txt')

@app.route('/analizar', methods=['POST'])
def analizar():
    if not API_KEY:
        return jsonify({"error": "La API key no está configurada."}), 500
    
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
        
        # Generar, guardar y obtener la URL local de la imagen
        animal_nombre = resultado_data.get("animal", "desconocido")
        local_image_url = generar_y_guardar_imagen(animal_nombre, resultado_id)
        resultado_data['imagen'] = local_image_url
        
        resultado_data['share_url'] = url_for('ver_resultado', resultado_id=resultado_id, _external=True)
        resultados_store[resultado_id] = resultado_data

        return jsonify(resultado_data)

    except Exception as e:
        print(f"Error inesperado en /analizar: {e}")
        return jsonify({"error": "Ocurrió un error misterioso en la selva digital."}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
