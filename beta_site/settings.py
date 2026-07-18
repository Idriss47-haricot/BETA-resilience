Import os
from pathlib import Path
from dotenv import load_dotenv
from django.urls import reverse_lazy

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ============ SÉCURITÉ ============
SECRET_KEY = 'django-insecure-temp-key-change-later'
DEBUG = True  # Met False en production
ALLOWED_HOSTS = [
    'carlosidriss.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# ============ APPLICATIONS ============
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'ckeditor',
    'compressor',
    'meta',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'debug_toolbar',
    
    # BETA-Résilience apps
    'apps.core',
    'apps.membres',
    'apps.services',
    'apps.projets',
    'apps.demandes',
    'apps.actualites',
    'apps.documents',
    'apps.partenaires',
    'apps.contacts',
    'apps.notifications',  
    'apps.evenements',     
    'apps.forums',      
    'apps.authentification',   # ✅ AJOUTER CETTE LIGNE

]

# ============ MIDDLEWARE ============
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# ============ URLs ET WSGI ============
ROOT_URLCONF = 'beta_site.urls'
WSGI_APPLICATION = 'beta_site.wsgi.application'

# ============ TEMPLATES ============
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ CORRIGÉ
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_global',  # ✅ AJOUTÉ
            ],
        },
    },
]

# ============ BASE DE DONNÉES ============
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============ AUTHENTIFICATION ============
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============ INTERNATIONALISATION ============
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True

# ============ FICHIERS STATIQUES ============
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============ FICHIERS MÉDIAS ============
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============ CRISPY FORMS ============
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ============ CKEDITOR ============
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 400,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage', 'image2', 'youtube', 'video',
            'font', 'colorbutton', 'justify',
            'widget', 'dialog', 'dialogui'
        ]),
    },
}

# ============ COMPRESSOR ============
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter']
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

# ============ META ============
META_SITE_NAME = 'BETA-Résilience'

# ============ EMAIL ============
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'betaresilienceofficiel1@gmail.com'
EMAIL_HOST_PASSWORD = 'uvnj mffq oqzw zgkz'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL = EMAIL_HOST_USER

# ============ URL DU SITE ============
SITE_URL = 'http://127.0.0.1:8000'

# ============ AUTHENTIFICATION ============
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/membres/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ============ DEBUG TOOLBAR ============
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1']

# ============ DÉFAUT ============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
