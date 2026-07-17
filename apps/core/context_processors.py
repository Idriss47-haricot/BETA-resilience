"""
Context processors pour injecter des données globales dans tous les templates
"""
from apps.core.models import SiteConfiguration
from apps.partenaires.models import Partenaire
from apps.actualites.models import Article
from apps.projets.models import Projet
from apps.services.models import Service

"""
Context processors pour le SEO
"""
from apps.core.models import SiteConfiguration
from django.conf import settings


def seo_context(request):
    """
    Ajouter des variables SEO à tous les templates
    """
    site_config = SiteConfiguration.objects.first()
    
    context = {
        'site_name': site_config.site_name if site_config else 'BETA-Résilience',
        'site_tagline': site_config.site_tagline if site_config else '',
        'site_description': site_config.meta_description if site_config else '',
        'site_keywords': site_config.meta_keywords if site_config else '',
        'site_url': request.build_absolute_uri('/'),
        'current_path': request.path,
    }
    
    # Ajouter le titre par défaut
    if request.path == '/':
        context['page_title'] = f"{site_config.site_name if site_config else 'BETA-Résilience'}"
    else:
        context['page_title'] = f"{context.get('page_title', '')} - {site_config.site_name if site_config else 'BETA-Résilience'}"
    
    return context

def site_global(request):
    """
    Variables globales disponibles dans tous les templates
    """
    context = {}
    
    # Configuration du site
    site_config = SiteConfiguration.objects.first()
    context['site_config'] = site_config
    
    # Menu - pages statiques pour le menu principal
    from apps.core.models import Page
    context['menu_pages'] = Page.objects.filter(is_published=True, is_in_menu=True).order_by('order')
    
    # Dernières actualités pour le footer ou sidebar
    context['footer_actualites'] = Article.objects.filter(est_publie=True).order_by('-date_publication')[:3]
    
    # Derniers projets
    context['footer_projets'] = Projet.objects.filter(est_publie=True).order_by('-date_debut')[:3]
    
    # Partenaires pour le footer
    context['footer_partenaires'] = Partenaire.objects.filter(est_actif=True).order_by('?')[:6]
    
    # Année pour le copyright
    from datetime import datetime
    context['current_year'] = datetime.now().year
    
    return context