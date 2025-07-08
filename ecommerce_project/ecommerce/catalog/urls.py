# from django.urls import path
# from . import views

# app_name = 'catalog'
# urlpatterns = [
#     path('', views.home, name='home'),
#     path('products/', views.product_list, name='product_list'),
#     path('product/<int:item_id>/', views.product_detail, name='product_detail'),
#     path('category/<path:main_category_name>/', views.products_by_category, name='products_by_category'),
#     path('category/<path:main_category_name>/<path:sub_category_name>/', views.products_by_subcategory, name='products_by_subcategory'),
#     path('categories/', views.all_categories, name='all_categories'),
#     path('search/', views.search_products, name='search_products'),
# ]

from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:item_id>/', views.product_detail, name='product_detail'),

    # CORRECTED: Switched back to <path:...> to allow slashes in category names.
    # The order remains the same: most specific URL comes first.
    path('category/<path:main_category_name>/<path:sub_category_name>/', views.products_by_subcategory, name='products_by_subcategory'),
    path('category/<path:main_category_name>/', views.products_by_category, name='products_by_category'),

    path('categories/', views.all_categories, name='all_categories'),
    path('search/', views.search_products, name='search_products'),
]