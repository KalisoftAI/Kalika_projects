import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from starlette.routing import Mount

# Set DJANGO_SETTINGS_MODULE before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

# Initialize Django ASGI application
django_app = get_asgi_application()

# Lazy import of FastAPI app after Django settings are configured
from fastapi_app.app import app as fastapi_app

# Create FastAPI app to mount both Django and FastAPI
application = FastAPI(
    routes=[
        Mount('/admin', app=fastapi_app),  # FastAPI at /admin/
        Mount('/', app=django_app),  # Django at /
    ]
)