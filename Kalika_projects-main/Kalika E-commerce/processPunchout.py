<?php
// Read the JSON input (sent from the checkout button)
$input = file_get_contents('php://input');
$cartData = json_decode($input, true);

// Ensure data is valid
if (!isset($cartData['cartItems']) || !isset($cartData['totalAmount'])) {
    echo json_encode(['success' => false, 'message' => 'Invalid cart data.']);
    exit;
}

// Extract cart data
$cartItems = $cartData['cartItems'];
$totalAmount = $cartData['totalAmount'];

// Prepare cXML PunchOutOrderMessage
$buyerCookie = '123456';  // Unique identifier for the PunchOut session
$punchoutOrderMessage = "<PunchOutOrderMessage>
    <BuyerCookie>{$buyerCookie}</BuyerCookie>
    <PunchOutOrderMessageHeader>
        <Total>
            <Money currency=\"INR\">{$totalAmount}</Money>
        </Total>
    </PunchOutOrderMessageHeader>";

foreach ($cartItems as $item) {
    $punchoutOrderMessage .= "<ItemIn quantity=\"{$item['quantity']}\">
        <ItemID>
            <SupplierPartID>{$item['name']}</SupplierPartID>
        </ItemID>
        <ItemDetail>
            <UnitPrice>
                <Money currency=\"INR\">{$item['price']}</Money>
            </UnitPrice>
        </ItemDetail>
    </ItemIn>";
}

$punchoutOrderMessage .= "</PunchOutOrderMessage>";

// Simulate sending the PunchOutOrderMessage (for demo, we just log or save it)
file_put_contents('punchout_order.xml', $punchoutOrderMessage); // Save to a file (or send to a server)

// Respond back with a success message
echo json_encode([
    'success' => true,
    'redirectURL' => 'thankyou.html' // Redirect to a thank-you page
]);
?>