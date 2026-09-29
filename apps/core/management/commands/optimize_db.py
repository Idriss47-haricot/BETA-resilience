"""
Commande Django pour optimiser la base de données
python manage.py optimize_db
"""
from django.core.management.base import BaseCommand
from django.db import connection, connections
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimiser la base de données (indexes, vacuum, etc.)'
    
    def handle(self, *args, **options):
        self.stdout.write('Optimisation de la base de données...')
        
        # Vérifier et créer les indexes manquants
        self.create_missing_indexes()
        
        # Vider les données inutiles
        self.vacuum_database()
        
        # Analyser les statistiques
        self.analyze_database()
        
        self.stdout.write(self.style.SUCCESS('Optimisation terminée !'))
    
    def create_missing_indexes(self):
        """
        Créer des indexes sur les champs fréquemment recherchés
        """
        with connection.cursor() as cursor:
            # Vérifier si l'index existe déjà
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'articles_date_publication_idx'
                )
            """)
            exists = cursor.fetchone()[0]
            
            if not exists:
                self.stdout.write('Création des indexes...')
                # Index pour les dates
                cursor.execute('CREATE INDEX articles_date_publication_idx ON actualites_article (date_publication DESC);')
                cursor.execute('CREATE INDEX projets_date_debut_idx ON projets_projet (date_debut DESC);')
                
                # Index pour les slugs
                cursor.execute('CREATE INDEX articles_slug_idx ON actualites_article (slug);')
                cursor.execute('CREATE INDEX projets_slug_idx ON projets_projet (slug);')
                
                # Index pour les statuts
                cursor.execute('CREATE INDEX articles_statut_idx ON actualites_article (statut);')
                cursor.execute('CREATE INDEX projets_statut_idx ON projets_projet (statut);')
                
                self.stdout.write(self.style.SUCCESS('Indexes créés avec succès.'))
            else:
                self.stdout.write('Indexes déjà présents.')
    
    def vacuum_database(self):
        """
        Vider les données inutiles (PostgreSQL)
        """
        with connection.cursor() as cursor:
            self.stdout.write('VACUUM en cours...')
            cursor.execute('VACUUM ANALYZE;')
    
    def analyze_database(self):
        """
        Analyser les statistiques de la base de données
        """
        with connection.cursor() as cursor:
            self.stdout.write('Analyse des statistiques...')
            cursor.execute('ANALYZE;')