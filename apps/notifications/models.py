from django.db import models

# Create your models here.
"""
Modèles pour l'application Notifications
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """
    Notification pour un utilisateur
    """
    TYPE_CHOICES = [
        ('demande_validee', '✅ Demande validée'),
        ('demande_refusee', '❌ Demande refusée'),
        ('demande_en_cours', '🔄 Demande en cours'),
        ('demande_recue', '📩 Demande reçue'),
        ('nouveau_document', '📄 Nouveau document'),
        ('evenement_proche', '📅 Événement proche'),
        ('evenement_annule', '❌ Événement annulé'),
        ('evenement_ajoute', '📅 Nouvel événement'),
        ('rappel_activation', '⏰ Rappel d\'activation'),
        ('bienvenue', '👋 Bienvenue'),
        ('message_forum', '💬 Nouveau message'),
        ('reponse_demande', '📝 Réponse à votre demande'),
        ('systeme', '⚙️ Information système'),
    ]
    
    utilisateur = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='Utilisateur'
    )
    type = models.CharField(
        'Type de notification', 
        max_length=30, 
        choices=TYPE_CHOICES
    )
    titre = models.CharField('Titre', max_length=200)
    message = models.TextField('Message')
    lien = models.CharField('Lien', max_length=500, blank=True, null=True)
    est_lue = models.BooleanField('Lue', default=False)
    date_creation = models.DateTimeField('Date de création', auto_now_add=True)
    date_lecture = models.DateTimeField('Date de lecture', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f'{self.get_type_display()} - {self.utilisateur.username}'
    
    def marquer_comme_lue(self):
        if not self.est_lue:
            self.est_lue = True
            self.date_lecture = timezone.now()
            self.save(update_fields=['est_lue', 'date_lecture'])
    
    def get_icone(self):
        icons = {
            'demande_validee': 'fa-check-circle',
            'demande_refusee': 'fa-times-circle',
            'demande_en_cours': 'fa-spinner',
            'demande_recue': 'fa-inbox',
            'nouveau_document': 'fa-file-alt',
            'evenement_proche': 'fa-calendar-day',
            'evenement_annule': 'fa-calendar-times',
            'evenement_ajoute': 'fa-calendar-plus',
            'rappel_activation': 'fa-clock',
            'bienvenue': 'fa-handshake',
            'message_forum': 'fa-comment',
            'reponse_demande': 'fa-reply',
            'systeme': 'fa-info-circle',
        }
        return icons.get(self.type, 'fa-bell')
    
    def get_couleur(self):
        colors = {
            'demande_validee': '#28a745',
            'demande_refusee': '#dc3545',
            'demande_en_cours': '#ffc107',
            'demande_recue': '#17a2b8',
            'nouveau_document': '#007bff',
            'evenement_proche': '#fd7e14',
            'evenement_annule': '#dc3545',
            'evenement_ajoute': '#28a745',
            'rappel_activation': '#ffc107',
            'bienvenue': '#28a745',
            'message_forum': '#6f42c1',
            'reponse_demande': '#20c997',
            'systeme': '#6c757d',
        }
        return colors.get(self.type, '#6c757d')


class PreferenceNotification(models.Model):
    """
    Préférences de notification de l'utilisateur
    """
    utilisateur = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='preferences_notifications',
        verbose_name='Utilisateur'
    )
    email_notifications = models.BooleanField(
        'Notifications par email', 
        default=True
    )
    push_notifications = models.BooleanField(
        'Notifications sur le site', 
        default=True
    )
    email_resume_quotidien = models.BooleanField(
        'Résumé quotidien par email', 
        default=False
    )
    types_actives = models.JSONField(
        'Types de notifications actives',
        default=list,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Préférence de notification'
        verbose_name_plural = 'Préférences de notifications'
    
    def __str__(self):
        return f'Préférences de {self.utilisateur.username}'