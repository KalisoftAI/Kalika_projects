//document.addEventListener('DOMContentLoaded', function () {
//    let cart = JSON.parse(localStorage.getItem('cart')) || [];
//    const users = JSON.parse(localStorage.getItem('users')) || [];
//    const form = document.getElementById('form');
//    const errorMessage = document.getElementById('error-message');
//
//    // Function to add item to cart
//    function addToCart(name, price) {
//        const existingItem = cart.find(item => item.name === name);
//        if (existingItem) {
//            existingItem.quantity += 1; // Increase quantity if already in cart
//        } else {
//            cart.push({ name, price, quantity: 1 }); // Add new item
//        }
//        updateCart(); // Update localStorage and re-render the display
//    }
//
//    // Event listener for "Add to Cart" buttons
//    document.querySelectorAll('.add-to-cart').forEach(button => {
//        button.addEventListener('click', function () {
//            const productName = this.getAttribute('data-name');
//            const productPrice = parseInt(this.getAttribute('data-price'));
//            addToCart(productName, productPrice); // Add product to cart
//        });
//    });
//
//    // Function to calculate and display the cart count
//    function updateCartCount() {
//        const cartCountElement = document.querySelector('.cart-count');
//        if (cartCountElement) { // Check if element exists
//            let totalItems = cart.reduce((acc, item) => acc + item.quantity, 0);
//            cartCountElement.textContent = totalItems;
//            updateCartCount();
//        }
//    }
//
//    // Function to display user name
//    function displayUserName() {
//        const userName = localStorage.getItem('userName');
//        if (userName) {
//            const userElement = document.getElementById('user-personalization');
//            if (userElement) {
//                userElement.innerHTML = `<h3>Welcome, ${userName}!</h3>`;
//            } else {
//                console.error('User personalization element not found');
//            }
//        }
//    }
//
//    // Function to update the cart in localStorage and re-render the display
//    function updateCart() {
//        localStorage.setItem('cart', JSON.stringify(cart));
//        displayCart();
//    }
//
//    // Function to display cart items
//    function displayCart() {
//        const cartItemsContainer = document.getElementById('cart-items');
//        if (cartItemsContainer) {
//            if (cart.length === 0) {
//                cartItemsContainer.innerHTML = '<li>Your cart is empty.</li>';
//                return;
//            }
//
//            // Clear previous items
//            cartItemsContainer.innerHTML = '';
//
//            // Loop through each item and create list elements
//            cart.forEach((item, index) => {
//                const listItem = document.createElement('li');
//
//                // Create product image element
//                const productImage = document.createElement('img');
//                productImage.src = `images/${item.name.replace(/\s+/g, '_').toLowerCase()}.jpg`;
//                productImage.alt = item.name;
//                productImage.classList.add('product-image');
//
//                // Create product info element
//                const productInfo = document.createElement('div');
//                productInfo.classList.add('product-info');
//                productInfo.innerHTML = `${item.name} - Quantity: ${item.quantity} - Price: RS.${item.price}`;
//
//                // Create buttons to increase/decrease quantity
//                const increaseButton = document.createElement('button');
//                increaseButton.classList.add('quantity-btn');
//                increaseButton.textContent = '+';
//                increaseButton.addEventListener('click', () => {
//                    cart[index].quantity += 1;
//                    updateCart();
//                    updateCartCount(); // Update count after changing quantity
//                });
//
//                const decreaseButton = document.createElement('button');
//                decreaseButton.classList.add('quantity-btn');
//                decreaseButton.textContent = '-';
//                decreaseButton.addEventListener('click', () => {
//                    if (cart[index].quantity > 1) {
//                        cart[index].quantity -= 1;
//                    } else {
//                        cart.splice(index, 1); // Remove item if quantity is 0
//                    }
//                    updateCart();
//                    updateCartCount(); // Update count after changing quantity
//                });
//
//                // Create remove button
//                const removeButton = document.createElement('button');
//                removeButton.classList.add('remove-btn');
//                removeButton.textContent = 'Remove';
//                removeButton.addEventListener('click', () => {
//                    cart.splice(index, 1); // Remove item from cart
//                    updateCart();
//                    updateCartCount(); // Update count after removing item
//                });
//
//                // Append image, info, and buttons to list item
//                listItem.appendChild(productImage);
//                listItem.appendChild(productInfo);
//                listItem.appendChild(increaseButton);
//                listItem.appendChild(decreaseButton);
//                listItem.appendChild(removeButton);
//
//                cartItemsContainer.appendChild(listItem);
//            });
//        }
//    }
//
//    // Function to clear the cart and logout
//    function logout() {
//        localStorage.removeItem('cart');
//        localStorage.removeItem('userName');
//        alert("You have been logged out.");
//        window.location.href = "index.html";
//    }
//
//    // Event listener for logout button
//    document.addEventListener('DOMContentLoaded', function() {
//        const logoutButton = document.getElementById('logout');
//        if (logoutButton) {
//            logoutButton.addEventListener('click', logout);
//        } else {
//            console.warn("Logout button not found, no action will be taken.");
//        }
//
//        function logout() {
//            // Your logout logic here
//            console.log("Logging out...");
//        }
//    });
//
//    // Punchout XML creation function
//    function generatePunchoutXML(cart) {
//        const punchoutData = {
//            punchout_order: {
//                order_header: {
//                    user_name: document.getElementById('user-name').value,
//                    shipping_address: document.getElementById('shipping-address').value,
//                    payment_status: document.getElementById('payment-status').value
//                },
//                order_items: cart.map(item => ({
//                    product_name: item.name,
//                    quantity: item.quantity,
//                    price: item.price
//                }))
//            }
//        };
//
//        // Create the XML structure
//        const xmlString = `
//            <?xml version="1.0" encoding="UTF-8"?>
//            <punchout>
//                <order_header>
//                    <user_name>${punchoutData.punchout_order.order_header.user_name}</user_name>
//                    <shipping_address>${punchoutData.punchout_order.order_header.shipping_address}</shipping_address>
//                    <payment_status>${punchoutData.punchout_order.order_header.payment_status}</payment_status>
//                </order_header>
//                <order_items>
//                    ${punchoutData.punchout_order.order_items.map(item => `
//                        <item>
//                            <product_name>${item.product_name}</product_name>
//                            <quantity>${item.quantity}</quantity>
//                            <price>${item.price}</price>
//                        </item>
//                    `).join('')}
//                </order_items>
//            </punchout>
//        `;
//
//        // Create a Blob object and trigger download
//        const blob = new Blob([xmlString], { type: 'application/xml' });
//        const link = document.createElement('a');
//        link.href = URL.createObjectURL(blob);
//        link.download = 'punchout_order.xml';
//        link.click();
//    }
//
//    // Checkout button event listener
//    const checkoutButton = document.querySelector('.btn');
//    if (checkoutButton) {
//        checkoutButton.addEventListener('click', function(event) {
//            event.preventDefault(); // Prevent form submission
//            generatePunchoutXML(cart); // Generate and download Punchout XML file
//        });
//    }
//
//    // Call functions on page load
//    displayUserName();
//    updateCartCount();
//    displayCart();
//});




