from .models import Product
from cart.models import CartItem
def categories(request):
    main_categories = Product.objects.values('main_category').distinct().exclude(main_category='')
    category_dict = {}
    for main_cat in main_categories:
        main_category_name = main_cat['main_category']
        subcategories = Product.objects.filter(main_category=main_category_name).values('sub_categories').distinct().exclude(sub_categories__in=['', None])
        category_dict[main_category_name] = {
            'subcategories': [{'name': sub['sub_categories']} for sub in subcategories]
        }
    return {'categories': category_dict}

def cart_item_count(request):
    # Ensure session_key exists
    if not request.session.session_key:
        request.session.create()
    
    # Calculate total quantity of items in the cart
    cart_items = CartItem.objects.filter(session_key=request.session.session_key)
    total_quantity = sum(item.quantity for item in cart_items)
    
    return {
        'cart_item_count': total_quantity
    }