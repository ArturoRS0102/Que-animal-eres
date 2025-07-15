# ¿Qué Animal Eres? - Aplicación Web con IA

Esta es una aplicación web divertida construida con Flask y Python que permite a los usuarios responder un cuestionario de personalidad de 8 preguntas. Las respuestas se envían a una IA (OpenAI GPT-3.5) para generar un perfil de "espíritu animal" único y entretenido.

El proyecto está diseñado para ser simple, viral y monetizable a través de espacios publicitarios.

## Características

- **Backend en Flask:** Ligero, rápido y fácil de desplegar.
- **Análisis con IA:** Utiliza la API de OpenAI para un análisis de personalidad creativo.
- **Interfaz Responsive:** Diseño moderno y amigable con dispositivos móviles gracias a TailwindCSS.
- **Simulación de Monetización:** Incluye banners publicitarios simulados y un "video ad" obligatorio antes del resultado.
- **Viralidad:** Botones para compartir en Twitter, Facebook y para copiar el enlace.
- **Listo para Desplegar:** Configurado para un despliegue sencillo en plataformas como Render.com.

## Estructura del Proyecto


/que-animal-eres
├── templates/
│   └── index.html         # Interfaz de usuario
├── static/
│   └── script.js          # Lógica del frontend
├── app.py                 # Aplicación Flask (backend)
├── requirements.txt       # Dependencias de Python
├── Procfile               # Instrucciones para el servidor
└── README.md              # Esta guía


## Cómo Ejecutar Localmente

1.  **Clonar el Repositorio**
    ```bash
    git clone <URL-del-repositorio>
    cd que-animal-eres
    ```

2.  **Crear y Activar un Entorno Virtual**
    ```bash
    # Para Mac/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar Dependencias**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la API Key de OpenAI**
    Crea un archivo llamado `.env` en la raíz del proyecto y añade tu API Key. Para que Flask la detecte automáticamente al usar `flask run`, necesitas instalar `python-dotenv`.
    
    Primero instálalo: `pip install python-dotenv`
    
    Luego, crea el archivo `.env`:
    ```
    OPENAI_API_KEY='TU_API_KEY_DE_OPENAI_AQUI'
    ```

5.  **Ejecutar la Aplicación**
    ```bash
    flask run
    ```
    Abre tu navegador y ve a `http://127.0.0.1:5000`.

## Instrucciones de Despliegue en Render.com

1.  **Sube tu proyecto a GitHub:** Asegúrate de que todos los archivos (`app.py`, `requirements.txt`, `Procfile`, etc.) estén en tu repositorio.

2.  **Crea una cuenta en Render:** Si no tienes una, regístrate en [Render.com](https://render.com/).

3.  **Crea un Nuevo "Web Service":**
    - En tu dashboard de Render, haz clic en **"New +"** y selecciona **"Web Service"**.
    - Conecta tu cuenta de GitHub y selecciona el repositorio de tu proyecto.

4.  **Configura el Servicio Web:**
    - **Name:** Elige un nombre único para tu aplicación (ej: `que-animal-eres`).
    - **Region:** Elige una región cercana a tus usuarios.
    - **Branch:** `main` o la rama que desees desplegar.
    - **Root Directory:** Déjalo en blanco si `app.py` está en la raíz.
    - **Runtime:** `Python 3`.
    - **Build Command:** `pip install -r requirements.txt` (Render suele detectarlo automáticamente).
    - **Start Command:** `gunicorn app:app` (Render lo tomará del `Procfile`).
    - **Instance Type:** `Free` es suficiente para empezar.

5.  **Añade la Variable de Entorno:**
    - Ve a la sección **"Environment"**.
    - Haz clic en **"Add Environment Variable"**.
    - **Key:** `OPENAI_API_KEY`
    - **Value:** Pega tu clave de API de OpenAI aquí.

6.  **Despliega:**
    - Haz clic en **"Create Web Service"**.
    - Render comenzará a construir y desplegar tu aplicación. Una vez que el estado sea "Live", podrás acceder a ella desde la URL proporcionada.

¡Y listo! Tu aplicación estará en línea para que todo el mundo descubra su espíritu animal.
