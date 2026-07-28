"""
Commande pour envoyer des notifications en masse
python manage.py send_notification --titre "Info" --message "Message" --type systeme
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.notifications.models import Notification
from apps.membres.models import Membre


class Command(BaseCommand):
    help = 'Envoyer une notification à tous les membres'
    
    def add_arguments(self, parser):
        parser.add_argument('--titre', type=str, help='Titre de la notification')
        parser.add_argument('--message', type=str, help='Message de la notification')
        parser.add_argument('--type', type=str, default='systeme', help='Type de notification')
        parser.add_argument('--lien', type=str, default='', help='Lien associé')
    
    def handle(self, *args, **options):
        titre = options.get('titre')
        message = options.get('message')
        type_notif = options.get('type')
        lien = options.get('lien', '')
        
        if not titre or not message:
            self.stdout.write(self.style.ERROR('❌ Titre et message sont requis'))
            return
        
        membres = Membre.objects.filter(est_actif=True, est_compte_active=True)
        count = 0
        
        for membre in membres:
            if membre.user:
                Notification.objects.create(
                    utilisateur=membre.user,
                    type=type_notif,
                    titre=titre,
                    message=message,
                    lien=lien,
                )
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Notification envoyée à {count} membres !')
        )