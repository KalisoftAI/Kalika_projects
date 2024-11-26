document.addEventListener('DOMContentLoaded', function () {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const form = document.getElementById('form');
    const errorMessage = document.getElementById('error-message');
    // Select the search input and the container for search results
//    const searchInput = document.getElementById('searchInput');
//    let searchResults = null; // Placeholder for the dynamically created results container
//    const productDetailsSection = document.getElementById('productDetails'); // Product details section
//    const productName = document.getElementById('productName');
//    const productSubcategory = document.getElementById('productSubcategory');
//    const productPrice = document.getElementById('productPrice');
//    const productDescription = document.getElementById('productDescription');
//    const addToCartButton = document.getElementById('addToCart');

    document.querySelectorAll('.product-form').forEach(form => {
        form.addEventListener('submit', event => {
            event.preventDefault(); // Prevent default form submission
    
            const formData = new FormData(form);
    
            fetch('/add_to_cart', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url; // Redirect to the cart page
                } else {
                    console.log('Item added to cart successfully!');
                }
            })
            .catch(error => console.error('Error adding to cart:', error));
        });
    });

    // Function to calculate and display the cart count
    function updateCartCount() {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) { // Check if element exists
            let totalItems = cart.reduce((acc, item) => acc + item.quantity, 0);
            cartCountElement.textContent = totalItems;
            updateCartCount();
        } 
    }

    // Function to display user name
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

    // Function to update the cart in localStorage and re-render the display
    function updateCart() {
        localStorage.setItem('cart', JSON.stringify(cart));
        displayCart();
    }

    // Function to display cart items
    function displayCart() {
        const cartItemsContainer = document.getElementById('cart-items');
        if (cartItemsContainer) {
            if (cart.length === 0) {
                cartItemsContainer.innerHTML = '<li>Your cart is empty.</li>';
                return;
            }

            // Clear previous items
            cartItemsContainer.innerHTML = '';

            // Loop through each item and create list elements
            cart.forEach((item, index) => {
                const listItem = document.createElement('li');

                // Create product image element
                const productImage = document.createElement('img');
                productImage.src = `images/${item.name.replace(/\s+/g, '_').toLowerCase()}.jpg`;
                productImage.alt = item.name;
                productImage.classList.add('product-image');

                // Create product info element
                const productInfo = document.createElement('div');
                productInfo.classList.add('product-info');
                productInfo.innerHTML = ` ${item.name}- Quantity: ${item.quantity} - Price: RS.${item.price}`;

                // Create buttons to increase/decrease quantity
                const increaseButton = document.createElement('button');
                increaseButton.classList.add('quantity-btn');
                increaseButton.textContent = '+';
                increaseButton.addEventListener('click', () => {
                    cart[index].quantity += 1;
                    updateCart();
                    updateCartCount(); // Update count after changing quantity
                });

                const decreaseButton = document.createElement('button');
                decreaseButton.classList.add('quantity-btn');
                decreaseButton.textContent = '-';
                decreaseButton.addEventListener('click', () => {
                    if (cart[index].quantity > 1) {
                        cart[index].quantity -= 1;
                    } else {
                        cart.splice(index, 1); // Remove item if quantity is 0
                    }
                    updateCart();
                    updateCartCount(); // Update count after changing quantity
                });

                // Create remove button
                const removeButton = document.createElement('button');
                removeButton.classList.add('remove-btn');
                removeButton.textContent = 'Remove';
                removeButton.addEventListener('click', () => {
                    cart.splice(index, 1); // Remove item from cart
                    updateCart();
                    updateCartCount(); // Update count after removing item
                });

                // Append image, info, and buttons to list item
                listItem.appendChild(productImage);
                listItem.appendChild(productInfo);
                listItem.appendChild(increaseButton);
                listItem.appendChild(decreaseButton);
                listItem.appendChild(removeButton);

                cartItemsContainer.appendChild(listItem);
            });
        } 
        
   }

    // Function to clear the cart and logout
    function logout() {
        localStorage.removeItem('cart');
        localStorage.removeItem('userName');
        alert("You have been logged out.");
        window.location.href = "index.html";
    }

    // Event listener for logout button
    document.addEventListener('DOMContentLoaded', function() {
        const logoutButton = document.getElementById('logout');
        if (logoutButton) {
            logoutButton.addEventListener('click', logout);
        } else {
            console.warn("Logout button not found, no action will be taken.");
        }

        function logout() {
            // Your logout logic here
            console.log("Logging out...");
        }
    });

    // Call functions on page load
    displayUserName();
    updateCartCount();
    displayCart();
    

    // Registration Logic
    function handleRegister(event) {
        event.preventDefault();
        
        // Retrieve form elements
        const nameInput = document.getElementById("name");
        const emailInput = document.getElementById("email");
//        const mobileInput = document.getElementById("mobile");
        const passwordInput = document.getElementById("password");
        const confirmPasswordInput = document.getElementById("confirm-password");
    
        // Check if elements exist before accessing their values
        if (!nameInput || !emailInput || !passwordInput || !confirmPasswordInput) {
            console.error("One or more form fields not found");
            if (errorMessage) {
                errorMessage.style.display = "block";
                errorMessage.textContent = "Form elements missing!";
            }
            return;
        }
    
        const name = nameInput.value;
        const email = emailInput.value;
//        const mobile = mobileInput.value;
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
    
        // Check for existing user
        if (users.some(u => u.email === email )) {
            errorMessage.style.display = "block";
            errorMessage.textContent = "Email number already exists!";
        } else if (password !== confirmPassword) {
            errorMessage.style.display = "block";
            errorMessage.textContent = "Passwords do not match!";
        } else {
            // Register the user
            users.push({ name, email, password });
            localStorage.setItem('users', JSON.stringify(users));
            alert("Registration successful! You can now log in.");
            window.location.href = "login.html"; // Redirect to login page
        }
    
    }
});

