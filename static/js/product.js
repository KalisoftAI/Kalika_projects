// static/js/product.js

document.addEventListener('DOMContentLoaded', function() {
    // Get the product ID from the URL path, e.g., /product/123
    const pathParts = window.location.pathname.split('/');
    const productId = pathParts[pathParts.length - 1];

    if (productId && !isNaN(productId)) {
        // Fetch data from the new API endpoint
        fetch(`/api/products/${productId}`)
            .then(response => response.json())
            .then(product => {
                if (product.error) {
                    document.getElementById('product-details-container').innerHTML = `<h2>${product.error}</h2>`;
                    return;
                }

                // Populate the product detail elements
                document.getElementById('product-name').innerText = product.name;
                document.getElementById('product-image').src = product.image_url;
                document.getElementById('product-image').alt = product.name;
                document.getElementById('product-description').innerText = product.description;
                document.getElementById('product-price').innerText = `RS. ${product.price.toFixed(2)}`;

                // You can reuse the addToCart function from main.js if it's loaded globally
                // or redefine it here if needed.
                const addToCartBtn = document.getElementById('add-to-cart-btn');
                if(addToCartBtn){
                    addToCartBtn.onclick = () => {
                         // A global addToCart function would be ideal here
                         alert(`Added ${product.name} to cart.`);
                    };
                }
            })
            .catch(error => {
                console.error('Error fetching product details:', error);
                document.getElementById('product-details-container').innerHTML = '<h2>Error loading product details.</h2>';
            });
    }
});