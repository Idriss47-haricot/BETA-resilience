"""
Configuration des URLs principales du site BETA-Résilience
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from .sitemaps import StaticViewSitemap

# Imports d'applications
from apps.core.views import redirect_after_login
from apps.membres.views import MembreLoginView, MaDemandeDetailView

# Import de l'admin personnalisé
from apps.core.admin import admin_site

# Imports des sitemaps
from apps.core.sitemaps import (
    StaticViewSitemap,
    PageSitemap,
    ArticleSitemap,
    ProjetSitemap,
    MembreSitemap,
    ServiceSitemap
)

# Import pour le robots.txt
from apps.core.seo import RobotsTxtView


# ============================================================
# 1. CONFIGURATION DU SITEMAP
# ============================================================
sitemaps = {
    'static': StaticViewSitemap,
    'pages': PageSitemap,
    'articles': ArticleSitemap,
    'projets': ProjetSitemap,
    'membres': MembreSitemap,
    'services': ServiceSitemap,
}


# ============================================================
# 2. URLS PRINCIPALES
# ============================================================
urlpatterns = [
    # ----- Administration -----
    path('admin/', admin_site.urls),

    # ----- Applications principales -----
    path('', include('apps.core.urls')),
    path('membres/', include('apps.membres.urls')),
    path('services/', include('apps.services.urls')),
    path('projets/', include('apps.projets.urls')),
    path('actualites/', include('apps.actualites.urls')),
    path('documents/', include('apps.documents.urls')),
    path('partenaires/', include('apps.partenaires.urls')),
    path('contact/', include('apps.contacts.urls')),
    path('demandes/', include('apps.demandes.urls')),
    path('forums/', include('apps.forums.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('evenements/', include('apps.evenements.urls')),

    # ----- Authentification & Comptes -----
    path('auth-2fa/', include('apps.authentification.urls')),
    path('login/', MembreLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/profile/', redirect_after_login, name='profile_redirect'),
    path('register/', TemplateView.as_view(template_name='authentification/register.html'), name='register_prive'),

    # ----- Détail demande membre -----
    path('membres/ma-demande/<int:pk>/', MaDemandeDetailView.as_view(), name='ma_demande_detail'),

    # ----- SEO & Vérifications -----
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', RobotsTxtView.as_view(), name='robots'),
    path('google1234567890.html', TemplateView.as_view(template_name='google_verification.html')),
]


# ============================================================
# 3. GESTION DES FICHIERS STATIQUES ET MÉDIAS (DÉVELOPPEMENT)
# ============================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
    except ImportError:
        pass
