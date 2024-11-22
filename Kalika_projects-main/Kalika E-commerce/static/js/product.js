document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const itemcode = urlParams.get('itemcode');

    if (itemcode) {
        fetch(`/products/${itemcode}`)
            .then(response => response.json())
            .then(product => {
                if (product.error) {
                    alert(product.error);
                    return;
                }

                document.getElementById('product-name').innerText = product.name;
                document.getElementById('product-description').innerText = product.description;
                document.getElementById('product-price').innerText = `Price: $${product.price}`;

                document.getElementById('add-to-cart').onclick = () => {
                    alert(`${product.name} added to cart!`);
                    // Logic to add product to cart can be added here.
                };
            })
            .catch(error => {
                console.error('Error fetching product details:', error);
                alert('Error fetching product details');
            });
    } else {
        alert("No item code provided.");
    }
});