from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = 'django-insecure-cqg&&gl+!yt7mdytm1_f9d$fr&2h&xz_mrd%n)zr!2vqzeke#-'  # Cambia esta clave en producción

DEBUG = True

ALLOWED_HOSTS = []  # Agregar los hosts permitidos en producción

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps de terceros
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Apps propias
    'accounts',
    'barbers',
    'services',
    'schedules',
    'appointments',
    'reviews',
    # Nueva app de monitoreo
    'monitoring',
]

# Configuración para el heartbeat
HEARTBEAT_CHECK_INTERVAL = 30  # segundos
HEARTBEAT_FAILURE_THRESHOLD = 120  # segundos (2 minutos)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Mantener CSRF pero lo desactivamos para token
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'monitoring.middleware.HeartbeatCsrfExemptMiddleware',  # Añadir este middleware al final
]

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # Autenticación por token
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Autenticación requerida por defecto
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = True  # En producción, especificar los orígenes permitidos

# Configuración de usuario personalizado
AUTH_USER_MODEL = 'accounts.User'

ROOT_URLCONF = 'backend_barberia.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_barberia.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Puedes cambiar a una base de datos más robusta en producción
    }
}

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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================ AÑADIR DESDE AQUÍ ================

# Configuración de Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Asegúrate de tener Redis instalado
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'  # Usa la misma zona horaria que tienes en Django

# Configuración para tareas periódicas (Celery Beat)
CELERY_BEAT_SCHEDULE = {
    'check-nodes-every-30-seconds': {
        'task': 'monitoring.tasks.check_nodes_heartbeat',
        'schedule': HEARTBEAT_CHECK_INTERVAL,  # Usa la variable que ya tienes definida
    },
    'check-services-every-5-minutes': {
        'task': 'monitoring.tasks.check_barbershop_services',
        'schedule': 300.0,  # cada 5 minutos
    },
}

# Configuración de logging para Celery
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'monitoring': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Asegúrate de que exista el directorio de logs
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)