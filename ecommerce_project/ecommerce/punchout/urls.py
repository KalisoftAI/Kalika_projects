from django.urls import path
from . import views

app_name = 'punchout'
urlpatterns = [
    path('setup/', views.punchout_setup, name='punchout_setup'),
    path('response/', views.return_cart_to_ariba, name='return_cart_to_ariba'),
    path('debug/', views.show_punchout_debug, name='show_punchout_debug'),
]