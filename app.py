import os
import json
import requests
from flask import Flask, render_template, request, jsonify

# Inicialización de la aplicación Flask
app = Flask(__name__)

# --- Configuración de la API (AHORA PARA OPENAI) ---
# La API Key se obtiene de una variable de entorno para seguridad.
API_KEY = os.environ.get('OPENAI_API_KEY')
API_URL = "https://api.openai.com/v1/chat/completions"

# --- Preguntas del Cuestionario ---
# (Esta sección no cambia)
cuestionario = [
    {
        "pregunta": "¿Cómo prefieres pasar tu tiempo libre?",
        "opciones": {
            "A": "En casa relajado y tranquilo.",
            "B": "Haciendo ejercicio o explorando al aire libre.",
            "C": "Con amigos o en reuniones sociales.",
            "D": "Probando algo nuevo o creativo."
        }
    },
    # ... (el resto de las preguntas siguen aquí igual que antes) ...
    {
        "pregunta": "¿Cuál de estas cualidades valoras más en ti mismo?",
        "opciones": {
            "A": "Inteligencia y reflexión.",
            "B": "Fuerza y determinación.",
            "C": "Lealtad y compromiso.",
            "D": "Creatividad y adaptabilidad."
        }
    }
]

def analizar_respuestas_con_ia(respuestas_texto):
    """
    Construye el prompt y llama a la API de OpenAI para obtener el análisis.
    """
    if not API_KEY:
        # Respuesta de fallback si la API Key no está configurada
        return {
            "animal": "Gato Doméstico",
            "descripcion": "Eres una persona tranquila y disfrutas de la comodidad de tu hogar. A veces misterioso, pero siempre sabes cómo conseguir lo que quieres, especialmente si se trata de una siesta al sol.",
            "lema": "La vida es simple: comer, dormir, y juzgar silenciosamente.",
            "imagen": "gato"
        }

    # 1. Construcción del prompt para OpenAI
    system_prompt = """
    Eres un experto en zoología y psicología. Tu tarea es analizar las respuestas de un cuestionario de personalidad y determinar qué animal representa mejor al usuario.
    Debes responder únicamente con un objeto JSON válido, sin texto adicional antes o después.
    El JSON debe tener la siguiente estructura:
    {
      "animal": "Nombre del Animal",
      "descripcion": "Una descripción de personalidad divertida, creativa y positiva en una sola frase.",
      "lema": "Un lema corto y pegadizo para ese animal.",
      "imagen": "nombre_del_animal_en_minusculas_y_sin_espacios_para_usar_en_una_url"
    }
    """
    user_prompt = f"Aquí están las respuestas del usuario:\n{respuestas_texto}"

    # 2. Estructura del payload para OpenAI
    payload = {
        "model": "gpt-3.5-turbo",  # Modelo económico y eficiente para esta tarea
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"}  # Asegura que la respuesta sea un JSON válido
    }

    # 3. Headers de autenticación para OpenAI
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=25)
        response.raise_for_status()

        # 4. Parseo de la respuesta de OpenAI
        response_data = response.json()
        json_string = response_data['choices'][0]['message']['content']
        
        return json.loads(json_string)

    except requests.exceptions.RequestException as e:
        print(f"Error llamando a la API de OpenAI: {e}")
        return {"error": "No se pudo contactar al servicio de análisis. Inténtalo de nuevo más tarde."}
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error procesando la respuesta de OpenAI: {e}")
        return {"error": "La respuesta del análisis no tuvo el formato esperado. ¡Qué animal tan rebelde!"}


@app.route('/')
def index():
    """
    Ruta principal que renderiza la página del cuestionario.
    """
    # Se pasa el cuestionario completo a la plantilla
    full_cuestionario = [
        {
            "pregunta": "¿Cómo prefieres pasar tu tiempo libre?",
            "opciones": {
                "A": "En casa relajado y tranquilo.",
                "B": "Haciendo ejercicio o explorando al aire libre.",
                "C": "Con amigos o en reuniones sociales.",
                "D": "Probando algo nuevo o creativo."
            }
        },
        {
            "pregunta": "¿Cómo reaccionas ante una situación de peligro?",
            "opciones": {
                "A": "Me escondo y pienso con calma antes de actuar.",
                "B": "Reacciono rápido y enfrento la situación.",
                "C": "Busco ayuda o protejo a quienes me rodean.",
                "D": "Me adapto rápidamente, aunque no sepa qué hacer."
            }
        },
        {
            "pregunta": "¿Qué ritmo de vida llevas?",
            "opciones": {
                "A": "Lento y relajado, disfruto cada momento.",
                "B": "Activo y lleno de energía.",
                "C": "Equilibrado, según el día y la situación.",
                "D": "Impredecible, cada día es diferente."
            }
        },
        {
            "pregunta": "¿Cómo te describirían tus amigos?",
            "opciones": {
                "A": "Tranquilo y observador.",
                "B": "Valiente y determinado.",
                "C": "Leal y protector.",
                "D": "Curioso y divertido."
            }
        },
        {
            "pregunta": "¿Prefieres estar solo o acompañado?",
            "opciones": {
                "A": "Prefiero estar solo, me siento cómodo así.",
                "B": "Me gusta estar con otros, pero también necesito mi espacio.",
                "C": "Me encanta estar en grupo, siempre rodeado de gente.",
                "D": "Depende, a veces solo y a veces con todos."
            }
        },
        {
            "pregunta": "¿Cuál de estas comidas te representa mejor?",
            "opciones": {
                "A": "Algo simple pero delicioso, como pan o frutas.",
                "B": "Carne o platillos intensos.",
                "C": "Comida casera, tradicional.",
                "D": "Algo exótico o fuera de lo común."
            }
        },
        {
            "pregunta": "¿Qué paisajes prefieres?",
            "opciones": {
                "A": "Bosques o montañas silenciosas.",
                "B": "Praderas o selvas llenas de vida.",
                "C": "Lugares cálidos y protegidos.",
                "D": "Playas, desiertos o lugares inusuales."
            }
        },
        {
            "pregunta": "¿Cuál de estas cualidades valoras más en ti mismo?",
            "opciones": {
                "A": "Inteligencia y reflexión.",
                "B": "Fuerza y determinación.",
                "C": "Lealtad y compromiso.",
                "D": "Creatividad y adaptabilidad."
            }
        }
    ]
    return render_template('index.html', cuestionario=full_cuestionario)