document.addEventListener('DOMContentLoaded', function () {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const users = JSON.parse(localStorage.getItem('users')) || [];
    const form = document.getElementById('form');
    const errorMessage = document.getElementById('error-message');

    // Function to add item to cart
    function addToCart(name, price) {
        const existingItem = cart.find(item => item.name === name);
        if (existingItem) {
            existingItem.quantity += 1; // Increase quantity if already in cart
        } else {
            cart.push({ name, price, quantity: 1 }); // Add new item
        }
        updateCart(); // Update localStorage and re-render the display
    }

    // Event listener for "Add to Cart" buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function () {
            const productName = this.getAttribute('data-name');
            const productPrice = parseInt(this.getAttribute('data-price'));
            addToCart(productName, productPrice); // Add product to cart
        });
    });

    // Function to calculate and display the cart count
    function updateCartCount() {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) { // Check if element exists
            let totalItems = cart.reduce((acc, item) => acc + item.quantity, 0);
            cartCountElement.textContent = totalItems;
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
                productInfo.innerHTML = `${item.name} - Quantity: ${item.quantity} - Price: RS.${item.price}`;

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

    // Punchout XML creation function
    function generatePunchoutXML(cart) {
        const punchoutData = {
            punchout_order: {
                order_header: {
                    user_name: document.getElementById('user-name').value,
                    shipping_address: document.getElementById('shipping-address').value,
                    payment_status: document.getElementById('payment-status').value
                },
                order_items: cart.map(item => ({
                    product_name: item.name,
                    quantity: item.quantity,
                    price: item.price
                }))
            }
        };

        // Create the XML structure
        const xmlString = `
            <?xml version="1.0" encoding="UTF-8"?>
            <punchout>
                <order_header>
                    <user_name>${punchoutData.punchout_order.order_header.user_name}</user_name>
                    <shipping_address>${punchoutData.punchout_order.order_header.shipping_address}</shipping_address>
                    <payment_status>${punchoutData.punchout_order.order_header.payment_status}</payment_status>
                </order_header>
                <order_items>
                    ${punchoutData.punchout_order.order_items.map(item => `
                        <item>
                            <product_name>${item.product_name}</product_name>
                            <quantity>${item.quantity}</quantity>
                            <price>${item.price}</price>
                        </item>
                    `).join('')}
                </order_items>
            </punchout>
        `;

        // Create a Blob object and trigger download
        const blob = new Blob([xmlString], { type: 'application/xml' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'punchout_order.xml';
        link.click();
        clearCart();

        // Function to clear the cart
    function clearCart() {
    localStorage.removeItem('cart'); // Clear cart in localStorage
    cart = []; // Clear cart array in memory
    updateCartCount(); // Update cart count display
    displayCart(); // Re-render the cart display to show it is empty
    console.log('Cart cleared:', localStorage); // Optional: confirm by logging
}

//        // Clear the cart after Punchout download
//        localStorage.removeItem('cart');
//        console.log(localStorage);
//        cart = []; // Empty the cart array in memory
//        updateCartCount(); // Update the cart count to zero
//        displayCart(); // Re-render the cart (empty cart message will appear)
    }

    // Checkout button event listener
    const checkoutButton = document.querySelector('.btn');
    if (checkoutButton) {
        checkoutButton.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent form submission
            generatePunchoutXML(cart); // Generate and download Punchout XML file
        });
    }

    // Call functions on page load
    displayUserName();
    updateCartCount();
    displayCart();
});

