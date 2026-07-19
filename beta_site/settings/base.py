"""
Configuration de base commune à tous les environnements
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # ← 3 niveaux car settings/base.py

SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')

# Ajoute le dossier racine du projet au PYTHONPATH
sys.path.insert(0, str(BASE_DIR))

# --- APPLICATIONS DE BASE ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

# --- APPLICATIONS TIERCES ---
THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'ckeditor',
    'compressor',
    'meta',
]

# --- APPLICATIONS BETA-RÉSILIENCE ---
LOCAL_APPS = [
    'apps.core',
    'apps.membres',
    'apps.services',
    'apps.projets',
    'apps.actualites',
    'apps.documents',
    'apps.partenaires',
    'apps.contacts',
    'apps.demandes', 
    'apps.notifications',   # ← ajoute
    'apps.evenements',      # ← ajoute
    'apps.forums',          # ← ajoute
    'apps.authentification',   # ✅ AJOUTER CETTE LIGNE   
]

INSTALLED_APPS += THIRD_PARTY_APPS + LOCAL_APPS

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- TEMPLATES ---
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
                'apps.core.context_processors.site_global',
            ],
        },
    },
]

# --- AUTHENTIFICATION ---
ROOT_URLCONF = 'beta_site.urls'
WSGI_APPLICATION = 'beta_site.wsgi.application'

# --- INTERNATIONALISATION ---
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True

# --- FICHIERS STATIQUES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- FICHIERS MÉDIAS ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- CRISPY FORMS ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- CKEDITOR ---
CKEDITOR_CONFIGS = {
    'default': {
        'height': 400,
        'width': '100%',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
            ['Font', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Source', 'Format', 'Maximize'],
        ],
        # Plugins de base uniquement — pas youtube/video qui ne sont pas inclus
        'extraPlugins': ','.join([
            'image2', 'font', 'colorbutton',
            'justify', 'lineutils', 'widget',
            'dialog', 'dialogui',
        ]),
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
    },
}

# --- DÉFAUT ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- AUTHENTIFICATION ---
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

# --- MESSAGES ---
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# --- SESSION ---
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_SAVE_EVERY_REQUEST = True

# --- SÉCURITÉ ---
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# --- EMAIL (par défaut) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', EMAIL_HOST_USER)


"""
Configuration de base avec optimisations - Ajouter ces paramètres
"""

# --- OPTIMISATION DES REQUÊTES ---
# Utiliser select_related et prefetch_related automatiquement
# Configurer un cache pour les requêtes lourdes
# Ajouter des indexes sur les champs fréquemment recherchés

# --- CACHE POUR LES VUES ---
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'beta'

# --- TEMPLATES CACHING ---
TEMPLATE_LOADERS = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# --- COMPRESSION DES FICHIERS STATIQUES ---
# django-compressor

COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]
COMPRESS_PRECOMPILERS = [
    ('text/x-scss', 'django_libsass.SassCompiler'),
]

# --- OPTIMISATION DES IMAGES ---
# django-imagekit pour optimiser les images


# Configuration d'imagekit
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.Optimistic'

# --- PAGINATION PAR DÉFAUT ---
PAGINATION_DEFAULT_PAGE_SIZE = 12

# --- DATABASE OPTIMIZATIONS ---
# Pool de connexions
DATABASE_POOL = {
    'max_connections': 20,
    'min_connections': 2,
}

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',  # pour django-compressor
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
