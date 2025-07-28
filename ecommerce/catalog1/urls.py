from django.urls import path
from . import views

app_name = 'catalog'
urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:item_id>/', views.product_detail, name='product_detail'),
    path('category/<path:main_category_name>/', views.products_by_category, name='products_by_category'),
    path('category/<path:main_category_name>/<path:sub_category_name>/', views.products_by_subcategory, name='products_by_subcategory'),
    path('search/', views.search_products, name='search_products'),
]