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

    const loginMenu = document.querySelector('.login-menu');
    const loginToggle = document.querySelector('.login-toggle');

    if (loginMenu && loginToggle) {
        loginToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const isOpen = loginMenu.classList.toggle('open');
            loginToggle.setAttribute('aria-expanded', isOpen);
        });

        document.addEventListener('click', (event) => {
            if (!loginMenu.contains(event.target)) {
                loginMenu.classList.remove('open');
                loginToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
});