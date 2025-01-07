// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize variables and get DOM elements
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const errorMessage = document.getElementById('error-message');
    const userElement = document.getElementById('user-personalization');
    const userMenu = document.getElementById('user-menu');
    const userDropdown = document.getElementById('user-dropdown');
    const editProfileButton = document.getElementById('edit-profile-button');
    const editAddressButton = document.getElementById('edit-address-button');
    const editAddressModal = document.getElementById('edit-address-modal');
    const cancelEditAddressButton = document.getElementById('cancel-edit-address');
    const editAddressForm = document.getElementById('edit-address-form');
    const userInitial = document.getElementById('user-initial');
    const usernameDisplay = document.getElementById('username-display');
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');
    const dropdownList = document.getElementById('dropdown-list');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const popupSearchResults = document.getElementById('popupSearchResults');
    const cartItemsContainer = document.getElementById('cart-items');

    // Function to update cart count
    function updateCartCount() {
        fetch('/cart/count')
            .then(response => response.json())
            .then(data => {
                const cartCountElement = document.querySelector('.cart-count');
                if (cartCountElement) {
                    cartCountElement.textContent = data.cart_count || 0;
                } else {
                    console.error("Cart count element not found!");
                }
            })
            .catch(error => console.error("Error fetching cart count:", error));
    }
    
    function removeItemFromCart(itemcode) {
        fetch('/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ itemcode: itemcode, action: 'remove' })
        })
            .then(response => response.json())
            .then(data => {
                console.log("Updated cart:", data.cart_items);
                updateCartCount(); // Update cart count in the header
            })
            .catch(error => console.error("Error removing item from cart:", error));
    }
    

    // Toggle dropdown visibility
    if (userDropdown) {
        userDropdown.addEventListener('click', () => {
            const isMenuVisible = userMenu && userMenu.style.display === 'block';
            if (userMenu) userMenu.style.display = isMenuVisible ? 'none' : 'block';
        });
    }

    // Close dropdown if clicked outside
    document.addEventListener('click', (event) => {
        if (userDropdown && userMenu && !userDropdown.contains(event.target) && !userMenu.contains(event.target)) {
            userMenu.style.display = 'none';
        }
    });

    // Show edit address modal
    if (editAddressButton) {
        editAddressButton.addEventListener('click', (event) => {
            event.preventDefault();
            if (editAddressModal) editAddressModal.style.display = 'block';
        });
    }

    // Close edit address modal
    if (cancelEditAddressButton) {
        cancelEditAddressButton.addEventListener('click', () => {
            if (editAddressModal) editAddressModal.style.display = 'none';
        });
    }

    // Fetch and personalize user info
    async function fetchUserInfo() {
        try {
            const response = await fetch('/get_user_info');
            const result = await response.json();

            if (result.success && result.user_name) {
                const firstInitial = result.user_name.charAt(0).toUpperCase();
                if (userInitial) userInitial.textContent = firstInitial;
                if (usernameDisplay) usernameDisplay.textContent = result.user_name;

                if (loginButton) loginButton.style.display = 'none';
                if (userDropdown) userDropdown.style.display = 'inline-flex';
                if (userMenu) userMenu.style.display = 'none';
            }
        } catch (error) {
            console.error('Error fetching user info:', error);
        }
    }

    // Redirect to edit profile page
    if (editProfileButton) {
        editProfileButton.addEventListener('click', (event) => {
            event.preventDefault();
            window.location.href = '/edit_profile';
        });
    }

    // Handle address form submission
    if (editAddressForm) {
        editAddressForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(editAddressForm);
            const addressData = Object.fromEntries(formData);

            try {
                const response = await fetch('/save_address', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(addressData),
                });

                if (response.ok) {
                    alert('Address updated successfully!');
                    if (editAddressModal) editAddressModal.style.display = 'none';
                } else {
                    alert('Failed to update address. Please try again.');
                }
            } catch (error) {
                console.error('Error saving address:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }

    // Handle logout
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/logout', { method: 'GET' });
                const result = await response.json();
                if (result.success) {
                    alert(result.message);
                    window.location.href = '/login';  // Redirect to login page after logout
                } else {
                    alert('Error: Unable to log out. Please try again.');
                }
            } catch (error) {
                console.error('Error during logout:', error);
            }
        });
    }

    // Function to display cart items
    function displayCart() {
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

     // Handle search input
     if (searchInput) {
        // Handle real-time search for the popup
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();

            if (!query) {
                if (popupSearchResults) popupSearchResults.style.display = 'none';
                if (searchResults) searchResults.innerHTML = '';
                return;
            }

            if (popupSearchResults) popupSearchResults.style.display = 'block';

            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (searchResults) {
                        searchResults.innerHTML = data.length
                            ? data.slice(0, 7).map(product => `
                                <li>
                                    <a href="/product/${product.itemcode}" target="_blank">${product.name}</a>
                                </li>
                            `).join('')
                            : '<li>No products found</li>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching search results:', error);
                    if (searchResults) searchResults.innerHTML = '<li>Error fetching results. Please try again later.</li>';
                });
        });

        // Hide popup when clicking outside
        document.addEventListener('click', (event) => {
            if (popupSearchResults && !popupSearchResults.contains(event.target) && event.target !== searchInput) {
                popupSearchResults.style.display = 'none';
            }
        });
    }

    if (searchBtn) {
        // Redirect to the search results page when the button is clicked
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/search/results?q=${encodeURIComponent(query)}`;
            }
        });

    // Add functionality for "Add to Cart" buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function () {
            const form = this.closest('form');
            const formData = new FormData(form);
            const jsonData = Object.fromEntries(formData.entries());
    
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(jsonData),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Cart updated:', data);
                updateCartCount();
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Initialize carousel
    function initializeCarousel() {
        const slides = [
            { image: '../static/image/banner1.jpg' },
            { image: '../static/image/banner2.jpg' },
            { image: '../static/image/banner3.jpg' },
        ];

        const indicators = document.querySelector('.carousel-indicators');
        const inner = document.querySelector('.carousel-inner');

        slides.forEach((slide, index) => {
            const indicator = document.createElement('li');
            indicator.dataset.target = '#heroCarousel';
            indicator.dataset.slideTo = index;
            if (index === 0) indicator.classList.add('active');
            if (indicators) indicators.appendChild(indicator);

            const item = document.createElement('div');
            item.classList.add('item');
            if (index === 0) item.classList.add('active');
            item.style.backgroundImage = `url('${slide.image}')`;
            if (inner) inner.appendChild(item);
        });
    }

    // Initial calls on page load
    fetchUserInfo();
    updateCartCount();
    displayCart();
    initializeCarousel();
}
});

