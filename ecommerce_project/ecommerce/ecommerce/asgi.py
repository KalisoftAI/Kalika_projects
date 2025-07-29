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

# import os
# from django.core.asgi import get_asgi_application
# from fastapi.staticfiles import StaticFiles
# # Make sure the import path is correct for your project structure
# # import sys

# # # Add your project base directory to sys.path
# # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # PARENT_DIR = os.path.dirname(BASE_DIR)
# # if PARENT_DIR not in sys.path:
# #     sys.path.insert(0, PARENT_DIR)

# from fastapi_app.main import app as fastapi_app

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

# # This is the standard Django ASGI application
# django_app = get_asgi_application()

# # This is your FastAPI app instance
# # Mount the FastAPI app at the /admin path.
# # IMPORTANT: This line makes all FastAPI routes available under /admin
# application = fastapi_app
# application.mount("/admin", django_app)

# # This line is for serving FastAPI's own static files if needed
# # The path "/admin-static" must match what's in your FastAPI app.mount()
# application.mount("/admin-static", StaticFiles(directory="fastapi_app/static"), name="admin-static")