import os
from django.core.asgi import get_asgi_application
from django.conf import settings
from fastapi import FastAPI
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

# Set the settings module for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

# Get the default Django ASGI application
django_app = get_asgi_application()

# Import the FastAPI app
from fastapi_app.app import app as fastapi_app

# Define the final application that will run under Uvicorn
application = FastAPI(
    routes=[
        # Mount the FastAPI admin panel at /admin
        Mount('/admin', app=fastapi_app),

        # Mount the collected Django static files at /static.
        # This tells Uvicorn to serve files from your STATIC_ROOT directory.
        Mount(settings.STATIC_URL, app=StaticFiles(directory=settings.STATIC_ROOT), name="static"),

        # Mount the main Django application at the root.
        # This MUST come after the static files mount.
        Mount('/', app=django_app),
    ]
)