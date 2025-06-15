from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from cart.models import CartItem

@login_required
def checkout(request):
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.subtotal() for item in cart_items)
        
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            shipping_address=shipping_address,
            status='Pending',
            payment_status='Unpaid'
        )
        
        cart_items.delete()
        return redirect('catalog:home')
    
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'checkout/checkout.html', {'cart_items': cart_items, 'total': total})