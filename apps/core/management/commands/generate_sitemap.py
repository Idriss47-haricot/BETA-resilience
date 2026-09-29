"""
Commande Django pour générer le sitemap
python manage.py generate_sitemap
"""
from django.core.management.base import BaseCommand
from django.contrib.sitemaps.views import sitemap
from django.core.management import call_command
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Génère le sitemap du site'
    
    def handle(self, *args, **options):
        self.stdout.write('Génération du sitemap...')
        
        # Définir le chemin du sitemap
        sitemap_path = settings.BASE_DIR / 'sitemap.xml'
        
        # Générer le sitemap en utilisant la commande Django
        call_command('sitemap')
        
        self.stdout.write(self.style.SUCCESS(f'Sitemap généré avec succès: {sitemap_path}'))