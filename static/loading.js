document.addEventListener('DOMContentLoaded', () => {
    const progressBar = document.getElementById('progress-bar');
    const stepsText = document.getElementById('steps-text');

    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${wsProtocol}://${window.location.host}/ws/progresso`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        progressBar.style.width = data.progress + "%";
        stepsText.textContent = data.progress + "%";

        if (data.progress >= 100) {
            window.location.href = "/resultado";
        }
    };

    ws.onerror = (err) => {
        console.error("Erro WebSocket:", err);
        alert("Falha na barra de progresso. A análise continuará, mas a barra não será exibida.");
    };
});
