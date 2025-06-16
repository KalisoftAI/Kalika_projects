from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import CartItem
from catalog.models import Product
from django.contrib.auth.decorators import login_required

def get_cart_items(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return CartItem.objects.filter(session_key=session_key)

def cart(request):
    cart_items = get_cart_items(request)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total': total})


# def add_to_cart(request, item_id):
#     product = get_object_or_404(Product, item_id=item_id)
#     if request.user.is_authenticated:
#         cart_item, created = CartItem.objects.get_or_create(
#             user=request.user,
#             product=product,
#             defaults={'quantity': 1}
#         )
#     else:
#         session_key = request.session.session_key
#         if not session_key:
#             request.session.create()
#             session_key = request.session.session_key
#         cart_item, created = CartItem.objects.get_or_create(
#             session_key=session_key,
#             product=product,
#             defaults={'quantity': 1}
#         )
#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()
#     return redirect('cart:cart')

# --- THIS IS THE MODIFIED VIEW FOR PUNCHOUT ---
def add_to_cart(request, item_id):
    product = get_object_or_404(Product, item_id=item_id)  # Using Item_id to match your model

    # Use your existing logic to get or create the cart item
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )
    else:
        session_key = request.session.session_key
        if not session_key:
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

    # --- THIS IS THE NEW LOGIC ---
    # Check if this is a PunchOut session.
    if request.session.get('is_punchout', False):
        # If it is, redirect back to the product list to continue shopping.
        return redirect('catalog:product-list')
    else:
        # Otherwise, use your original flow for regular customers.
        return redirect('cart:cart')

def cart_count(request):
    cart_items = get_cart_items(request)
    count = sum(item.quantity for item in cart_items)
    return JsonResponse({'count': count})

def product_list(request):
    products = Product.objects.all()

    # Get cart item count using your session logic
    cart_item_count = 0
    if request.user.is_authenticated:
        cart_item_count = sum(item.quantity for item in CartItem.objects.filter(user=request.user))
    else:
        session_key = request.session.session_key
        if session_key:
            cart_item_count = sum(item.quantity for item in CartItem.objects.filter(session_key=session_key))

    context = {
        'products': products,
        'cart_item_count': cart_item_count, # Pass the count to the template
    }
    # IMPORTANT: Make sure this renders your existing home.html
    return render(request, 'catalog/home.html', context)