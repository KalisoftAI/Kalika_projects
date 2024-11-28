// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize cart and user data from localStorage
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const errorMessage = document.getElementById('error-message');

    // Function to update cart count
    function updateCartCount() {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
            const totalItems = cart.reduce((acc, item) => acc + item.quantity, 0);
            cartCountElement.textContent = totalItems;
        }
    }

    document.addEventListener("DOMContentLoaded", async () => {
        const userElement = document.getElementById('user-personalization');
        const loginButton = document.getElementById('login-button');
    
        fetch('/get_user_info')
        .then(response => response.json())
        .then(result => {
            if (result.success && result.user_name) {
                userElement.innerHTML = `<h3>Welcome, ${result.user_name}!</h3>`;
                loginButton.style.display = 'none'; // Hide login button
            }
        })
        .catch(error => {
            console.error('Error fetching user info:', error);
        });

    });

    // Function to update cart in localStorage and refresh the display
    function updateCartCountOnIndex() {
        fetch('/cart/count', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            const cartCountElement = document.querySelector('.cart-count');
            if (cartCountElement) {
                cartCountElement.textContent = data.cart_count || 0; // Update the cart count
            }
        })
        .catch(error => console.error('Error fetching cart count:', error));
    }

    // Remove item from the cart
    function removeItemFromCart(index) {
        cart.splice(index, 1);
        updateCart();
        updateCartCount();
    }

    // Logout functionality
    function logout() {
        localStorage.removeItem('cart');
        localStorage.removeItem('userName');
        alert('You have been logged out.');
        window.location.href = 'index.html';
    }

    // Attach logout event listener
    const logoutButton = document.getElementById('logout');
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    }

    

    // Search Functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchResults = null;

        function createSearchResultsContainer() {
            searchResults = document.createElement('ul');
            searchResults.id = 'searchResults';
            searchResults.classList.add('search-results');
            searchInput.parentNode.appendChild(searchResults);
        }

        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();
            if (!query) {
                if (searchResults) searchResults.innerHTML = '';
                return;
            }

            if (!searchResults) createSearchResultsContainer();

            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = data.length
                        ? data.slice(0, 7).map(product => `
                            <li>
                                <a href="/product/${product.itemcode}" target="_blank">${product.name}</a>
                            </li>
                        `).join('')
                        : '<li>No products found</li>';
                })
                .catch(error => {
                    console.error('Error fetching search results:', error);
                    searchResults.innerHTML = '<li>Error fetching results. Please try again later.</li>';
                });
        });
    }

    // Function to display cart items
    function displayCart() {
        const cartItemsContainer = document.getElementById('cart-items');
        if (cartItemsContainer) {
            cartItemsContainer.innerHTML = cart.length
                ? cart.map((item, index) => `
                    <li>
                        <img src="images/${item.name.replace(/\s+/g, '_').toLowerCase()}.jpg" alt="${item.name}" class="product-image">
                        <div class="product-info">${item.name} - Quantity: ${item.quantity} - Price: ₹${item.price}</div>
                        <button class="quantity-btn" onclick="updateItemQuantity(${index}, 1)">+</button>
                        <button class="quantity-btn" onclick="updateItemQuantity(${index}, -1)">-</button>
                        <button class="remove-btn" onclick="removeItemFromCart(${index})">Remove</button>
                    </li>
                `).join('')
                : '<li>Your cart is empty.</li>';
        }
    }

    // Initial calls on page load
    displayUserName();
    updateCartCount();
    displayCart();
    updateCartCountOnIndex();
    
});
