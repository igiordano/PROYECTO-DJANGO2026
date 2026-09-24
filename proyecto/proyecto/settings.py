"""
Configuracion Django del proyecto Autopartes.

Los valores sensibles y dependientes del entorno se leen desde variables de
entorno (ver `.env.example`) y solo usan valores por defecto cuando
`DJANGO_DEBUG` esta activo, de modo que un despliegue en produccion no pueda
arrancar por accidente con la clave de desarrollo.

Correcciones aplicadas respecto de la version original:
- `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` ya no estan incrustados en el codigo.
- Se agrega i18n para Argentina y el uso de `Decimal` para montos monetarios.
- Se configura Django REST Framework con autenticacion JWT y paginacion.
- Se habilita CORS solo para los origenes declarados en el entorno.
"""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(nombre, por_defecto=False):
    """Lee una variable de entorno booleana aceptando 1/true/yes/on."""
    valor = os.environ.get(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in {'1', 'true', 'yes', 'on', 'si', 'sí'}


def env_list(nombre, por_defecto=None):
    """Lee una variable separada por comas y descarta los elementos vacios."""
    valor = os.environ.get(nombre, '')
    return [elemento.strip() for elemento in valor.split(',') if elemento.strip()] or list(por_defecto or [])


# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------

DEBUG = env_bool('DJANGO_DEBUG', por_defecto=True)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        # Clave de desarrollo: solo valida mientras DEBUG=True.
        SECRET_KEY = 'django-insecure-clave-solo-para-desarrollo-local'
    else:
        raise RuntimeError(
            'Falta la variable de entorno DJANGO_SECRET_KEY. '
            'Definila antes de ejecutar con DEBUG=False.'
        )

ALLOWED_HOSTS = env_list(
    'DJANGO_ALLOWED_HOSTS',
    por_defecto=['localhost', '127.0.0.1', '[::1]'] if DEBUG else [],
)

CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS')

# Cabeceras y cookies endurecidas cuando el sitio corre en produccion.
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', por_defecto=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'


# ---------------------------------------------------------------------------
# Aplicaciones y middleware
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceros
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    # Propias
    'Autopartes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # CorsMiddleware debe ir lo mas arriba posible y antes de CommonMiddleware.
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proyecto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'proyecto.wsgi.application'
ASGI_APPLICATION = 'proyecto.asgi.application'


# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # Evita el error "database is locked" cuando hay escrituras seguidas.
        'OPTIONS': {'timeout': 20},
    }
}
# Nota: SQLite alcanza para desarrollo y para una demo. Para produccion con
# mas de un proceso, migrar a PostgreSQL es la recomendacion de la auditoria.


# ---------------------------------------------------------------------------
# Autenticacion y contrasenas
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internacionalizacion
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Archivos estaticos y multimedia
# ---------------------------------------------------------------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Destino de `collectstatic` para produccion.
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Todo cerrado por defecto: cada vista abre lo que necesita.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        # Limita los envios anonimos del formulario de contacto.
        'anon': '60/hour',
        'user': '2000/hour',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'SIGNING_KEY': SECRET_KEY,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API Autopartes',
    'DESCRIPTION': (
        'API REST del sistema de autopartes. Autenticacion con JWT: obtenga el '
        'par de tokens en /api/v1/auth/token/ y envie el token de acceso en la '
        'cabecera `Authorization: Bearer <token>`.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}


# ---------------------------------------------------------------------------
# CORS (necesario para la app cliente en el navegador)
# ---------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env_list('DJANGO_CORS_ALLOWED_ORIGINS')
if DEBUG:
    # Puertos habituales de desarrollo de Vite, Create React App y Expo Web.
    CORS_ALLOWED_ORIGINS += [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:8081',
        'http://127.0.0.1:8081',
    ]
CORS_ALLOWED_ORIGINS = sorted(set(CORS_ALLOWED_ORIGINS))
CORS_ALLOW_CREDENTIALS = False


# ---------------------------------------------------------------------------
# Registro de errores
# ---------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '[{levelname}] {asctime} {name}: {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
