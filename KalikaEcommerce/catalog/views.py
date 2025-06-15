from django.shortcuts import render
from .models import Product
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

def home(request):
    try:
        products = Product.objects.all()[:12]
        logger.debug(f"Home view fetched {products.count()} products")
        return render(request, 'catalog/home.html', {'products': products})
    except Exception as e:
        logger.error(f"Error in home view: {e}")
        return render(request, 'catalog/home.html', {'products': []})

def products_by_category(request, main_category_name):
    try:
        products = Product.objects.filter(main_category=main_category_name)
        logger.debug(f"Category '{main_category_name}' fetched {products.count()} products")
        return render(request, 'catalog/products_by_category.html', {
            'products': products,
            'category': main_category_name
        })
    except Exception as e:
        logger.error(f"Error in products_by_category view: {e}")
        return render(request, 'catalog/products_by_category.html', {
            'products': [],
            'category': main_category_name
        })

def products_by_subcategory(request, main_category_name, sub_category_name):
    try:
        products = Product.objects.filter(
            main_category=main_category_name,
            sub_categories=sub_category_name
        )
        logger.debug(f"Subcategory '{sub_category_name}' in '{main_category_name}' fetched {products.count()} products")
        return render(request, 'catalog/products_by_subcategory.html', {
            'products': products,
            'category': main_category_name,
            'subcategory': sub_category_name
        })
    except Exception as e:
        logger.error(f"Error in products_by_subcategory view: {e}")
        return render(request, 'catalog/products_by_subcategory.html', {
            'products': [],
            'category': main_category_name,
            'subcategory': sub_category_name
        })

def search_products(request):
    try:
        query = request.GET.get('query', '')
        products = Product.objects.filter(
            Q(product_title__icontains=query) | Q(product_description__icontains=query)
        )[:12]
        logger.debug(f"Search query '{query}' fetched {products.count()} products")
        return render(request, 'catalog/home.html', {'products': products, 'query': query})
    except Exception as e:
        logger.error(f"Error in search_products view: {e}")
        return render(request, 'catalog/home.html', {'products': [], 'query': query})