# punchout/urls.py
from django.urls import path
from . import views

app_name = 'punchout' # App ka naam Punchout rakhein

urlpatterns = [
    path('order/', views.generate_punchout_order_cxml, name='generate_punchout_order_cxml'),
    path('debug/', views.show_punchout_debug, name='show_punchout_debug'),
    # Agar aap Punchout setup request ko bhi handle karna chahte hain, to isko uncomment karein
    # path('setup/', views.punchout_setup_request, name='punchout_setup_request'),
    # Note: Punchout return URL ko bhi yahan define karna padega agar aap use handle kar rahe hain.
    # path('punchout-return/', views.handle_punchout_return, name='punchout_return'),
]