@app.route('/analizar', methods=['POST'])
def analizar():
    """
    Endpoint que recibe las respuestas, las procesa y devuelve el resultado de la IA.
    """
    respuestas = request.json.get('respuestas', {})
    
    # Formatear las respuestas para el prompt
    respuestas_formateadas = []
    # Usamos el mismo cuestionario definido globalmente para la lógica
    full_cuestionario_logic = [
        {
            "pregunta": "¿Cómo prefieres pasar tu tiempo libre?",
            "opciones": {
                "A": "En casa relajado y tranquilo.",
                "B": "Haciendo ejercicio o explorando al aire libre.",
                "C": "Con amigos o en reuniones sociales.",
                "D": "Probando algo nuevo o creativo."
            }
        },
        {
            "pregunta": "¿Cómo reaccionas ante una situación de peligro?",
            "opciones": {
                "A": "Me escondo y pienso con calma antes de actuar.",
                "B": "Reacciono rápido y enfrento la situación.",
                "C": "Busco ayuda o protejo a quienes me rodean.",
                "D": "Me adapto rápidamente, aunque no sepa qué hacer."
            }
        },
        {
            "pregunta": "¿Qué ritmo de vida llevas?",
            "opciones": {
                "A": "Lento y relajado, disfruto cada momento.",
                "B": "Activo y lleno de energía.",
                "C": "Equilibrado, según el día y la situación.",
                "D": "Impredecible, cada día es diferente."
            }
        },
        {
            "pregunta": "¿Cómo te describirían tus amigos?",
            "opciones": {
                "A": "Tranquilo y observador.",
                "B": "Valiente y determinado.",
                "C": "Leal y protector.",
                "D": "Curioso y divertido."
            }
        },
        {
            "pregunta": "¿Prefieres estar solo o acompañado?",
            "opciones": {
                "A": "Prefiero estar solo, me siento cómodo así.",
                "B": "Me gusta estar con otros, pero también necesito mi espacio.",
                "C": "Me encanta estar en grupo, siempre rodeado de gente.",
                "D": "Depende, a veces solo y a veces con todos."
            }
        },
        {
            "pregunta": "¿Cuál de estas comidas te representa mejor?",
            "opciones": {
                "A": "Algo simple pero delicioso, como pan o frutas.",
                "B": "Carne o platillos intensos.",
                "C": "Comida casera, tradicional.",
                "D": "Algo exótico o fuera de lo común."
            }
        },
        {
            "pregunta": "¿Qué paisajes prefieres?",
            "opciones": {
                "A": "Bosques o montañas silenciosas.",
                "B": "Praderas o selvas llenas de vida.",
                "C": "Lugares cálidos y protegidos.",
                "D": "Playas, desiertos o lugares inusuales."
            }
        },
        {
            "pregunta": "¿Cuál de estas cualidades valoras más en ti mismo?",
            "opciones": {
                "A": "Inteligencia y reflexión.",
                "B": "Fuerza y determinación.",
                "C": "Lealtad y compromiso.",
                "D": "Creatividad y adaptabilidad."
            }
        }
    ]
    for i, (pregunta_obj, opcion_letra) in enumerate(zip(full_cuestionario_logic, respuestas.values())):
        pregunta_texto = pregunta_obj['pregunta']
        respuesta_texto = pregunta_obj['opciones'].get(opcion_letra, "Sin respuesta")
        respuestas_formateadas.append(f"P{i+1}: {pregunta_texto} -> R: {respuesta_texto}")

    resultado_ia = analizar_respuestas_con_ia("\n".join(respuestas_formateadas))
    
    return jsonify(resultado_ia)

# --- Punto de Entrada ---
if __name__ == '__main__':
    # El modo debug se activa si se corre el script directamente
    app.run(debug=True)
