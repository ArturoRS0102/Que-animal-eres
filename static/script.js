document.addEventListener('DOMContentLoaded', () => {
    const quizForm = document.getElementById('quiz-form');
    const quizSection = document.getElementById('quiz-section');
    const loadingSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('result-section');
    const adTimerEl = document.getElementById('ad-timer');

    // --- NUEVO CÓDIGO PARA MANEJAR EL ESTILO DE SELECCIÓN ---
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', () => {
            // Primero, quita el estilo de todas las opciones de la misma pregunta
            const groupName = radio.name;
            const optionsInGroup = document.querySelectorAll(`input[name="${groupName}"]`);
            optionsInGroup.forEach(option => {
                option.parentElement.classList.remove('opcion-seleccionada');
            });

            // Luego, añade el estilo solo a la opción seleccionada
            if (radio.checked) {
                radio.parentElement.classList.add('opcion-seleccionada');
            }
        });
    });
    // --- FIN DEL NUEVO CÓDIGO ---

    quizForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Recoger las respuestas
        const formData = new FormData(quizForm);
        const respuestas = {};
        let questionCount = 0;
        for (let [key, value] of formData.entries()) {
            respuestas[key] = value;
            questionCount++;
        }

        // Validar que todas las preguntas fueron respondidas
        const totalQuestions = document.querySelectorAll('.question-block').length;
        if (questionCount < totalQuestions) {
            alert('Por favor, responde todas las preguntas.');
            return;
        }

        // 2. Ocultar cuestionario y mostrar carga/anuncio
        quizSection.classList.add('opacity-0');
        setTimeout(() => {
            quizSection.classList.add('hidden');
            loadingSection.classList.remove('hidden');
        }, 500);

        // 3. Simular anuncio con temporizador
        let timeLeft = 7; 
        adTimerEl.textContent = timeLeft;
        const adInterval = setInterval(() => {
            timeLeft--;
            adTimerEl.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(adInterval);
            }
        }, 1000);

        // 4. Enviar respuestas al backend
        try {
            const response = await fetch('/analizar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ respuestas }),
            });

            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.statusText}`);
            }

            const result = await response.json();
            
            // Esperar a que termine el temporizador del anuncio
            setTimeout(() => {
                displayResult(result);
            }, Math.max(0, timeLeft * 1000));

        } catch (error) {
            console.error('Error al analizar:', error);
            const errorResult = {
                animal: "Error",
                descripcion: "Hubo un problema al contactar a nuestros expertos animales. Por favor, intenta de nuevo más tarde.",
                lema: "A veces la selva digital tiene mala señal.",
                imagen: "error"
            };
            setTimeout(() => {
                displayResult(errorResult);
            }, Math.max(0, timeLeft * 1000));
        }
    });

    function displayResult(result) {
        loadingSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        resultSection.classList.add('opacity-100');

        if (result.error) {
            document.getElementById('animal-name').textContent = "Oops";
            document.getElementById('animal-description').textContent = result.error;
            document.getElementById('animal-motto').textContent = "";
            document.getElementById('animal-image').src = `https://placehold.co/300x300/f87171/ffffff?text=Error`;
            return;
        }

        document.getElementById('animal-name').textContent = result.animal;
        document.getElementById('animal-description').textContent = result.descripcion;
        document.getElementById('animal-motto').textContent = `"${result.lema}"`;
        
        document.getElementById('animal-image').src = `https://placehold.co/400x400/f9a825/ffffff?text=${encodeURIComponent(result.animal)}`;
        document.getElementById('animal-image').alt = `Imagen de un ${result.animal}`;

        const shareText = `¡Descubrí que mi espíritu animal es un ${result.animal}! "${result.lema}" Descubre el tuyo aquí:`;
        const shareUrl = window.location.href;

        const twitterIntent = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
        document.getElementById('share-twitter').href = twitterIntent;

        const facebookIntent = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`;
        document.getElementById('share-facebook').href = facebookIntent;

        const copyButton = document.getElementById('copy-link');
        const copyFeedback = document.getElementById('copy-feedback');
        copyButton.addEventListener('click', () => {
            const textToCopy = `${shareText} ${shareUrl}`;
            navigator.clipboard.writeText(textToCopy).then(() => {
                copyFeedback.textContent = '¡Enlace copiado!';
                setTimeout(() => {
                    copyFeedback.textContent = '';
                }, 2000);
            }).catch(err => {
                console.error('Error al copiar el enlace: ', err);
                copyFeedback.textContent = 'Error al copiar';
            });
        });
    }
});