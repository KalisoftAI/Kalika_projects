// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize cart and user data from localStorage
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const errorMessage = document.getElementById('error-message');
    const userElement = document.getElementById('user-personalization');
    const userMenu = document.getElementById('user-menu');
    const userDropdown = document.getElementById('user-dropdown');
    const userInitial = document.getElementById('user-initial');
    const usernameDisplay = document.getElementById('username-display');
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');
    const dropdownList = document.getElementById('dropdown-list');
    

    // Function to update cart count
    function updateCartCount() {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
            const totalItems = cart.reduce((acc, item) => acc + item.quantity, 0);
            cartCountElement.textContent = totalItems;
        }
    }
    // Remove item from the cart
    function removeItemFromCart(index) {
        cart.splice(index, 1);
        updateCart();
        updateCartCount();
    }


    // Fetch user info and personalize the page
    async function fetchUserInfo() {
        try {
            const response = await fetch('/get_user_info');
            const result = await response.json();

            if (result.success && result.user_name) {
                // Get first initial of the username
                const firstInitial = result.user_name.charAt(0).toUpperCase();
                userInitial.textContent = firstInitial;
                usernameDisplay.textContent = result.user_name;

                // Hide login button and show the dropdown button with the user's initial
                loginButton.style.display = 'none'; // Hide login button
                userDropdown.style.display = 'inline-flex'; // Show the dropdown button
                userMenu.style.display = 'block'; // Show user menu (dropdown content)
            }
        } catch (error) {
            console.error('Error fetching user info:', error);
        }
    }

    // Toggle dropdown menu
    userDropdown.addEventListener('click', () => {
        dropdownList.style.display = dropdownList.style.display === 'block' ? 'none' : 'block';
    });

    // Logout handler
    logoutButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/logout', { method: 'GET' });
            const result = await response.json();
            if (result.success) {
                alert(result.message);
                location.reload(); // Reload the page to reset UI
            }
        } catch (error) {
            console.error('Error during logout:', error);
        }
    });
    
    // Call fetchUserInfo on page load
    fetchUserInfo();
    // Function to update cart count from the server
    function updateCartCountOnIndex() {
        fetch('/cart/count', {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
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

    
    // Logout functionality
    function logout() {
        localStorage.removeItem('cart');
        localStorage.removeItem('userName');
        alert('You have been logged out.');
        window.location.href = 'index.html';
    }

    // Attach logout event listener
    // const logoutButton = document.getElementById('logout');
    // if (logoutButton) {
    //     logoutButton.addEventListener('click', logout);
    // }

    // Search Functionality
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const popupSearchResults = document.getElementById('popupSearchResults');

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();

            if (!query) {
                popupSearchResults.style.display = 'none'; // Hide popup if input is empty
                searchResults.innerHTML = '';
                return;
            }

            popupSearchResults.style.display = 'block'; // Show popup

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

        // Hide popup when clicking outside
        document.addEventListener('click', (event) => {
            if (!popupSearchResults.contains(event.target) && event.target !== searchInput) {
                popupSearchResults.style.display = 'none';
            }
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
    fetchUserInfo();
    updateCartCount();
    displayCart();
    updateCartCountOnIndex();
    fetchUserInfo();
});
