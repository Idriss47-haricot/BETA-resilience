"""
Utilitaires pour les notifications
"""
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from apps.notifications.models import Notification


def creer_notification(utilisateur, type_notification, titre, message, lien=None):
    """
    Créer une notification pour un utilisateur
    """
    notification = Notification.objects.create(
        utilisateur=utilisateur,
        type=type_notification,
        titre=titre,
        message=message,
        lien=lien
    )
    return notification


def envoyer_notification_a_tous(titre, message, type_notification='systeme', lien=None):
    """
    Envoyer une notification à tous les utilisateurs actifs
    """
    from apps.membres.models import Membre
    membres = Membre.objects.filter(est_actif=True, est_compte_active=True)
    count = 0
    
    for membre in membres:
        if membre.user:
            Notification.objects.create(
                utilisateur=membre.user,
                type=type_notification,
                titre=titre,
                message=message,
                lien=lien
            )
            count += 1
    
    return count


def envoyer_notification_a_groupe(utilisateurs, titre, message, type_notification='systeme', lien=None):
    """
    Envoyer une notification à un groupe d'utilisateurs
    """
    count = 0
    for utilisateur in utilisateurs:
        Notification.objects.create(
            utilisateur=utilisateur,
            type=type_notification,
            titre=titre,
            message=message,
            lien=lien
        )
        count += 1
    return count


def envoyer_email_notification(notification):
    """
    Envoyer une notification par email
    """
    try:
        sujet = f'[BETA-Résilience] {notification.titre}'
        context = {
            'notification': notification,
            'site_url': settings.SITE_URL,
            'site_name': 'BETA-Résilience',
        }
        message_html = render_to_string('notifications/email_notification.html', context)
        
        email = EmailMessage(
            sujet,
            message_html,
            settings.DEFAULT_FROM_EMAIL,
            [notification.utilisateur.email],
            reply_to=[settings.CONTACT_EMAIL],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)
    except Exception as e:
        print(f"Erreur d'envoi d'email: {e}")