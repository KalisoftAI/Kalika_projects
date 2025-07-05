import time
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.db.models import Q
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging
from cart.models import CartItem

logger = logging.getLogger(__name__)

# This is the master list of main categories that will appear in your menu.
DEFINED_MAIN_CATEGORIES = [
    "Safety", "Janitorial", "Packaging", "Facility Maintenance",
    "Chemicals & Lubricants", "Abrasives", "Adhesives, Sealants & Tape",
    "Hand & Power Tools", "Pneumatics", "Cutting Tools", "Welding Tools",
    "Measuring Instruments & Tools", "Mechanical Power Transmission",
    "ACCESSORIES", "STATIONERY", "Appliances And Utilities", "WAVE PROJECT",
    "Plastic Bags", "PTFE HOSE CTCI",
]

# This is a blocklist to filter out unwanted sub-category names.
SUB_CATEGORY_BLOCKLIST = ["home", "system", "menu1", "shop", ""]

def build_category_context():
    """
    Builds the nested dictionary for the header menu.
    This new version is much more efficient, using a single database query.
    """
    category_structure = {main_cat: {'subcategories': {}, 'product_count': 0} for main_cat in DEFINED_MAIN_CATEGORIES}

    # Fetch all relevant product fields in a single query
    products_for_categories = Product.objects.filter(
        main_category__in=DEFINED_MAIN_CATEGORIES
    ).exclude(
        Q(sub_categories__isnull=True) | Q(sub_categories__exact='') | Q(sub_categories__in=SUB_CATEGORY_BLOCKLIST)
    ).values('main_category', 'sub_categories').distinct().order_by('main_category', 'sub_categories')

    # Count products per main category and subcategory
    for main_cat in DEFINED_MAIN_CATEGORIES:
        category_structure[main_cat]['product_count'] = Product.objects.filter(main_category=main_cat).count()
        subcategories = Product.objects.filter(main_category=main_cat).exclude(
            Q(sub_categories__isnull=True) | Q(sub_categories__exact='') | Q(sub_categories__in=SUB_CATEGORY_BLOCKLIST)
        ).values('sub_categories').distinct()
        for sub_cat in subcategories:
            sub_cat_name = sub_cat['sub_categories']
            product_count = Product.objects.filter(main_category=main_cat, sub_categories=sub_cat_name).count()
            category_structure[main_cat]['subcategories'][sub_cat_name] = {'name': sub_cat_name, 'product_count': product_count}

    # Convert to final format
    final_categories_data = {}
    for main_cat in DEFINED_MAIN_CATEGORIES:
        if main_cat in category_structure:
            subcategories_list = sorted([
                sub_data for sub_key, sub_data in category_structure[main_cat]['subcategories'].items()
            ], key=lambda x: x['name'])
            final_categories_data[main_cat] = {
                'subcategories': subcategories_list,
                'product_count': category_structure[main_cat]['product_count']
            }

    # Limit to first 10 main categories for dropdown
    limited_categories = dict(list(final_categories_data.items())[:10])
    return limited_categories

def get_s3_presigned_url(bucket_name, object_key, expiration=3600):
    try:
        object_key = object_key.lstrip('/')
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )
    except ClientError as e:
        logger.error(f"Error generating pre-signed URL for {object_key}: {e}")
        return None

def add_s3_urls_to_products(products):
    for product in products:
        if product.image_url:
            image_key = product.image_url.lstrip('/')
            product.s3_image_url = get_s3_presigned_url(
                settings.AWS_S3_BUCKET_NAME,
                image_key
            )
        else:
            product.s3_image_url = None
    return products

