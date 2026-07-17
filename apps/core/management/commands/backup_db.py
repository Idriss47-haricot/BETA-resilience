"""
Commande Django pour sauvegarder la base de données
python manage.py backup_db
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
import os
import shutil
import datetime
import subprocess
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sauvegarde automatique de la base de données et des médias'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['db', 'media', 'all'],
            default='all',
            help='Type de sauvegarde'
        )
    
    def handle(self, *args, **options):
        backup_type = options['type']
        
        # Créer le dossier de sauvegarde
        backup_dir = settings.BASE_DIR / 'backups'
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if backup_type in ['db', 'all']:
            self.backup_database(backup_dir, timestamp)
        
        if backup_type in ['media', 'all']:
            self.backup_media(backup_dir, timestamp)
        
        # Nettoyer les anciennes sauvegardes
        self.cleanup_old_backups(backup_dir)
        
        self.stdout.write(self.style.SUCCESS(f'Sauvegarde terminée avec succès !'))
    
    def backup_database(self, backup_dir, timestamp):
        """
        Sauvegarder la base de données PostgreSQL
        """
        db_settings = settings.DATABASES['default']
        
        if db_settings['ENGINE'] == 'django.db.backends.postgresql':
            backup_file = backup_dir / f'db_backup_{timestamp}.sql'
            
            try:
                # Utiliser pg_dump pour PostgreSQL
                cmd = [
                    'pg_dump',
                    '-h', db_settings['HOST'],
                    '-p', db_settings['PORT'],
                    '-U', db_settings['USER'],
                    '-d', db_settings['NAME'],
                    '-f', str(backup_file),
                    '--format=plain',
                    '--clean',
                ]
                
                # Ajouter le mot de passe dans les variables d'environnement
                env = os.environ.copy()
                env['PGPASSWORD'] = db_settings['PASSWORD']
                
                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                
                if result.returncode == 0:
                    size = backup_file.stat().st_size / (1024 * 1024)
                    self.stdout.write(
                        self.style.SUCCESS(f'Base de données sauvegardée: {backup_file.name} ({size:.2f} Mo)')
                    )
                    logger.info(f"Base de données sauvegardée: {backup_file.name}")
                else:
                    self.stdout.write(self.style.ERROR(f'Erreur: {result.stderr}'))
                    logger.error(f"Erreur de sauvegarde DB: {result.stderr}")
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erreur: {str(e)}'))
                logger.error(f"Erreur de sauvegarde DB: {str(e)}")
        
        elif db_settings['ENGINE'] == 'django.db.backends.sqlite3':
            # Pour SQLite, copier le fichier
            db_path = db_settings['NAME']
            backup_file = backup_dir / f'db_backup_{timestamp}.sqlite3'
            
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_file)
                size = backup_file.stat().st_size / (1024 * 1024)
                self.stdout.write(
                    self.style.SUCCESS(f'Base de données sauvegardée: {backup_file.name} ({size:.2f} Mo)')
                )
                logger.info(f"Base de données sauvegardée: {backup_file.name}")
            else:
                self.stdout.write(self.style.ERROR('Fichier de base de données introuvable.'))
    
    def backup_media(self, backup_dir, timestamp):
        """
        Sauvegarder les fichiers média
        """
        media_dir = settings.MEDIA_ROOT
        backup_file = backup_dir / f'media_backup_{timestamp}.zip'
        
        if os.path.exists(media_dir):
            try:
                shutil.make_archive(str(backup_file).replace('.zip', ''), 'zip', media_dir)
                size = backup_file.stat().st_size / (1024 * 1024)
                self.stdout.write(
                    self.style.SUCCESS(f'Médias sauvegardés: {backup_file.name} ({size:.2f} Mo)')
                )
                logger.info(f"Médias sauvegardés: {backup_file.name}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erreur: {str(e)}'))
                logger.error(f"Erreur de sauvegarde des médias: {str(e)}")
        else:
            self.stdout.write(self.style.WARNING('Dossier media introuvable.'))
    
    def cleanup_old_backups(self, backup_dir):
        """
        Supprimer les sauvegardes de plus de 7 jours
        """
        import datetime
        from pathlib import Path
        
        cutoff = datetime.datetime.now() - datetime.timedelta(days=7)
        
        for file in backup_dir.iterdir():
            if file.is_file():
                file_time = datetime.datetime.fromtimestamp(file.stat().st_mtime)
                if file_time < cutoff:
                    file.unlink()
                    self.stdout.write(f'Ancienne sauvegarde supprimée: {file.name}')
                    logger.info(f"Ancienne sauvegarde supprimée: {file.name}")