document.addEventListener('DOMContentLoaded', function () {
    // Initialize global variables
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const users = JSON.parse(localStorage.getItem('users')) || [];

    // References to HTML elements
    const form = document.getElementById('form');
    const errorMessage = document.getElementById('error-message');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const logoutButton = document.getElementById('logout');

    // Function to calculate and display the cart count
    function updateCartCountOnIndex() {
        fetch('/cart/count', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
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

    // Function to display user name from localStorage
    function displayUserName() {
        const userName = localStorage.getItem('userName');
        if (userName) {
            const userElement = document.getElementById('user-personalization');
            if (userElement) {
                userElement.innerHTML = `<h3>Welcome, ${userName}!</h3>`;
            } else {
                console.error('User personalization element not found');
            }
        }
    }

    // Function to update cart in localStorage and re-render the display
    function updateCart() {
        localStorage.setItem('cart', JSON.stringify(cart));
        displayCart();
        updateCartCount();
    }

    
        

    // Function to handle logout
    function logout() {
        localStorage.removeItem('cart');
        localStorage.removeItem('userName');
        alert('You have been logged out.');
        window.location.href = 'index.html';
    }

    // Event listener for logout button
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    }

    // Function to create search results container
    function createSearchResultsContainer() {
        const searchResults = document.createElement('ul');
        searchResults.id = 'searchResults';
        searchResults.classList.add('search-results');
        searchInput.parentNode.appendChild(searchResults);
        return searchResults;
    }

    // Event listener for search input
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();
            const searchResults = document.getElementById('searchResults');
    
            // Clear results if input is empty
            if (!query) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none'; // Hide the dropdown
                return;
            }
    
            // Fetch data from the backend
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = ''; // Clear previous results
    
                    if (data.length === 0) {
                        searchResults.innerHTML = '<li class="dropdown-item">No products found</li>';
                        searchResults.style.display = 'block'; // Show the dropdown
                        return;
                    }
    
                    // Limit results to 7 and populate dropdown
                    const limitedResults = data.slice(0, 7);
                    limitedResults.forEach(product => {
                        const li = document.createElement('li');
                        li.classList.add('dropdown-item');
                        li.innerHTML = `<a href="#" class="product-link" data-itemcode="${product.itemcode}">${product.name}</a>`;
                        searchResults.appendChild(li);
                    });
    
                    searchResults.style.display = 'block'; // Show the dropdown
    
                    // Add event listeners for product links
                    document.querySelectorAll('.product-link').forEach(link => {
                        link.addEventListener('click', function (event) {
                            event.preventDefault();
                            const itemcode = this.dataset.itemcode;
                            showProductDetails(itemcode);
                        });
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    searchResults.innerHTML = '<li class="dropdown-item">Unable to fetch results. Try again later.</li>';
                    searchResults.style.display = 'block';
                });
        });
    
        // Hide dropdown when clicked outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.header-actions')) {
                const searchResults = document.getElementById('searchResults');
                if (searchResults) searchResults.style.display = 'none';
            }
        });
    }
    
    // Function to display product details
    function showProductDetails(itemcode) {
        const productDetailsSection = document.getElementById('product-details');
        const productName = document.getElementById('product-name');
        const productDescription = document.getElementById('product-description');
        const productPrice = document.getElementById('product-price');
        const addToCartButton = document.getElementById('add-to-cart');
    
        fetch(`/product/${itemcode}`)
            .then(response => response.json())
            .then(product => {
                if (product.error) {
                    alert(product.error);
                    return;
                }
    
                // Update product details
                productName.innerText = product.name;
                productDescription.innerText = product.description;
                productPrice.innerText = `Price: ₹${product.price}`;
                productDetailsSection.style.display = 'block';
    
                // Add to cart button functionality
                addToCartButton.onclick = () => {
                    alert(`${product.name} added to cart!`);
                };
            })
            .catch(error => {
                console.error('Error fetching product details:', error);
                alert('Error fetching product details');
            });
    }

    // Initial function calls on page load
    displayUserName();
    updateCartCountOnIndex();
    displayCart();
    
});






