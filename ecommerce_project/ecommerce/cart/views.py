from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem
from catalog.models import Product
from django.http import JsonResponse
import json
import logging
from catalog.views import get_s3_presigned_url
from django.conf import settings
from django.contrib import messages

logger = logging.getLogger(__name__)

def add_to_cart(request, item_id):
    """
    Adds a product to the cart. If the request is an AJAX request, it returns a
    JSON response indicating success. Otherwise, it redirects to the cart view.
    """
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

    logger.info(f"Item {item_id} added to cart for session_key: {session_key}")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Product added to cart successfully.'})

    return redirect('cart:view_cart')

def view_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)
    total = sum(item.quantity * item.product.price for item in cart_items)
    for item in cart_items:
        item.subtotal = item.quantity * item.product.price
        item.product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, item.product.image_url) if item.product.image_url else None
        logger.debug(f"Cart item {item.id}: s3_image_url = {item.product.s3_image_url}")
    return render(request, 'cart/view_cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def remove_from_cart(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(id=item_id, session_key=request.session.session_key)
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
        except CartItem.DoesNotExist:
            logger.warning(f"CartItem id {item_id} not found for session {request.session.session_key}")
            messages.error(request, 'Item not found in your cart.')
        return redirect('cart:view_cart')
    return redirect('cart:view_cart')



def update_cart_quantity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = data.get('quantity')

            cart_item = CartItem.objects.get(id=item_id, session_key=request.session.session_key)

            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                logger.info(f"Updated quantity for CartItem {item_id} to {quantity}.")
                updated_cart_items = CartItem.objects.filter(session_key=request.session.session_key)
                new_total = sum(item.quantity * item.product.price for item in updated_cart_items)
                return JsonResponse({'success': True, 'new_quantity': quantity, 'new_subtotal': cart_item.quantity * cart_item.product.price, 'new_total': new_total})
            else:
                cart_item.delete()
                logger.info(f"Removed CartItem {item_id} as quantity was 0 or less.")
                updated_cart_items = CartItem.objects.filter(session_key=request.session.session_key)
                new_total = sum(item.quantity * item.product.price for item in updated_cart_items)
                return JsonResponse({'success': True, 'removed': True, 'item_id': item_id, 'new_total': new_total})
        except CartItem.DoesNotExist:
            logger.error(f"CartItem id {item_id} not found for session {request.session.session_key}.")
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
        except json.JSONDecodeError:
            logger.error("JSON decode error in update_cart_quantity.")
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def checkout(request):
    if not request.session.session_key:
        logger.info("No session key, creating a new one.")
        request.session.create()

    session_key = request.session.session_key
    is_punchout = request.session.get('is_punchout', False)
    punchout_return_url = request.session.get('punchout_return_url', 'http://127.0.0.1:8000/punchout/response/')
    punchout_user = request.session.get('punchout_user', 'test@localhost')
    logger.info(f"Checkout accessed with method: {request.method}, session_key: {session_key}, is_punchout: {is_punchout}, "
                f"punchout_return_url: {punchout_return_url}, punchout_user: {punchout_user}")

    if is_punchout:
        logger.info(f"PunchOut session detected, redirecting to PunchOut return flow.")
        return redirect('punchout:return_cart_to_ariba')

    if not request.user.is_authenticated:
        logger.info(f"User not authenticated for session_key {session_key}, redirecting to login.")
        return redirect('accounts:login')

    cart_items = CartItem.objects.filter(session_key=session_key)
    total = 0 # Initialize total

    # --- THIS LOOP IS NOW CORRECTED ---
    # It now calculates the subtotal AND generates the S3 image URL for each item.
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal
        
        # This line generates the image URL
        if item.product.image_url:
            item.product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, item.product.image_url)
        else:
            item.product.s3_image_url = None
    # --- END OF CORRECTED LOOP ---

    logger.info(f"Non-PunchOut checkout for session_key: {session_key}, items: {cart_items.count()}, total: {total}")

    if request.method == 'POST':
        logger.info(f"Processing checkout POST for session_key {session_key}")
        cart_items.delete()
        logger.info(f"Checkout complete, cart cleared for session_key {session_key}")
        return redirect('cart:thankyou')

    logger.warning(f"Rendering checkout.html for session_key {session_key} - PunchOut session not detected.")
    return render(request, 'cart/checkout.html', {'cart_items': cart_items, 'total': total})

def thankyou(request):
    logger.info(f"Thank You page accessed for session_key: {request.session.session_key}")
    return render(request, 'cart/thankyou.html')

def proceed_to_thankyou(request):
    if not request.session.session_key:
        logger.info("No session key, creating a new one.")
        request.session.create()

    session_key = request.session.session_key
    logger.info(f"Proceed to Thank You accessed with method: {request.method}, session_key: {session_key}")

    if request.method == 'POST':
        cart_items = CartItem.objects.filter(session_key=session_key)
        logger.info(f"Clearing cart for session_key: {session_key}, items: {cart_items.count()}")
        cart_items.delete()
        logger.info(f"Cart cleared, redirecting to thank you page for session_key: {session_key}")
        return redirect('cart:thankyou')

    return redirect('cart:view_cart')