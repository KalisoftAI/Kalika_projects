import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key-here'
DEBUG = True
# Add your domain here. If accessing via IP or localhost directly, keep them.
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'kalikaindia.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog.apps.CatalogConfig',
    'accounts.apps.AccountsConfig',
    'cart.apps.CartConfig',
    'crispy_forms',
    'crispy_bootstrap4','punchout',
    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'catalog.context_processors.categories','catalog.context_processors.cart_item_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecom_prod_catalog',
        'USER': 'vikas',
        'PASSWORD': 'kalika1667',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
AUTH_USER_MODEL = 'accounts.CustomUser'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "catalog/static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Added to define where collected static files will go

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.CustomUser'
CRISPY_TEMPLATE_PACK = 'bootstrap4'  # Set to use Bootstrap 4 templates
CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap4',)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = 'us-east-1'
AWS_S3_BUCKET_NAME = 'kalika-ecom'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SAMESITE = 'Lax'

# Ariba PunchOut Settings
ARIBA_NETWORK_ID = os.getenv('ARIBA_NETWORK_ID')
ARIBA_ENDPOINT = 'https://test.ariba.com/punchout/cxml/setup'

# --- Static and Media Files (Crucial for Nginx serving) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "catalog/static"] # Keep your app-specific static dirs
STATIC_ROOT = BASE_DIR / "staticfiles" # Nginx will serve from here

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "mediafiles" # Nginx will serve from here (create this folder)

# --- SSL Configuration (for Nginx reverse proxy with HTTPS) ---
# Tells Django that Nginx is handling SSL and forwarding the original protocol
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Set to True for production to redirect HTTP to HTTPS. For local testing, keep False initially.
# Once Nginx is configured with SSL, you can try setting this to True.
SECURE_SSL_REDIRECT = False

# Ensure cookies are only sent over HTTPS. Set to True for production.
# For local testing with self-signed certs or if issues, keep False initially.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False