document.addEventListener('DOMContentLoaded', () => {
    // Initialize range sliders to show the current value
    const ranges = document.querySelectorAll('input[type="range"]');
    for (const range of ranges) {
        const percentElement = document.createElement('div');
        percentElement.textContent = `${range.value}%`;
        percentElement.className = 'percent ms-3';
        range.insertAdjacentElement('afterend', percentElement);
        range.addEventListener('input', () => percentElement.innerHTML = `${range.value}%`);
    }

    // Initialize doNotFollowLinks
    const doNotFollowLinks = document.querySelectorAll("a[data-do-not-follow-link]");
    for (const link of doNotFollowLinks) {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            fetch(link.href);
        });
    }

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => 
        new bootstrap.Tooltip(tooltipTriggerEl))
});