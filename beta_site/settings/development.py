"""
Configuration de développement
"""
from .base import *
import os

# --- DÉBOGAGE ---
DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-development-key-12345')

# --- HÔTES AUTORISÉS ---
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# --- BASE DE DONNÉES (SQLite pour le développement) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- APPLICATIONS DE DÉBOGAGE ---
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# --- INTERNAL IPS pour debug toolbar ---
INTERNAL_IPS = ['127.0.0.1']

# --- CACHE ---
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# --- FICHIERS STATIQUES ---
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# --- EMAIL (console pour le développement) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 

# --- CORS ---
CORS_ALLOW_ALL_ORIGINS = True

# --- LOGGING ---
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
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Créer le dossier logs si nécessaire
LOG_DIR = BASE_DIR / 'logs'
if not LOG_DIR.exists():
    LOG_DIR.mkdir()