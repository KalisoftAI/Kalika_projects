# punchout/urls.py
from django.urls import path
from . import views

app_name = 'punchout'
urlpatterns = [
    path('setup/', views.punchout_setup, name='punchout_setup'),
    path('return/', views.return_cart_to_ariba, name='return_cart_to_ariba'),
]