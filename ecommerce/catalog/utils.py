import boto3
from django.conf import settings
from django.db.models import Q
from .models import Product

DEFINED_MAIN_CATEGORIES = [
    "safety", "janitorial", "packaging", "facility maintenance",
    "chemicals & lubricants", "abrasives", "adhesives, sealants & tape",
    "hand & power tools", "pneumatics", "cutting tools", "welding tools",
    "measuring instruments & tools", "mechanical power transmission",
    "accessories", "stationery", "appliances and utilities", "wave project",
    "plastic bags", "ptfe hose ctci",
]
SUB_CATEGORY_BLOCKLIST = ["home", "system", "menu1", "shop", ""]

def add_s3_urls_to_products(products):
    """
    Add S3 presigned URLs to products for image access.
    Assumes products have an 'image_url' field from the database.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    for product in products:
        if product.image_url:
            try:
                # Assuming image_url is a path like 'images/product.jpg'
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                key = product.image_url
                product.s3_image_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': key},
                    ExpiresIn=3600  # URL valid for 1 hour
                )
            except Exception as e:
                product.s3_image_url = None
        else:
            product.s3_image_url = None
    return products

def build_category_context():
    """
    Build category structure for templates.
    Moved from context_processors.py to avoid redundancy.
    """
    category_structure = {main_cat: {'subcategories': {}, 'product_count': 0} for main_cat in DEFINED_MAIN_CATEGORIES}

    products_for_categories = Product.objects.filter(
        main_category__in=DEFINED_MAIN_CATEGORIES
    ).exclude(
        Q(sub_categories__isnull=True) | Q(sub_categories__exact='') | Q(sub_categories__in=SUB_CATEGORY_BLOCKLIST)
    ).values('main_category', 'sub_categories').distinct().order_by('main_category', 'sub_categories')

    for main_cat in DEFINED_MAIN_CATEGORIES:
        category_structure[main_cat]['product_count'] = Product.objects.filter(main_category__iexact=main_cat).count()
        subcategories = Product.objects.filter(main_category__iexact=main_cat).exclude(
            Q(sub_categories__isnull=True) | Q(sub_categories__exact='') | Q(sub_categories__in=SUB_CATEGORY_BLOCKLIST)
        ).values('sub_categories').distinct()
        for sub_cat in subcategories:
            sub_cat_name = sub_cat['sub_categories'].strip().lower()
            product_count = Product.objects.filter(main_category__iexact=main_cat, sub_categories__contains=sub_cat_name).count()
            category_structure[main_cat]['subcategories'][sub_cat_name] = {'name': sub_cat_name, 'product_count': product_count}

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

    return final_categories_data