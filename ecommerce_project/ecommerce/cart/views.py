from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem
from catalog.models import Product
from django.http import JsonResponse
import json
import logging

logger = logging.getLogger(__name__)

def add_to_cart(request, item_id):
    product = get_object_or_404(Product, item_id=item_id)
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart_item, created = CartItem.objects.get_or_create(
        session_key=session_key,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    logger.info(f"Added item {item_id} to cart, session_key: {session_key}")
    return redirect('cart:view_cart')

def view_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)
    total = sum(item.product.price * item.quantity for item in cart_items)
    # Calculate item-wise total
    cart_items_with_total = [
        {
            'product': item.product,
            'quantity': item.quantity,
            'item_total': item.product.price * item.quantity
        }
        for item in cart_items
    ]
    logger.info(f"Viewing cart, session_key: {session_key}, items: {cart_items.count()}, total: {total}")
    return render(request, 'catalog/cart.html', {
        'cart_items': cart_items_with_total,
        'total': total
    })

def remove_from_cart(request, item_id):
    if not request.session.session_key:
        logger.info("No session key, redirecting to view_cart")
        return redirect('cart:view_cart')
    session_key = request.session.session_key
    cart_item = get_object_or_404(CartItem, session_key=session_key, product__item_id=item_id)
    cart_item.delete()
    logger.info(f"Removed item {item_id} from cart, session_key: {session_key}")
    return redirect('cart:view_cart')

def checkout(request):
    if not request.session.session_key:
        logger.info("No session key, creating new session")
        request.session.create()
    
    session_key = request.session.session_key
    is_punchout = request.session.get('is_punchout', False)
    punchout_return_url = request.session.get('punchout_return_url', 'http://127.0.0.1:8000/punchout/response/')
    punchout_user = request.session.get('punchout_user', 'test@localhost')
    logger.info(f"Checkout accessed, method: {request.method}, session_key: {session_key}, is_punchout: {is_punchout}, "
                f"punchout_return_url: {punchout_return_url}, punchout_user: {punchout_user}")
    
    if is_punchout:
        logger.info(f"PunchOut session detected, redirecting to punchout:return_to_ariba for session_key {session_key}")
        return redirect('punchout:return_to_ariba')
    
    if not request.user.is_authenticated:
        logger.info(f"User not authenticated for session_key {session_key}, redirecting to login")
        return redirect('login')  # Replace with your actual login URL name
    
    cart_items = CartItem.objects.filter(session_key=session_key)
    total = sum(item.product.price * item.quantity for item in cart_items)
    logger.info(f"Non-PunchOut checkout, session_key: {session_key}, items: {cart_items.count()}, total: {total}")
    
    if request.method == 'POST':
        logger.info(f"Processing checkout POST for session_key {session_key}")
        # Placeholder for order insertion (dbtest2 is missing)
        # from dbtest2 import insert_order
        # insert_order(
        #     user_id=request.user.id,
        #     total_amount=float(total),
        #     status='Pending',
        #     shipping_address=request.POST.get('shipping_address', '1234 Elm St'),
        #     payment_status='Unpaid'
        # )
        logger.warning("Order insertion skipped due to missing dbtest2 module")
        cart_items.delete()
        logger.info(f"Checkout completed, cart cleared for session_key {session_key}")
        return redirect('catalog:home')  # Replace with your home URL name
    
    logger.warning(f"Rendering checkout.html for session_key {session_key} - PunchOut session not detected")
    return render(request, 'catalog/checkout.html', {'cart_items': cart_items, 'total': total})

def thankyou(request):
    logger.info(f"Thank You page accessed for session_key: {request.session.session_key}")
    return render(request, 'cart/thankyou.html')