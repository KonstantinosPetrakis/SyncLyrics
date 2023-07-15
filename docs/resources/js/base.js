function infoBoxesObserved(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add('active');
    });
}


document.addEventListener('DOMContentLoaded', () => {
    let observer = new IntersectionObserver(infoBoxesObserved, {
        root: null,
        rootMargin: '0px',
        threshold: [0.2, 0.2, 1, 1]
    });

    const infoBoxes = document.querySelectorAll('.info-box');
    for (let i = 0; i < infoBoxes.length; i++) {
        observer.observe(infoBoxes[i]);
        infoBoxes[i].style.setProperty('--direction', i % 2 == 0 ? 1 : -1);
    }
});