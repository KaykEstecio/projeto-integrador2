document.addEventListener('DOMContentLoaded', () => {
    const track = document.querySelector('.carousel-track');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    if (!track) return; // Only run on pages with carousel

    const cards = Array.from(document.querySelectorAll('.car-card'));
    let currentIndex = 0;
    const totalCards = cards.length;

    function updateCarousel() {
        cards.forEach((card, index) => {
            // Calculate distance from current index
            let offset = (index - currentIndex + totalCards) % totalCards;

            // Adjust for negative wrapping
            if (offset > totalCards / 2) {
                offset -= totalCards;
            }

            // Styles based on offset
            let transform = '';
            let opacity = 0;
            let zIndex = 0;
            let filter = 'blur(5px) brightness(0.5)';

            if (offset === 0) {
                // Center item
                transform = 'translateX(0) scale(1)';
                opacity = 1;
                zIndex = 10;
                filter = 'none';
            } else if (offset === 1) {
                // Right item
                transform = 'translateX(60%) scale(0.8) rotateY(-15deg)';
                opacity = 0.8;
                zIndex = 5;
            } else if (offset === -1) {
                // Left item
                transform = 'translateX(-60%) scale(0.8) rotateY(15deg)';
                opacity = 0.8;
                zIndex = 5;
            } else {
                // Hidden items
                transform = 'translateX(0) scale(0.5)';
                opacity = 0;
                zIndex = 0;
            }

            card.style.transform = transform;
            card.style.opacity = opacity;
            card.style.zIndex = zIndex;
            card.style.filter = filter;
        });
    }

    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % totalCards;
        updateCarousel();
    });

    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + totalCards) % totalCards;
        updateCarousel();
    });

    // Initial update
    updateCarousel();
});
