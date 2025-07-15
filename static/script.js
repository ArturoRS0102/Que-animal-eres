document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("quiz-form");
    const quizSection = document.getElementById("quiz-section");
    const loadingSection = document.getElementById("loading-section");
    const resultSection = document.getElementById("result-section");

    const animalImage = document.getElementById("animal-image");
    const animalName = document.getElementById("animal-name");
    const animalDescription = document.getElementById("animal-description");
    const animalMotto = document.getElementById("animal-motto");

    const shareTwitter = document.getElementById("share-twitter");
    const shareFacebook = document.getElementById("share-facebook");
    const copyLink = document.getElementById("copy-link");
    const copyFeedback = document.getElementById("copy-feedback");

    // CORREGIR CLASES VISUALES – una sola seleccionada por pregunta
    const radios = document.querySelectorAll('input[type="radio"]');
    radios.forEach((radio) => {
        radio.addEventListener("change", () => {
            const group = document.querySelectorAll(`input[name="${radio.name}"]`);
            group.forEach((r) => r.parentElement.classList.remove("opcion-seleccionada"));
            if (radio.checked) {
                radio.parentElement.classList.add("opcion-seleccionada");
            }
        });
    });

    // Envío del formulario
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Recolectar respuestas
        const formData = new FormData(form);
        const respuestas = {};
        for (const [key, value] of formData.entries()) {
            respuestas[key] = value;
        }

        quizSection.classList.add("hidden");
        loadingSection.classList.remove("hidden");

        // Simular video publicitario (7 segundos)
        let tiempo = 7;
        const adTimer = document.getElementById("ad-timer");
        const countdown = setInterval(() => {
            tiempo--;
            adTimer.textContent = tiempo;
            if (tiempo <= 0) {
                clearInterval(countdown);
                mostrarResultado(respuestas);
            }
        }, 1000);
    });

    // Mostrar el resultado con llamada a la API Flask
    async function mostrarResultado(respuestas) {
        const response = await fetch("/evaluar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(respuestas),
        });
        const data = await response.json();

        loadingSection.classList.add("hidden");
        resultSection.classList.remove("hidden");

        animalImage.src = data.imagen || animalImage.src;
        animalName.textContent = data.nombre;
        animalDescription.textContent = data.descripcion;
        animalMotto.textContent = `"${data.lema}"`;

        const shareText = `¡Soy un ${data.nombre}! Descubre qué animal eres tú 👉 https://que-animal-eres.onrender.com`;

        shareTwitter.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
        shareFacebook.href = `https://www.facebook.com/sharer/sharer.php?u=https://que-animal-eres.onrender.com`;

        copyLink.addEventListener("click", () => {
            navigator.clipboard.writeText("https://que-animal-eres.onrender.com").then(() => {
                copyFeedback.textContent = "¡Enlace copiado!";
                setTimeout(() => {
                    copyFeedback.textContent = "";
                }, 2000);
            });
        });
    }
});

