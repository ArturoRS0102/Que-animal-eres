document.addEventListener('DOMContentLoaded', () => {
    const quizForm = document.getElementById('quiz-form');
    const quizSection = document.getElementById('quiz-section');
    const loadingSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('result-section');
    const adTimerEl = document.getElementById('ad-timer');
    const copyButton = document.getElementById('copy-link');
    const copyFeedback = document.getElementById('copy-feedback');

    // Maneja el estilo visual de la selección
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', () => {
            document.querySelectorAll(`input[name="${radio.name}"]`).forEach(option => {
                option.parentElement.classList.remove('opcion-seleccionada');
            });
            if (radio.checked) {
                radio.parentElement.classList.add('opcion-seleccionada');
            }
        });
    });

    // Asigna el evento al botón de copiar una sola vez
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
            console.error('Error al copiar: ', err);
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

        let isTimerFinished = false;
        let apiResult = null;

        const showResultIfNeeded = () => {
            if (isTimerFinished && apiResult) {
                displayResult(apiResult);
            }
        };

        let timeLeft = 7; 
        adTimerEl.textContent = timeLeft;
        const adInterval = setInterval(() => {
            timeLeft--;
            adTimerEl.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(adInterval);
                isTimerFinished = true;
                showResultIfNeeded();
            }
        }, 1000);

        try {
            const response = await fetch('/analizar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ respuestas }),
            });
            if (!response.ok) throw new Error(`Error del servidor: ${response.statusText}`);
            apiResult = await response.json();
            showResultIfNeeded();
        } catch (error) {
            console.error('Error al analizar:', error);
            apiResult = {
                animal: "Error",
                descripcion: "Hubo un problema al contactar a nuestros expertos animales. Por favor, intenta de nuevo más tarde.",
                lema: "A veces la selva digital tiene mala señal.",
                imagen: "error"
            };
            showResultIfNeeded();
        }
    });

    function displayResult(result) {
        loadingSection.classList.add('hidden');
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

        document.getElementById('share-twitter').href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
        document.getElementById('share-facebook').href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`;
    }
});
