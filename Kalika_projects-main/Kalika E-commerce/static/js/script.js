document.addEventListener('DOMContentLoaded', function () {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const form = document.getElementById('form');
    const errorMessage = document.getElementById('error-message');

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
        const mobileInput = document.getElementById("mobile");
        const passwordInput = document.getElementById("password");
        const confirmPasswordInput = document.getElementById("confirm-password");
    
        // Check if elements exist before accessing their values
        if (!nameInput || !emailInput || !mobileInput || !passwordInput || !confirmPasswordInput) {
            console.error("One or more form fields not found");
            if (errorMessage) {
                errorMessage.style.display = "block";
                errorMessage.textContent = "Form elements missing!";
            }
            return;
        }
    
        const name = nameInput.value;
        const email = emailInput.value;
        const mobile = mobileInput.value;
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
    
        // Check for existing user
        if (users.some(u => u.email === email || u.mobile === mobile)) {
            errorMessage.style.display = "block";
            errorMessage.textContent = "Email or mobile number already exists!";
        } else if (password !== confirmPassword) {
            errorMessage.style.display = "block";
            errorMessage.textContent = "Passwords do not match!";
        } else {
            // Register the user
            users.push({ name, email, mobile, password });
            localStorage.setItem('users', JSON.stringify(users));
            alert("Registration successful! You can now log in.");
            window.location.href = "login.html"; // Redirect to login page
        }
    
    }
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




