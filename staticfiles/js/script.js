
document.addEventListener("DOMContentLoaded", function () {
    // Smooth Scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Mobile Navbar Toggle
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarMenu = document.querySelector(".navbar-collapse");

    if (navbarToggler) {
        navbarToggler.addEventListener("click", function () {
            navbarMenu.classList.toggle("show");
        });
    }

    // Fade-in effect on scroll
    function fadeInOnScroll() {
        document.querySelectorAll(".fade-in").forEach((element) => {
            if (element.getBoundingClientRect().top < window.innerHeight - 100) {
                element.classList.add("visible");
            }
        });
    }

    window.addEventListener("scroll", fadeInOnScroll);
    fadeInOnScroll(); // Run on load

    // Dark Mode Toggle (Optional)
    const darkModeBtn = document.getElementById("dark-mode-btn");
    if (darkModeBtn) {
        darkModeBtn.addEventListener("click", function () {
            document.body.classList.toggle("dark-mode");
        });
    }
});

// Animated Counter Script
document.addEventListener('DOMContentLoaded', () => {
    const counters = document.querySelectorAll('.counter');

    counters.forEach(counter => {
        counter.innerText = '0';

        const updateCounter = () => {
            const target = +counter.getAttribute('data-target');
            const current = +counter.innerText;
            const increment = target / 100;

            if (current < target) {
                counter.innerText = Math.ceil(current + increment);
                setTimeout(updateCounter, 20);
            } else {
                counter.innerText = target + '+';
            }
        };

        updateCounter();
    });
});