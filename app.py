import os
import json
import requests
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, abort
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# --- CREAR CARPETAS NECESARIAS ---
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
IMAGE_DIR = os.path.join(STATIC_FOLDER, 'generated_images')
os.makedirs(IMAGE_DIR, exist_ok=True)

# --- Configuración de API ---
API_KEY = os.getenv("OPENAI_API_KEY")
API_URL_CHAT = "https://api.openai.com/v1/chat/completions"
API_URL_IMAGE = "https://api.openai.com/v1/images/generations"

# --- Almacenamiento de Resultados (En memoria) ---
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

@app.route('/')
def index():
    return render_template("quiz.html", cuestionario=cuestionario)

@app.route('/resultado/<string:resultado_id>')
def ver_resultado(resultado_id):
    resultado = resultados_store.get(resultado_id)
    if not resultado:
        abort(404)
    return render_template('resultado.html', resultado=resultado)

@app.route('/analizar', methods=['POST'])
def analizar():
    print("📩 Solicitud recibida en /analizar")
    data = request.get_json(silent=True)
    respuestas = data.get('respuestas', {}) if data else {}
    if not respuestas:
        return jsonify({"error": "No se recibieron respuestas."}), 400
    # ... resto de tu lógica como ya la tienes
