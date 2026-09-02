// Funcionalidad interactiva local

document.addEventListener('DOMContentLoaded', () => {
    // Actualización del año en el pie de página
    const yearSpan = document.getElementById('currentYear');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Lógica de selectores del garaje
    const yearSelect = document.getElementById('yearSelect');
    const makeSelect = document.getElementById('makeSelect');
    const modelSelect = document.getElementById('modelSelect');

    if (yearSelect && makeSelect && modelSelect) {
        yearSelect.addEventListener('change', () => {
            const selected = yearSelect.value !== "";
            makeSelect.disabled = !selected;
            if (!selected) {
                modelSelect.disabled = true;
                makeSelect.value = "";
                modelSelect.value = "";
            }
        });

        makeSelect.addEventListener('change', () => {
            const selected = makeSelect.value !== "";
            modelSelect.disabled = !selected;
            if (!selected) {
                modelSelect.value = "";
            }
        });
    }
});