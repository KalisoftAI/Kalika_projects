from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from django.db.models import Q
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging
from cart.models import CartItem
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
logger = logging.getLogger(__name__)

def get_s3_presigned_url(bucket_name, object_key, expiration=3600):
    try:
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
        return url
    except ClientError as e:
        logger.error(f"Error generating pre-signed URL for {object_key}: {e}")
        return None

def home(request):
    products = Product.objects.all()[:12]
    for product in products:
        product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url) if product.image_url else None
    return render(request, 'catalog/home.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    cart_items = CartItem.objects.filter(session_key=request.session.session_key) if request.session.session_key else []
    for product in products:
        product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url) if product.image_url else None
    return render(request, 'catalog/product_list.html', {
        'products': products,
        'cart_item_count': sum(item.quantity for item in cart_items)
    })

def product_detail(request, item_id):
    product = get_object_or_404(Product, item_id=item_id)
    product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url) if product.image_url else None
    return render(request, 'catalog/product_detail.html', {'product': product})

def products_by_category(request, main_category_name):
    try:
        products = Product.objects.filter(main_category=main_category_name)
        for product in products:
            product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url) if product.image_url else None
        return render(request, 'catalog/products_by_category.html', {
            'main_category': main_category_name,
            'products': products
        })
    except ObjectDoesNotExist:
        return render(request, 'catalog/products_by_category.html', {
            'main_category': main_category_name,
            'products': []
        })

def products_by_subcategory(request, main_category_name, sub_category_name):
    try:
        products = Product.objects.filter(main_category=main_category_name, sub_categories=sub_category_name)
        return render(request, 'catalog/products_by_subcategory.html', {
            'main_category': main_category_name,
            'sub_category': sub_category_name,
            'products': products
        })
    except ObjectDoesNotExist:
        return render(request, 'catalog/products_by_subcategory.html', {
            'main_category': main_category_name,
            'sub_category': sub_category_name,
            'products': []
        })

def search_products(request):
    query = request.GET.get('query', '')
    products = Product.objects.filter(
        Q(product_title__icontains=query) | Q(product_description__icontains=query)
    )[:12]
    for product in products:
        product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url) if product.image_url else None
    return render(request, 'catalog/home.html', {'products': products, 'query': query})