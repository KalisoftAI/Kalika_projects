// main.js
let cart = [];
let products = [];

async function fetchProducts() {
    const response = await fetch('/api/products');
    products = await response.json();
    const productList = document.getElementById('productList');
    productList.innerHTML = '';
    products.forEach(product => {
        const productEl = document.createElement('div');
        productEl.className = 'product';
        productEl.innerHTML = `
            <img src="${product.image_url}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>$${product.price.toFixed(2)}</p>
            <button onclick="addToCart(${product.id})">Add to Cart</button>
        `;
        productList.appendChild(productEl);
    });
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    cart.push(product);
    updateCart();
}

function updateCart() {
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    cartItems.innerHTML = '';
    let total = 0;
    cart.forEach(product => {
        const li = document.createElement('li');
        li.textContent = `${product.name} - $${product.price.toFixed(2)}`;
        cartItems.appendChild(li);
        total += product.price;
    });
    cartTotal.textContent = total.toFixed(2);
}

document.getElementById('checkout').addEventListener('click', async () => {
    const response = await fetch('/api/punchout/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ items: cart.map(item => item.id) }),
    });
    if (response.ok) {
        const result = await response.json();
        window.location.href = result.returnUrl;
    }
});

fetchProducts();



