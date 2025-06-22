document.addEventListener('DOMContentLoaded', () => {
    // Fade-in and slide-up effect for product cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in', 'slide-up');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    document.querySelectorAll('.product-card').forEach(card => {
        observer.observe(card);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Sticky header effect with opacity transition
    const header = document.querySelector('nav');
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        if (currentScroll > 50) {
            header.classList.add('bg-opacity-90', 'shadow-md');
        } else {
            header.classList.remove('bg-opacity-90', 'shadow-md');
        }
        // Hide header on scroll down, show on scroll up
        if (currentScroll > lastScroll && currentScroll > 100) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        lastScroll = currentScroll;
    });

    // Category dropdown animation
    document.querySelectorAll('.dropdown-menu').forEach(dropdown => {
        dropdown.addEventListener('mouseenter', () => {
            dropdown.classList.add('opacity-100', 'translate-y-0');
            dropdown.classList.remove('opacity-0', 'translate-y-4');
        });
        dropdown.addEventListener('mouseleave', () => {
            dropdown.classList.add('opacity-0', 'translate-y-4');
            dropdown.classList.remove('opacity-100', 'translate-y-0');
        });
    });

    // Cart item count animation
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        const updateCartCount = () => {
            cartCount.classList.add('scale-125');
            setTimeout(() => {
                cartCount.classList.remove('scale-125');
            }, 200);
        };
        // Example: Trigger on cart update (you may need to call this from cart-related functions)
        document.addEventListener('cart-updated', updateCartCount);
    }

    // Product image zoom on hover
    document.querySelectorAll('.product-card img').forEach(img => {
        img.addEventListener('mouseenter', () => {
            img.style.transform = 'scale(1.1)';
            img.style.transition = 'transform 0.3s ease';
        });
        img.addEventListener('mouseleave', () => {
            img.style.transform = 'scale(1)';
        });
    });
});