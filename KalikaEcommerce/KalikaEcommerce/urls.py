from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
    path('cart/', include('cart.urls')),
    path('auth/', include('authentication.urls')),
    path('checkout/', include('checkout.urls')),
    path('punchout/', include('punchout.urls', namespace='punchout')),
    path('catalog/', include('catalog.urls', namespace='catalog')),
]