def home(request):
    # Fetch products for various categories dynamically
    products_by_category = {}
    current_minute = int(time.time() // 60)
    for category in DEFINED_MAIN_CATEGORIES:
        # MODIFICATION: Changed to a case-insensitive "contains" filter for more reliability.
        all_products = Product.objects.filter(
            main_category__icontains=category.split(" ")[0]
        ).exclude(image_url__icontains='noimage.jpg')
        
        total = all_products.count()
        offset = ((current_minute // 9) * 9) % max(1, total)  # avoid division by zero
        if total <= 10:
            products = all_products
        else:
            end = offset + 10
            if end <= total:
                products = all_products[offset:end]
            else:
                products = list(all_products[offset:]) + list(all_products[:end - total])
        products_by_category[category] = add_s3_urls_to_products(products)

    # Generate presigned URL for the video
    video_key = '/kalika-images/kalika-ad1.mp4'  # Replace with your actual S3 video key
    video_url = get_s3_presigned_url(
        bucket_name=settings.AWS_S3_BUCKET_NAME,
        object_key=video_key,
        expiration=3600  # URL valid for 1 hour
    )

    context = {
        'products_by_category': products_by_category,
        'featured_products': products_by_category.get("Hand & Power Tools", [])[:10],
        'categories': build_category_context(),
        'hero_video_url': video_url,
    }
    return render(request, 'catalog/home.html', context)

def product_list(request):
    products = Product.objects.all()
    products_with_urls = add_s3_urls_to_products(products)

    context = {
        'products': products_with_urls,
        'categories': build_category_context()
    }
    return render(request, 'catalog/product_list.html', context)

def product_detail(request, item_id):
    product = get_object_or_404(Product, item_id=item_id)
    if product.image_url:
        product.s3_image_url = get_s3_presigned_url(settings.AWS_S3_BUCKET_NAME, product.image_url.lstrip('/'))
    else:
        product.s3_image_url = None

    context = {
        'product': product,
        'categories': build_category_context()
    }
    return render(request, 'catalog/product_detail.html', context)

def products_by_category(request, main_category_name):
    products = Product.objects.filter(main_category=main_category_name)
    products_with_urls = add_s3_urls_to_products(products)

    context = {
        'main_category': main_category_name,
        'products': products_with_urls,
        'categories': build_category_context()
    }
    return render(request, 'catalog/products_by_category.html', context)

def products_by_subcategory(request, main_category_name, sub_category_name):
    products = Product.objects.filter(main_category=main_category_name, sub_categories__icontains=sub_category_name)
    products_with_urls = add_s3_urls_to_products(products)

    context = {
        'main_category': main_category_name,
        'sub_category': sub_category_name,
        'products': products_with_urls,
        'categories': build_category_context()
    }
    return render(request, 'catalog/products_by_subcategory.html', context)

def all_categories(request):
    categories_data = {}
    main_categories_queryset = (
        Product.objects
        .values_list('main_category', flat=True)
        .distinct()
        .exclude(main_category__isnull=True)
        .exclude(main_category__exact='')
        .order_by('main_category')
    )

    for main_cat in main_categories_queryset:
        subcategories_queryset = (
            Product.objects
            .filter(main_category=main_cat)
            .values_list('sub_categories', flat=True)
            .distinct()
            .exclude(sub_categories__isnull=True)
            .exclude(sub_categories__exact='')
            .exclude(sub_categories__in=SUB_CATEGORY_BLOCKLIST)
            .order_by('sub_categories')
        )
        subcategories_list = [{'name': sub_cat_name} for sub_cat_name in subcategories_queryset]
        if subcategories_list:
            categories_data[main_cat] = {'subcategories': subcategories_list}
    context = {
        'categories': categories_data,
        'categories_menu': build_category_context()
    }
    return render(request, 'catalog/all_categories.html', context)

def search_products(request):
    query = request.GET.get('query', '').strip()
    products = []
    if query:  # Only perform query if non-empty
        products = Product.objects.filter(
            Q(product_title__icontains=query) |
            Q(main_category__icontains=query) |
            Q(sub_categories__icontains=query)
        ).exclude(
            Q(sub_categories__in=SUB_CATEGORY_BLOCKLIST) |
            Q(main_category__isnull=True) |
            Q(main_category__exact='')
        ).distinct()[:12]
    products_with_urls = add_s3_urls_to_products(products)

    context = {
        'products': products_with_urls,
        'query': query,
        'categories': build_category_context()
    }
    return render(request, 'catalog/search_results.html', context)