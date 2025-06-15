import logging
from .models import Product
from django.db.models import Q
from urllib.parse import quote

logger = logging.getLogger(__name__)

def categories(request):
    try:
        logger.debug("Fetching categories for context processor")
        main_categories = Product.objects.filter(
            main_category__isnull=False, main_category__gt=''
        ).values('main_category').distinct()
        categories_dict = {}
        
        for main_cat in main_categories:
            main_cat_name = main_cat['main_category'].strip()
            # URL-safe key: replace '/' with '-' and URL-encode
            main_cat_key = quote(main_cat_name.replace('/', '-'))
            sub_cats = Product.objects.filter(
                main_category=main_cat_name,
                sub_categories__isnull=False,
                sub_categories__gt=''
            ).values('sub_categories').distinct()
            sub_cats_list = [
                {
                    'name': sc['sub_categories'].strip(),
                    'key': quote(sc['sub_categories'].strip().replace('/', '-'))
                } for sc in sub_cats
            ]
            if sub_cats_list:
                categories_dict[main_cat_name] = {
                    'key': main_cat_key,
                    'subcategories': sub_cats_list
                }
            logger.debug(f"Main: {main_cat_name} (key: {main_cat_key}), Sub: {[sc['name'] for sc in sub_cats_list]}")
        
        logger.debug(f"Categories dictionary: {categories_dict}")
        return {'categories': categories_dict}
    except Exception as e:
        logger.error(f"Error in categories context processor: {e}")
        return {'categories': {}}