// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Check if we are on a page that has the productList element
    if (document.getElementById('productList')) {
        fetchProducts();
    }
    // Update the cart display on every page load
    updateCartDisplay();
});

// Load cart from localStorage or initialize an empty array
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

async function fetchProducts() {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) throw new Error('Network response was not ok');

        const products = await response.json();
        const productList = document.getElementById('productList');
        productList.innerHTML = ''; // Clear loading message

        products.forEach(product => {
            const productEl = document.createElement('div');
            productEl.className = 'product-card'; // Use your existing CSS class
            // Note: The link now goes to the product detail page shell
            productEl.innerHTML = `
                <div class="product-image-wrapper">
                    <a href="/product/${product.id}">
                        <img src="${product.image_url}" alt="${product.name}" class="product-image">
                    </a>
                </div>
                <h3 class="product_name">${product.name}</h3>
                <p class="product-description">${product.description.substring(0, 100)}...</p>
                <span class="product_price">RS. ${product.price.toFixed(2)}</span>
                <button class="add-to-cart" onclick="addToCart(${product.id}, '${product.name}', ${product.price}, '${product.image_url}')">Add to Cart</button>
            `;
            productList.appendChild(productEl);
        });
    } catch (error) {
        console.error('Error fetching products:', error);
        document.getElementById('productList').innerHTML = '<p>Error loading products. Please try again later.</p>';
    }
}

function addToCart(productId, productName, productPrice, productImageUrl) {
    const existingItem = cart.find(item => item.id === productId);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: productName,
            price: productPrice,
            image_url: productImageUrl,
            quantity: 1
        });
    }

    saveCart();
    updateCartDisplay();
    alert(`Added ${productName} to cart!`);
}

function updateCartDisplay() {
    const cartCountEl = document.querySelector('.cart-count');
    if (cartCountEl) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCountEl.textContent = totalItems;
    }
}