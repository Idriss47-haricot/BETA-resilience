"""
Sitemap pour le référencement SEO
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.core.models import Page
from apps.actualites.models import Article
from apps.projets.models import Projet
from apps.membres.models import Membre
from apps.services.models import Service


class StaticViewSitemap(Sitemap):
    """
    Sitemap pour les pages statiques
    """
    priority = 0.8
    changefreq = 'monthly'
    
    def items(self):
        return [
            'core:accueil',
            'core:a_propos',
            'core:historique',
            'core:vision',
            'core:missions',
            'core:structuration',
            'core:conditions',
            'services:list',
            'projets:list',
            'actualites:list',
            'contacts:contact',
            'partenaires:list',
        ]
    
    def location(self, item):
        return reverse(item)


class PageSitemap(Sitemap):
    """
    Sitemap pour les pages dynamiques
    """
    priority = 0.6
    changefreq = 'monthly'
    
    def items(self):
        return Page.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at


class ArticleSitemap(Sitemap):
    """
    Sitemap pour les articles de blog
    """
    priority = 0.7
    changefreq = 'weekly'
    
    def items(self):
        return Article.objects.filter(est_publie=True)
    
    def lastmod(self, obj):
        return obj.date_modification or obj.date_publication


class ProjetSitemap(Sitemap):
    """
    Sitemap pour les projets
    """
    priority = 0.6
    changefreq = 'monthly'
    
    def items(self):
        return Projet.objects.filter(est_publie=True)
    
    def lastmod(self, obj):
        return obj.updated_at


class MembreSitemap(Sitemap):
    """
    Sitemap pour les membres
    """
    priority = 0.4
    changefreq = 'monthly'
    
    def items(self):
        return Membre.objects.filter(est_actif=True)
    
    def lastmod(self, obj):
        return obj.updated_at


class ServiceSitemap(Sitemap):
    """
    Sitemap pour les services
    """
    priority = 0.5
    changefreq = 'monthly'
    
    def items(self):
        return Service.objects.filter(est_actif=True)
    
    def lastmod(self, obj):
        return obj.updated_at