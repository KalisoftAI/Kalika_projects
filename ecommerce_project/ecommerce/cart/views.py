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
    logger.info(f"Item {item_id} cart mein add kiya gaya, session_key: {session_key}")
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
            messages.success(request, 'Item cart se hata diya gaya.')
        except CartItem.DoesNotExist:
            logger.warning(f"CartItem id {item_id} session {request.session.session_key} ke liye nahi mila")
            messages.error(request, 'Item aapke cart mein nahi mila.')
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
                logger.info(f"CartItem {item_id} ki quantity {quantity} par update ki gayi.")
                updated_cart_items = CartItem.objects.filter(session_key=request.session.session_key)
                new_total = sum(item.quantity * item.product.price for item in updated_cart_items)
                return JsonResponse({'success': True, 'new_quantity': quantity, 'new_subtotal': cart_item.quantity * cart_item.product.price, 'new_total': new_total})
            else:
                cart_item.delete()
                logger.info(f"CartItem {item_id} ko hata diya gaya kyunki quantity 0 ya usse kam thi.")
                updated_cart_items = CartItem.objects.filter(session_key=request.session.session_key)
                new_total = sum(item.quantity * item.product.price for item in updated_cart_items)
                return JsonResponse({'success': True, 'removed': True, 'item_id': item_id, 'new_total': new_total})
        except CartItem.DoesNotExist:
            logger.error(f"CartItem id {item_id} session {request.session.session_key} ke liye nahi mila.")
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
        logger.info("Koi session key nahi, naya session banaya ja raha hai")
        request.session.create()
    
    session_key = request.session.session_key
    is_punchout = request.session.get('is_punchout', False)
    punchout_return_url = request.session.get('punchout_return_url', 'http://127.0.0.1:8000/punchout/response/')
    punchout_user = request.session.get('punchout_user', 'test@localhost')
    logger.info(f"Checkout access kiya gaya, method: {request.method}, session_key: {session_key}, is_punchout: {is_punchout}, "
                f"punchout_return_url: {punchout_return_url}, punchout_user: {punchout_user}")
    
    if is_punchout:
        logger.info(f"PunchOut session detect kiya gaya, PunchOut return flow ke liye redirect kiya ja raha hai.")
        return redirect('punchout:return_cart_to_ariba')  # Updated to redirect to return_cart_to_ariba

    if not request.user.is_authenticated:
        logger.info(f"User authenticated nahi hai session_key {session_key} ke liye, login par redirect kiya ja raha hai")
        return redirect('accounts:login')

    cart_items = CartItem.objects.filter(session_key=session_key)
    total = sum(item.product.price * item.quantity for item in cart_items)
    logger.info(f"Non-PunchOut checkout, session_key: {session_key}, items: {cart_items.count()}, total: {total}")
    
    if request.method == 'POST':
        logger.info(f"Checkout POST process kiya ja raha hai session_key {session_key} ke liye")
        cart_items.delete()
        logger.info(f"Checkout complete, cart clear kiya gaya session_key {session_key} ke liye")
        return redirect('cart:thankyou')  # Updated to redirect to thankyou

    logger.warning(f"checkout.html render kiya ja raha hai session_key {session_key} ke liye - PunchOut session detect nahi hua")
    return render(request, 'cart/checkout.html', {'cart_items': cart_items, 'total': total})

def thankyou(request):
    logger.info(f"Thank You page access kiya gaya session_key: {request.session.session_key} ke liye")
    return render(request, 'cart/thankyou.html')

def proceed_to_thankyou(request):
    if not request.session.session_key:
        logger.info("No session key, naya session banaya ja raha hai")
        request.session.create()
    
    session_key = request.session.session_key
    logger.info(f"Proceed to Thank You access kiya gaya, method: {request.method}, session_key: {session_key}")
    
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(session_key=session_key)
        logger.info(f"Cart clear kiya ja raha hai session_key: {session_key} ke liye, items: {cart_items.count()}")
        cart_items.delete()
        logger.info(f"Cart clear kiya gaya, thank you page par redirect kiya ja raha hai session_key: {session_key} ke liye")
        return redirect('cart:thankyou')
    
    return redirect('cart:view_cart')