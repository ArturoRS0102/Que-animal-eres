document.addEventListener('DOMContentLoaded', () => {
    const quizForm = document.getElementById('quiz-form');
    const quizSection = document.getElementById('quiz-section');
    const loadingSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('result-section');
    const adTimerEl = document.getElementById('ad-timer');
    const copyButton = document.getElementById('copy-link');
    const copyFeedback = document.getElementById('copy-feedback');

    // --- CÓDIGO PARA MANEJAR EL ESTILO DE SELECCIÓN ---
    // Esto ya estaba correcto y se mantiene.
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', () => {
            const groupName = radio.name;
            const optionsInGroup = document.querySelectorAll(`input[name="${groupName}"]`);
            optionsInGroup.forEach(option => {
                option.parentElement.classList.remove('opcion-seleccionada');
            });
            if (radio.checked) {
                radio.parentElement.classList.add('opcion-seleccionada');
            }
        });
    });

    // --- CORRECCIÓN: Event listener del botón de copiar se asigna UNA SOLA VEZ ---
    // Se mueve fuera de la función displayResult para evitar duplicados.
    copyButton.addEventListener('click', () => {
        const animalName = document.getElementById('animal-name').textContent;
        const animalMotto = document.getElementById('animal-motto').textContent;
        const shareUrl = window.location.href;
        const shareText = `¡Descubrí que mi espíritu animal es un ${animalName}! ${animalMotto} Descubre el tuyo aquí:`;
        const textToCopy = `${shareText} ${shareUrl}`;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            copyFeedback.textContent = '¡Enlace copiado!';
            setTimeout(() => { copyFeedback.textContent = ''; }, 2000);
        }).catch(err => {
            console.error('Error al copiar el enlace: ', err);
            copyFeedback.textContent = 'Error al copiar';
        });
    });

    quizForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(quizForm);
        const totalQuestions = document.querySelectorAll('.question-block').length;
        if (formData.size < totalQuestions) {
            alert('Por favor, responde todas las preguntas.');
            return;
        }

        const respuestas = Object.fromEntries(formData);

        quizSection.classList.add('opacity-0');
        setTimeout(() => {
            quizSection.classList.add('hidden');
            loadingSection.classList.remove('hidden');
        }, 500);

        // --- MEJORA: Lógica de temporizador y API sincronizada ---
        let isTimerFinished = false;
        let apiResult = null;

        // 1. Inicia el temporizador del anuncio
        let timeLeft = 7; 
        adTimerEl.textContent = timeLeft;
        const adInterval = setInterval(() => {
            timeLeft--;
            adTimerEl.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(adInterval);
                isTimerFinished = true;
                // Si la API ya terminó cuando el timer acaba, muestra el resultado
                if (apiResult) {
                    displayResult(apiResult);
                }
            }
        }, 1000);

        // 2. Llama a la API
        try {
            const response = await fetch('/analizar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ respuestas }),
            });
            if (!response.ok) throw new Error(`Error del servidor: ${response.statusText}`);
            
            const result = await response.json();
            apiResult = result;
            // Si el timer ya terminó cuando la API responde, muestra el resultado
            if (isTimerFinished) {
                displayResult(apiResult);
            }
        } catch (error) {
            console.error('Error al analizar:', error);
            // --- CORRECCIÓN: String de una sola línea ---
            const errorResult = {
                animal: "Error",
                descripcion: "Hubo un problema al contactar a nuestros expertos animales. Por favor, intenta de nuevo más tarde.",
                lema: "A veces la selva digital tiene mala señal.",
                imagen: "error"
            };
            apiResult = errorResult;
            if (isTimerFinished) {
                displayResult(apiResult);
            }
        }
    });

    function displayResult(result) {
        loadingSection.classList.add('hidden');
        
        // --- MEJORA: Asegura que la opacidad se maneje correctamente ---
        resultSection.classList.remove('hidden', 'opacity-0');
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

        // La URL de Facebook ya estaba correcta, se mantiene.
        const facebookIntent = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`;
        document.getElementById('share-facebook').href = facebookIntent;
    }
});