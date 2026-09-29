"""
Modèles pour la gestion des contacts et messages
"""
from django.db import models
from django.core.mail import send_mail
from django.conf import settings

class MessageContact(models.Model):
    """
    Message envoyé via le formulaire de contact
    """
    SUJET_CHOICES = [
        ('general', 'Demande générale'),
        ('projet', 'Projet / Collaboration'),
        ('adhesion', 'Adhésion'),
        ('partenariat', 'Partenariat'),
        ('service', 'Demande de service'),
        ('autre', 'Autre'),
    ]
    
    # Informations de l'expéditeur
    nom = models.CharField('Nom', max_length=100)
    prenom = models.CharField('Prénom', max_length=100)
    email = models.EmailField('Email')
    telephone = models.CharField('Téléphone', max_length=50, blank=True)
    
    # Message
    sujet = models.CharField('Sujet', max_length=20, choices=SUJET_CHOICES, default='general')
    sujet_personnalise = models.CharField('Sujet personnalisé', max_length=200, blank=True)
    message = models.TextField('Message')
    
    # Statut
    est_lu = models.BooleanField('Lu', default=False)
    est_repondu = models.BooleanField('Répondu', default=False)
    reponse = models.TextField('Réponse', blank=True)
    
    # IP et métadonnées
    ip_address = models.GenericIPAddressField('Adresse IP', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    
    # Timestamps
    date_envoi = models.DateTimeField('Date d\'envoi', auto_now_add=True)
    date_reponse = models.DateTimeField('Date de réponse', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f'Message de {self.prenom} {self.nom} - {self.get_sujet_display()}'
    
    def get_sujet_complet(self):
        """Retourner le sujet complet"""
        if self.sujet_personnalise:
            return self.sujet_personnalise
        return self.get_sujet_display()
    
    def envoyer_email_notification(self):
        """Envoyer un email de notification à l'administrateur"""
        sujet_email = f'Nouveau message de contact - {self.prenom} {self.nom}'
        message_email = f"""
        Un nouveau message a été envoyé via le formulaire de contact.

        Expéditeur : {self.prenom} {self.nom}
        Email : {self.email}
        Téléphone : {self.telephone}
        Sujet : {self.get_sujet_complet()}

        Message :
        {self.message}

        ---
        Ce message a été envoyé depuis le site BETA-Résilience.
        """
        try:
            send_mail(
                sujet_email,
                message_email,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass  # Ignorer les erreurs d'email