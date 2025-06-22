from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.view_cart, name='view_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('view/', views.view_cart, name='view_cart'),
    path('thankyou/', views.thankyou, name='thankyou'), 
    
]