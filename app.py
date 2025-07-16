import os
import json
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
# Es una mejor práctica que usar os.getenv directamente para desarrollo.
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Configuración de API ---
API_KEY = os.getenv("OPENAI_API_KEY")
API_URL_CHAT = "https://api.openai.com/v1/chat/completions"
API_URL_IMAGE = "https://api.openai.com/v1/images/generations"

# --- Verificación de API Key ---
if not API_KEY:
    print("¡Advertencia! La variable de entorno OPENAI_API_KEY no está configurada.")
    # Podrías optar por salir de la aplicación si la API key es crucial
    # exit()

# --- Cuestionario ---
# (Sin cambios en la estructura de datos)
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
    """
    Genera una URL de imagen usando DALL-E 3 o devuelve una imagen de fallback en caso de error.
    """
    if not API_KEY:
        print("No se puede generar imagen: API_KEY no disponible.")
        return f"https://source.unsplash.com/512x512/?animal,{animal}"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # Prompt mejorado para obtener mejores imágenes
    data = {
        "model": "dall-e-3",
        "prompt": f"Un retrato artístico y amigable de un {animal}, estilo ilustración digital, con un fondo simple y colorido.",
        "n": 1,
        "size": "1024x1024", # Usamos 1024x1024 que es el tamaño estándar para DALL-E 3
        "quality": "standard"
    }
    try:
        response = requests.post(API_URL_IMAGE, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # Lanza un error para respuestas 4xx/5xx
        result = response.json()
        image_url = result.get('data', [{}])[0].get('url')
        if image_url:
            return image_url
        else:
            print("Error: La respuesta de DALL-E no contenía una URL de imagen.")
            return f"https://source.unsplash.com/512x512/?animal,{animal}"
            
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a DALL-E: {e}")
        return f"https://source.unsplash.com/512x512/?animal,{animal}"
    except Exception as e:
        print(f"Error inesperado al generar imagen: {e}")
        return f"https://source.unsplash.com/512x512/?animal,{animal}"

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    """Renderiza la página principal del cuestionario."""
    return render_template("quiz.html", cuestionario=cuestionario)

@app.route('/sw.js')
def serve_sw():
    """Sirve el archivo del Service Worker desde el directorio raíz."""
    return send_from_directory('.', 'sw.js')

@app.route('/analizar', methods=['POST'])
def analizar():
    """Analiza las respuestas del cuestionario y devuelve el animal correspondiente."""
    if not API_KEY:
        return jsonify({
            "animal": "Humano Desconectado", 
            "descripcion": "Parece que mi cerebro (la API de OpenAI) no está conectado. Por favor, configura la API key.", 
            "lema": "Sin conexión no hay inspiración.", 
            "imagen": "https://placehold.co/512x512/ff0000/ffffff?text=Error"
        }), 500

    respuestas = request.json.get('respuestas', {})
    if not respuestas or len(respuestas) != len(cuestionario):
        return jsonify({"error": "Se requieren todas las respuestas."}), 400

    # Formateo de respuestas para el prompt
    respuestas_formateadas = []
    for i, (pregunta_data, opcion_key) in enumerate(zip(cuestionario, respuestas.values())):
        texto_pregunta = pregunta_data['pregunta']
        texto_respuesta = pregunta_data['opciones'].get(opcion_key, "N/A")
        respuestas_formateadas.append(f"{i+1}. {texto_pregunta}\n   Respuesta: {texto_respuesta}")

    prompt_usuario = "\n".join(respuestas_formateadas)
    
    system_prompt = f"""
    Eres un psicólogo de animales espirituales, divertido y creativo. Analiza las siguientes respuestas de un test de personalidad.
    Basado en ellas, determina qué animal representa mejor a la persona.
    Tu respuesta DEBE ser únicamente un objeto JSON válido, sin texto adicional antes o después.
    La estructura del JSON debe ser la siguiente:
    {{
      "animal": "Nombre del Animal",
      "descripcion": "Una descripción de 2-3 frases sobre por qué la persona es ese animal, destacando su personalidad.",
      "lema": "Un lema o frase corta y divertida que represente al animal."
    }}
    """

    body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_usuario}
        ],
        "response_format": {"type": "json_object"} # Forza la salida en JSON
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Petición a la API de Chat
        response = requests.post(API_URL_CHAT, headers=headers, json=body, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        content_str = data.get('choices', [{}])[0].get('message', {}).get('content')
        
        if not content_str:
            raise ValueError("La respuesta de la API de chat estaba vacía.")

        # Cargar el JSON de la respuesta
        result = json.loads(content_str)

        # Generar imagen con DALL-E
        animal_nombre = result.get("animal", "desconocido")
        result['imagen'] = generar_imagen_dalle(animal_nombre)

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a la API de Chat: {e}")
        return jsonify({"error": "No se pudo comunicar con el analizador de almas salvajes."}), 503
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error al procesar la respuesta de la API: {e}")
        return jsonify({"error": "El analizador de almas salvajes dio una respuesta extraña."}), 500
    except Exception as e:
        print(f"Error inesperado en /analizar: {e}")
        return jsonify({"error": "Ocurrió un error misterioso en la selva digital."}), 500

if __name__ == '__main__':
    # El puerto 5001 es una alternativa común para evitar conflictos con otros servicios.
    app.run(host="0.0.0.0", port=5001, debug=True)