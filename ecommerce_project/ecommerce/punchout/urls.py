from django.urls import path
from . import views

app_name = 'punchout'
urlpatterns = [
    path('setup/', views.punchout_setup, name='punchout_setup'),
    path('return/', views.return_cart_to_ariba, name='return_to_ariba'),
    path('test-session/', views.test_punchout_session, name='test_punchout_session'),
    path('debug-session/', views.debug_session, name='debug_session'),
    path('response/', views.punchout_response, name='punchout_response'),
]