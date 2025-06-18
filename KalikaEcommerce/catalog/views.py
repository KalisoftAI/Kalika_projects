from django.shortcuts import render
from .models import Product
from django.db.models import Q
import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)

def get_s3_presigned_url(bucket_name, object_key, expiration=3600):
    """Generate a pre-signed URL for an S3 object."""
    try:
        # Remove leading slash from object_key if present
        object_key = object_key.lstrip('/')
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )
        logger.debug(f"Generated pre-signed URL for {object_key}")
        return url
    except ClientError as e:
        logger.error(f"Error generating pre-signed URL for {object_key}: {e}")
        return None

def home(request):
    try:
        products = Product.objects.all()[:12]
        # Add pre-signed URLs to each product
        for product in products:
            if product.image_url:
                product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url)
            else:
                product.s3_image_url = None
        logger.debug(f"Home view fetched {products.count()} products")
        return render(request, 'catalog/home.html', {'products': products})
    except Exception as e:
        logger.error(f"Error in home view: {e}")
        return render(request, 'catalog/home.html', {'products': []})

def products_by_category(request, main_category_name):
    try:
        products = Product.objects.filter(main_category=main_category_name)
        # Add pre-signed URLs to each product
        for product in products:
            if product.image_url:
                product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url)
            else:
                product.s3_image_url = None
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
        # Add pre-signed URLs to each product
        for product in products:
            if product.image_url:
                product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url)
            else:
                product.s3_image_url = None
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
        # Add pre-signed URLs to each product
        for product in products:
            if product.image_url:
                product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url)
            else:
                product.s3_image_url = None
        logger.debug(f"Search query '{query}' fetched {products.count()} products")
        return render(request, 'catalog/home.html', {'products': products, 'query': query})
    except Exception as e:
        logger.error(f"Error in search_products view: {e}")
        return render(request, 'catalog/home.html', {'products': [], 'query': query})

def product_list(request):
    try:
        products = Product.objects.all()
        # Add pre-signed URLs to each product
        for product in products:
            if product.image_url:
                product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url)
            else:
                product.s3_image_url = None
        cart_items = []
        if request.session.session_key:
            from cart.models import CartItem
            cart_items = CartItem.objects.filter(session_key=request.session.session_key)
        context = {
            'products': products,
            'cart_item_count': sum(item.quantity for item in cart_items)
        }
        logger.debug(f"Product list view fetched {products.count()} products")
        return render(request, 'catalog/product_list.html', context)
    except Exception as e:
        logger.error(f"Error in product_list view: {e}")
        return render(request, 'catalog/product_list.html', {'products': [], 'cart_item_count': 0})