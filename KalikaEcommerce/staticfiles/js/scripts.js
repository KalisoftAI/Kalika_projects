document.addEventListener('DOMContentLoaded', function() {
    const categoriesBtn = document.getElementById('categories-btn');
    const categoriesMenu = document.getElementById('categories-menu');
    if (categoriesBtn && categoriesMenu) {
        categoriesBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            categoriesMenu.style.display = categoriesMenu.style.display === 'block' ? 'none' : 'block';
        });
        document.addEventListener('click', function() {
            categoriesMenu.style.display = 'none';
        });
        categoriesMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // Update cart count dynamically
    function updateCartCount() {
        fetch('/cart/count/')
            .then(response => response.json())
            .then(data => {
                document.querySelector('.cart-count').textContent = data.count;
            });
    }
    updateCartCount();
});