# ¿Qué Animal Eres? - Aplicación Web con IA

# ¿Qué Animal Eres? 🐾

Una divertida app web que utiliza IA para identificar tu "animal interior" a partir de un breve test de personalidad.

## 🚀 Tecnologías utilizadas
- Python 3.x + Flask
- HTML + TailwindCSS + JavaScript
- OpenAI GPT-3.5 para análisis de personalidad
- Render.com para despliegue

## 📦 Instalación local
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=tu_clave_api_aqui
python app.py
```

## 🌐 Despliegue en Render
1. Crea una cuenta en [Render](https://render.com/)
2. Crea un nuevo Web Service y conecta este repositorio
3. Establece la variable de entorno `OPENAI_API_KEY`
4. Render detectará automáticamente:
   - `requirements.txt`
   - `Procfile`

## 🧠 ¿Cómo funciona?
1. El usuario responde 8 preguntas
2. Se simula un anuncio (temporizador de 7 segundos)
3. Las respuestas se analizan con la API de OpenAI
4. Se genera una respuesta creativa con:
   - Nombre del animal
   - Descripción divertida
   - Imagen placeholder
   - Lema personalizado

## 📣 Comparte tu animal
Al final del test puedes copiar y compartir tu resultado en redes sociales con un solo clic.

---

¡Diviértete descubriendo qué animal eres! 🦊🦉🐘