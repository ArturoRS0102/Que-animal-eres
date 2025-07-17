import os
import json
import requests
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, abort
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
IMAGE_DIR = os.path.join(STATIC_FOLDER, 'generated_images')
os.makedirs(IMAGE_DIR, exist_ok=True)

API_KEY = os.getenv("OPENAI_API_KEY")
API_URL_CHAT = "https://api.openai.com/v1/chat/completions"
API_URL_IMAGE = "https://api.openai.com/v1/images/generations"
resultados_store = {}

cuestionario = [ ... ]  # Usa tu lista actual (ya la tienes bien definida)

# Función: Genera imagen DALL·E
def generar_y_guardar_imagen(animal, resultado_id):
    fallback = url_for('static', filename='placeholder.png', _external=True)
    if not API_KEY:
        return fallback
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "dall-e-3",
        "prompt": f"Un retrato artístico y amigable de un {animal}, estilo ilustración digital, fondo simple.",
        "n": 1, "size": "1024x1024", "quality": "standard"
    }
    try:
        res = requests.post(API_URL_IMAGE, headers=headers, json=data, timeout=45)
        img_url = res.json()['data'][0]['url']
        img_data = requests.get(img_url).content
        local_file = os.path.join(IMAGE_DIR, f"{resultado_id}.png")
        with open(local_file, 'wb') as f:
            f.write(img_data)
        return url_for('static', filename=f"generated_images/{resultado_id}.png", _external=True)
    except:
        return fallback

# Función: Genera imagen compuesta con texto
def generar_imagen_compuesta(resultado, resultado_id):
    try:
        res = requests.get(resultado['imagen'], timeout=30)
        animal_img = Image.open(BytesIO(res.content)).convert("RGBA")
        background = Image.new("RGBA", (1024, 1280), (255, 255, 255, 255))
        animal_img = animal_img.resize((800, 800))
        background.paste(animal_img, (112, 20))

        draw = ImageDraw.Draw(background)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(font_path):
            font_path = "arial.ttf"
        font_title = ImageFont.truetype(font_path, 50)
        font_body = ImageFont.truetype(font_path, 36)

        y = 850
        draw.text((512, y), resultado['animal'], font=font_title, fill="black", anchor="mm")
        y += 70
        draw.text((512, y), resultado['lema'], font=font_body, fill="black", anchor="mm")
        y += 100
        draw.multiline_text((512, y), resultado['descripcion'], font=font_body, fill="black", anchor="mm", spacing=6, align="center")

        final_path = os.path.join(IMAGE_DIR, f"compuesto_{resultado_id}.png")
        background.save(final_path)
        return url_for('static', filename=f"generated_images/compuesto_{resultado_id}.png", _external=True)
    except Exception as e:
        print("Error al generar imagen compuesta:", e)
        return url_for('static', filename='placeholder.png', _external=True)

@app.route('/')
def index():
    return render_template("quiz.html", cuestionario=cuestionario)

@app.route('/resultado/<string:resultado_id>')
def ver_resultado(resultado_id):
    resultado = resultados_store.get(resultado_id)
    if not resultado:
        abort(404)
    return render_template("resultado.html", resultado=resultado)

@app.route('/analizar', methods=['POST'])
def analizar():
    print("📩 Solicitud recibida en /analizar")
    data = request.get_json(silent=True)
    respuestas = data.get('respuestas', {}) if data else {}
    if not respuestas:
        return jsonify({"error": "No se recibieron respuestas."}), 400

    respuestas_formateadas = [
        f"{i+1}. {q['pregunta']} -> {q['opciones'].get(respuestas.get(f'q{i+1}'), '')}"
        for i, q in enumerate(cuestionario)
    ]

    system_prompt = (
        'Eres un psicólogo de animales espirituales, divertido y creativo. Analiza las respuestas. '
        'Tu respuesta DEBE ser un objeto JSON con esta estructura: '
        '{"animal": "Nombre", "descripcion": "Texto", "lema": "Frase"}'
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
        res = requests.post(API_URL_CHAT, headers=headers, json=body, timeout=20)
        json_result = json.loads(res.json()['choices'][0]['message']['content'])
        resultado_id = str(uuid.uuid4())
        json_result["imagen"] = generar_y_guardar_imagen(json_result["animal"], resultado_id)
        json_result["imagen"] = generar_imagen_compuesta(json_result, resultado_id)
        json_result["share_url"] = url_for("ver_resultado", resultado_id=resultado_id, _external=True)
        resultados_store[resultado_id] = json_result
        return jsonify(json_result)
    except Exception as e:
        print("❌ Error en /analizar:", e)
        return jsonify({"error": "Error al analizar tus respuestas."}), 500

# --- Opcional: evitar errores 404 en logs ---
@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow:", 200, {'Content-Type': 'text/plain'}

@app.route('/sw.js')
def sw():
    return '', 200, {'Content-Type': 'application/javascript'}

if __name__ == '__main__':
    app.run(debug=True)
    
