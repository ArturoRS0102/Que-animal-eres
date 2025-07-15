document.addEventListener('DOMContentLoaded', () => {
  const quizForm = document.getElementById('quiz-form');
  const quizSection = document.getElementById('quiz-section');
  const loadingSection = document.getElementById('loading-section');
  const resultSection = document.getElementById('result-section');
  const adTimerEl = document.getElementById('ad-timer');
  const copyButton = document.getElementById('copy-link');
  const copyFeedback = document.getElementById('copy-feedback');

  // Estilo al seleccionar
  document.querySelectorAll('input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', () => {
      const group = document.querySelectorAll(`input[name="${radio.name}"]`);
      group.forEach(r => r.parentElement.classList.remove('opcion-seleccionada'));
      if (radio.checked) {
        radio.parentElement.classList.add('opcion-seleccionada');
      }
    });
  });

  copyButton.addEventListener('click', () => {
    const name = document.getElementById('animal-name').textContent;
    const motto = document.getElementById('animal-motto').textContent;
    const url = window.location.href;
    const text = `¡Descubrí que mi espíritu animal es un ${name}! ${motto} Descúbrelo tú también:`;
    navigator.clipboard.writeText(`${text} ${url}`).then(() => {
      copyFeedback.textContent = '¡Enlace copiado!';
      setTimeout(() => { copyFeedback.textContent = ''; }, 2000);
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

    let isTimerDone = false;
    let apiResult = null;

    let timeLeft = 7;
    adTimerEl.textContent = timeLeft;
    const timer = setInterval(() => {
      timeLeft--;
      adTimerEl.textContent = timeLeft;
      if (timeLeft <= 0) {
        clearInterval(timer);
        isTimerDone = true;
        if (apiResult) displayResult(apiResult);
      }
    }, 1000);

    try {
      const res = await fetch('/analizar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ respuestas })
      });
      const result = await res.json();
      apiResult = result;
      if (isTimerDone) displayResult(apiResult);
    } catch (err) {
      console.error('Error al contactar API:', err);
      apiResult = {
        animal: 'Error',
        descripcion: 'Hubo un problema analizando tus respuestas.',
        lema: 'La selva digital está ocupada.',
        imagen: 'error'
      };
      if (isTimerDone) displayResult(apiResult);
    }
  });

  function displayResult(result) {
    loadingSection.classList.add('hidden');
    resultSection.classList.remove('hidden', 'opacity-0');
    resultSection.classList.add('opacity-100');

    document.getElementById('animal-name').textContent = result.animal;
    document.getElementById('animal-description').textContent = result.descripcion;
    document.getElementById('animal-motto').textContent = `"${result.lema}"`;
    document.getElementById('animal-image').src = `https://placehold.co/400x400/f9a825/ffffff?text=${encodeURIComponent(result.animal)}`;
    document.getElementById('animal-image').alt = `Imagen de un ${result.animal}`;

    const shareText = `¡Descubrí que mi espíritu animal es un ${result.animal}! \"${result.lema}\" Descubre el tuyo aquí:`;
    const shareUrl = window.location.href;
    document.getElementById('share-twitter').href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
    document.getElementById('share-facebook').href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`;
  }
});
