"""
Configuration de production - Version sécurisée
"""
from .base import *
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# --- VARIABLES D'ENVIRONNEMENT OBLIGATOIRES ---
def get_env_variable(var_name):
    """Récupérer une variable d'environnement ou lever une erreur"""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"La variable d'environnement {var_name} est manquante"
        raise ImproperlyConfigured(error_msg)

# --- DÉTECTION DE L'ENVIRONNEMENT SERVERLESS (Vercel) ---
ON_VERCEL = os.getenv('VERCEL') == '1'

# --- SÉCURITÉ DE BASE ---
DEBUG = False
SECRET_KEY = get_env_variable('SECRET_KEY')

# --- HÔTES AUTORISÉS ---
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# --- BASE DE DONNÉES (PostgreSQL) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', ''),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Garder la connexion ouverte 10 minutes
        'OPTIONS': {
            'sslmode': os.getenv('DB_SSLMODE', 'require'),
        }
    }
}

# Utiliser DATABASE_URL si disponible (cas de Neon/Vercel)
if os.getenv('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )

# --- SÉCURITÉ HTTPS ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- SÉCURITÉ DES COOKIES ---
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_SAVE_EVERY_REQUEST = True

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_AGE = 31449600  # 1 an

# --- SÉCURITÉ DES CONTENUS ---
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# --- FICHIERS STATIQUES ---
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- MIDDLEWARE SUPPLEMENTAIRE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE

# --- AUTHENTIFICATION ---
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# --- LIMITATION DES TENTATIVES DE CONNEXION ---
INSTALLED_APPS += ['axes']
MIDDLEWARE += ['axes.middleware.AxesMiddleware']

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCK_OUT_AT_FAILURE = True
AXES_USE_USER_AGENT = True
AXES_IPWARE_PROXY_COUNT = 2
AXES_RESET_ON_SUCCESS = True
AXES_NEVER_LOCKOUT_WHITELIST = True

# --- EMAIL (SMTP sécurisé) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# --- ADMIN ---
ADMINS = [('Admin', os.getenv('ADMIN_EMAIL', DEFAULT_FROM_EMAIL))]

# --- LOGGING AVANCÉ ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level":"{levelname}","time":"{asctime}","module":"{module}","message":"{message}"}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Sur un serveur classique (pas Vercel), on ajoute des fichiers de log en plus de la console
if not ON_VERCEL:
    LOG_DIR = BASE_DIR / 'logs'
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    LOGGING['handlers']['file'] = {
        'level': 'WARNING',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOG_DIR / 'production.log',
        'maxBytes': 10 * 1024 * 1024,  # 10 Mo
        'backupCount': 10,
        'formatter': 'verbose',
    }
    LOGGING['handlers']['security_file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOG_DIR / 'security.log',
        'maxBytes': 5 * 1024 * 1024,  # 5 Mo
        'backupCount': 5,
        'formatter': 'json',
    }
    LOGGING['loggers']['django']['handlers'] = ['file', 'mail_admins']
    LOGGING['loggers']['django.request']['handlers'] = ['file', 'mail_admins']
    LOGGING['loggers']['django.security']['handlers'] = ['security_file']
    LOGGING['loggers']['axes']['handlers'] = ['security_file']

# --- CACHE ---
if os.getenv('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.getenv('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
                'CONNECTION_POOL_CLASS_KWARGS': {
                    'max_connections': 50,
                    'timeout': 20,
                },
                'MAX_CONNECTIONS': 1000,
                'PICKLE_VERSION': -1,
            },
            'KEY_PREFIX': 'beta',
        }
    }
else:
    # Pas de Redis configuré : cache mémoire locale (fonctionne partout, y compris sur Vercel)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# --- RATELIMIT (pour les API et formulaires) ---
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# --- BACKUP AUTOMATIQUE (désactivé sur Vercel : système de fichiers en lecture seule) ---
if not ON_VERCEL:
    INSTALLED_APPS += ['dbbackup']

    DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
    DBBACKUP_STORAGE_OPTIONS = {
        'location': BASE_DIR / 'backups/',
    }
    DBBACKUP_CLEANUP_KEEP = 7
    DBBACKUP_CLEANUP_KEEP_MEDIA = 7

    BACKUP_DIR = BASE_DIR / 'backups'
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)