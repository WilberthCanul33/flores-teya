import os
from pathlib import Path
from decouple import config
import paypalrestsdk
from django.utils.translation import gettext_lazy as _



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')



# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local apps
    'apps.accounts',
    'apps.catalog',
    'apps.cart',
    'apps.orders',
    'apps.payments',
    'apps.shipping',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← Agrega esto
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'organic_veggies.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.cart.context_processors.cart_count_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'organic_veggies.wsgi.application'

# Detectar si estamos en Docker - VERSIÓN MEJORADA
def is_running_in_docker():
    """Detecta si estamos dentro de un contenedor Docker"""
    # La variable DOCKER_CONTAINER=true se pasa desde docker-compose
    return os.environ.get('DOCKER_CONTAINER') == 'true'

# Configuración de base de datos según el entorno
if is_running_in_docker():
    # Estamos en Docker - usar nombres de servicio y variables del .env
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DOCKER_DB_NAME'),
            'USER': config('DOCKER_DB_USER'),
            'PASSWORD': config('DOCKER_DB_PASSWORD'),  # Toma del .env
            'HOST': config('DOCKER_DB_HOST'),
            'PORT': config('DOCKER_DB_PORT'),
        }
    }
    print("🐳 Configuración DOCKER detectada")
    print(f"   - DB Name: {config('DOCKER_DB_NAME')}")
    print(f"   - DB User: {config('DOCKER_DB_USER')}")
    print(f"   - DB Host: {config('DOCKER_DB_HOST')}")
else:
    # Estamos en desarrollo local - usar localhost
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('LOCAL_DB_NAME'),
            'USER': config('LOCAL_DB_USER'),
            'PASSWORD': config('LOCAL_DB_PASSWORD'),
            'HOST': config('LOCAL_DB_HOST'),
            'PORT': config('LOCAL_DB_PORT'),
        }
    }
    print("💻 Configuración LOCAL detectada")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Idioma por defecto
LANGUAGE_CODE = 'es-mx'



TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'catalog:product_list'
LOGOUT_REDIRECT_URL = 'catalog:product_list'

# Session settings
CART_SESSION_ID = 'cart'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# PayPal Configuration
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = config('PAYPAL_MODE', default='sandbox')
PAYPAL_RETURN_URL = config('PAYPAL_RETURN_URL')
PAYPAL_CANCEL_URL = config('PAYPAL_CANCEL_URL')

# Configurar SDK de PayPal
paypalrestsdk.configure({
    "mode": PAYPAL_MODE,
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET
})

# Configuración de Email - AHORA INDEPENDIENTE DE DEBUG
USE_MAILTRAP = config('USE_MAILTRAP', default=False, cast=bool)

if USE_MAILTRAP:
    # Usar Mailtrap (para pruebas)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('MAILTRAP_HOST', default='sandbox.smtp.mailtrap.io')
    EMAIL_PORT = config('MAILTRAP_PORT', default=2525, cast=int)
    EMAIL_HOST_USER = config('MAILTRAP_USER', default='')
    EMAIL_HOST_PASSWORD = config('MAILTRAP_PASSWORD', default='')
    EMAIL_USE_TLS = True
    print("📧 Usando MAILTRAP para emails de prueba")
else:
    # Usar Gmail real (producción)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    print("📧 Usando GMAIL REAL para emails")

DEFAULT_FROM_EMAIL = 'Organic Veggies <noreply@organicveggies.com>'
SITE_URL = config('SITE_URL', default='http://localhost:8000')

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_INDEX_FILE = True
WHITENOISE_ALLOW_ALL_ORIGINS = True
WHITENOISE_AUTOREFRESH = False
WHITENOISE_USE_FINDERS = False
WHITENOISE_MANIFEST_STRICT = False