// Function to create the results container
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    let searchResults = null; // Placeholder for dynamically created results container
    const productDetailsSection = document.getElementById('productDetails');
    const productName = document.getElementById('productName');
    const productSubcategory = document.getElementById('productSubcategory');
    const productPrice = document.getElementById('productPrice');
    const productDescription = document.getElementById('productDescription');
    const addToCartButton = document.getElementById('addToCart');
    function createSearchResultsContainer() {
        searchResults = document.createElement('ul');
        searchResults.id = 'searchResults';
        searchResults.classList.add('search-results');
        searchInput.parentNode.appendChild(searchResults); // Append results below the input
    }

//    // Event listener for handling input changes in the search bar
//    searchInput.addEventListener('input', () => {
//        const query = searchInput.value.trim(); // Get the input value and trim extra spaces
//
//        // Clear the results if the input is empty
//        if (query.length === 0) {
//            if (searchResults) searchResults.innerHTML = '';
//            return;
//        }
//
//        // Ensure the search results container exists
//        if (!searchResults) createSearchResultsContainer();
//
//        // Fetch data from the backend API
//        fetch(`/search?q=${encodeURIComponent(query)}`)
//            .then(response => {
//                if (!response.ok) {
//                    throw new Error('Failed to fetch search results');
//                }
//                return response.json();
//            })
//            .then(data => {
//                // Clear previous results
//                searchResults.innerHTML = '';
//
//                // Check if there are results
//                if (data.length === 0) {
//                    searchResults.innerHTML = '<li>No products found</li>';
//                    return;
//                }
//
//                // Limit results to 7 products
//                const limitedResults = data.slice(0, 7);
//
//                // Populate the search results
//                limitedResults.forEach(product => {
//                    const li = document.createElement('li');
//                    li.innerHTML = `<a href="#" class="product-link" data-itemcode="${product.itemcode}">${product.name}</a>`;
//                    searchResults.appendChild(li);
//                });
//
//                // Add event listeners for each product link
//                const productLinks = document.querySelectorAll('.product-link');
//                productLinks.forEach(link => {
//                    link.addEventListener('click', function(event) {
//                        event.preventDefault();  // Prevent the default link behavior
//                        const itemcode = this.getAttribute('data-itemcode');
//                        showProductDetails(itemcode);  // Show product details
//                    });
//                });
//            })
//            .catch(error => {
//                console.error('Error fetching search results:', error);
//                searchResults.innerHTML = '<li>Error fetching results. Please try again later.</li>';
//            });
//    });



    // Function to display product details
    function showProductDetails(itemcode) {
        const productDetailsSection = document.getElementById('product-details');
        const productName = document.getElementById('product-name');
        const productDescription = document.getElementById('product-description');
        const productPrice = document.getElementById('product-price');
        const addToCartButton = document.getElementById('add-to-cart');
        // Fetch product details from the backend
        fetch(`/product/${itemcode}`)
            .then(response => response.json())
            .then(product => {
                if (product.error) {
                    alert(product.error); // Handle backend errors
                    return;
                }

                // Update the product details section with fetched data
                productName.innerText = product.name;
                productDescription.innerText = product.description;
                productPrice.innerText = `Price: $${product.price}`;

                // Show the product details section
                productDetailsSection.style.display = 'block';

                // Handle 'Add to Cart' button functionality
                addToCartButton.onclick = () => {
                    alert(`${product.name} added to cart!`);
                    // Add logic to update cart, if needed
                };
            })
            .catch(error => {
                console.error('Error fetching product details:', error);
                alert('Error fetching product details');
            });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    let searchResults = null; // Placeholder for dynamically created results container

    function createSearchResultsContainer() {
        searchResults = document.createElement('ul');
        searchResults.id = 'searchResults';
        searchResults.classList.add('search-results');
        searchInput.parentNode.appendChild(searchResults); // Append results below the input
    }

    // Event listener for handling input changes in the search bar
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim(); // Get the input value and trim extra spaces

        // Clear the results if the input is empty
        if (query.length === 0) {
            if (searchResults) searchResults.innerHTML = '';
            return;
        }

        // Ensure the search results container exists
        if (!searchResults) createSearchResultsContainer();

        // Fetch data from the backend API
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch search results');
                }
                return response.json();
            })
            .then(data => {
                // Clear previous results
                searchResults.innerHTML = '';

                // Check if there are results
                if (!Array.isArray(data) || data.length === 0) {
                    searchResults.innerHTML = '<li>No products found</li>';
                    return;
                }

                // Limit results to 7 products
                const limitedResults = data.slice(0, 7);

//                // Populate the search results
//                limitedResults.forEach(product => {
//                    const li = document.createElement('li');
//                    li.innerHTML = `<a href="/product/${product.itemcode}" target="_blank">${product.productname || 'Unnamed Product'}</a>`;
//                    searchResults.appendChild(li);
//                });
//            })
                         // Populate the search results
                limitedResults.forEach(product => {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="/product/${product.itemcode}" target="_blank">${product.name || 'Unnamed Product'}</a>`;
                    searchResults.appendChild(li);
                });

            })
            .catch(error => {
                console.error('Error fetching search results:', error);
                if (searchResults) {
                    searchResults.innerHTML = '<li>Error fetching results. Please try again later.</li>';
                }
            });
    });

    // Event listener for the search button to redirect to a category page if needed
    document.getElementById('searchButton').addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query.length > 0) {
            window.location.href = `/search?q=${encodeURIComponent(query)}`;
        }
    });
});

//  Login Logic
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('form');
    const errorMessage = document.getElementById('error-message');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'email': email, 'password': password })
            });

            const result = await response.json();
            if (result.success) {
                alert("Login successful!");
                window.location.href = "/";  // Redirect to the desired page
            } else {
                errorMessage.style.display = "block";
                errorMessage.textContent = result.message;
            }
        } catch (error) {
            console.error('Error during login:', error);
            errorMessage.style.display = "block";
            errorMessage.textContent = "Login failed! Please try again.";
        }
    });
});




