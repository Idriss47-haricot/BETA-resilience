"""
Modèles pour la gestion des membres de BETA-Résilience
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
import os
import secrets
from django.utils import timezone
from django.contrib.auth.models import User

class Fonction(models.Model):
    """
    Fonctions des membres (Président, Secrétaire, etc.)
    """
    nom = models.CharField('Nom de la fonction', max_length=100)
    ordre = models.IntegerField('Ordre d\'affichage', default=0)
    est_actif = models.BooleanField('Actif', default=True)
    
    class Meta:
        verbose_name = 'Fonction'
        verbose_name_plural = 'Fonctions'
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom


class Membre(models.Model):
    """
    Membre de BETA-Résilience
    """
    # Informations personnelles
    nom = models.CharField('Nom', max_length=100)
    prenom = models.CharField('Prénom', max_length=100)
    photo = models.ImageField('Photo', upload_to='membres/', blank=True, null=True)
    
    # Fonction et statut
    fonction = models.ForeignKey(
        Fonction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Fonction'
    )
    statut = models.CharField('Statut', max_length=100, blank=True)
    biographie = models.TextField('Biographie', blank=True)
    
    # Contact
    email = models.EmailField('Email', blank=True)
    telephone = models.CharField('Téléphone', max_length=50, blank=True)
    
    # Informations d'adhésion
    date_adhesion = models.DateField('Date d\'adhésion', auto_now_add=True)
    est_actif = models.BooleanField('Membre actif', default=True)
    est_membre_bureau = models.BooleanField('Membre du Bureau Exécutif', default=False)
    
    # ===== NOUVEAUX CHAMPS POUR L'ACTIVATION =====
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='profil_membre',
        verbose_name='Utilisateur associé'
    )
    token_activation = models.CharField(
        'Token d\'activation', 
        max_length=255, 
        blank=True, 
        null=True
    )
    token_expiration = models.DateTimeField(
        'Date d\'expiration du token', 
        null=True, 
        blank=True
    )
    est_compte_active = models.BooleanField(
        'Compte activé', 
        default=False
    )
    date_validation = models.DateTimeField(
        'Date de validation', 
        null=True, 
        blank=True
    )
    date_invitation = models.DateTimeField(
        'Date d\'envoi de l\'invitation', 
        null=True, 
        blank=True
    )
    email_envoye = models.BooleanField(
    'Email envoyé', 
    default=False
    )
    date_acceptation = models.DateTimeField(
        'Date d\'acceptation', 
        null=True, 
        blank=True
    )
    # ===== FIN NOUVEAUX CHAMPS =====
    
    # Réseaux sociaux (optionnels)
    linkedin = models.URLField('LinkedIn', blank=True)
    twitter = models.URLField('Twitter', blank=True)
    researchgate = models.URLField('ResearchGate', blank=True)
    google_scholar = models.URLField('Google Scholar', blank=True)
    
    # Slug pour l'URL
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'
        ordering = ['-est_membre_bureau', 'fonction__ordre', 'nom', 'prenom']
    
    def __str__(self):
        return f'{self.prenom} {self.nom}'
    
    def save(self, *args, **kwargs):
        # Générer le slug automatiquement
        if not self.slug:
            self.slug = slugify(f'{self.prenom}-{self.nom}')
        
        # Optimiser l'image
        super().save(*args, **kwargs)
        if self.photo:
            self.optimiser_image()
    
    def optimiser_image(self):
        """Optimiser l'image pour le web"""
        try:
            img_path = self.photo.path
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            img.save(img_path, 'JPEG', quality=85, optimize=True)
        except Exception:
            pass
    
    def get_absolute_url(self):
        return reverse('membres:detail', kwargs={'slug': self.slug})
    
    def nom_complet(self):
        return f'{self.prenom} {self.nom}'
    
    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/images/default-avatar.png'
    
    # ===== MÉTHODES POUR L'ACTIVATION =====
    def generer_token_activation(self):
        """Générer un token d'activation unique"""
        self.token_activation = secrets.token_urlsafe(32)
        self.token_expiration = timezone.now() + timezone.timedelta(hours=48)
        self.date_invitation = timezone.now()
        self.save(update_fields=['token_activation', 'token_expiration', 'date_invitation'])
        return self.token_activation
    
    def verifier_token_activation(self, token):
        """Vérifier si le token est valide"""
        if not self.token_activation or not self.token_expiration:
            return False
        if self.token_activation != token:
            return False
        if timezone.now() > self.token_expiration:
            return False
        if self.est_compte_active:
            return False
        return True
    
    def activer_compte(self, user):
        """Activer le compte et associer l'utilisateur"""
        self.user = user
        self.est_compte_active = True
        self.token_activation = None
        self.token_expiration = None
        self.save(update_fields=['user', 'est_compte_active', 'token_activation', 'token_expiration'])
    
    def est_token_expire(self):
        """Vérifier si le token est expiré"""
        if not self.token_expiration:
            return True
        return timezone.now() > self.token_expiration
    
    def get_token_expiration_display(self):
        """Afficher le temps restant avant expiration"""
        if not self.token_expiration:
            return 'Expiré'
        delta = self.token_expiration - timezone.now()
        if delta.total_seconds() < 0:
            return 'Expiré'
        heures = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        return f'{heures}h {minutes}min'


class DemandeAdhesion(models.Model):
    """
    Demande d'adhésion au Groupe BETA-Résilience
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('en_cours', 'En cours de traitement'),
        ('invitation_envoyee', 'Invitation envoyée'),
        ('compte_active', 'Compte activé'),
    ]
    
    # Informations personnelles
    nom = models.CharField('Nom', max_length=100)
    prenom = models.CharField('Prénom', max_length=100)
    email = models.EmailField('Email')
    telephone = models.CharField('Téléphone', max_length=50)
    date_naissance = models.DateField('Date de naissance', null=True, blank=True)
    profession = models.CharField('Profession', max_length=200, blank=True)
    
    # Informations d'adhésion
    motivation = models.TextField('Motivation')
    competences = models.TextField('Compétences et domaines d\'expertise', blank=True)
    
    # CV et documents (optionnel)
    cv = models.FileField('CV', upload_to='adhesions/cv/', blank=True, null=True)
    lettre_motivation = models.FileField('Lettre de motivation', upload_to='adhesions/lettres/', blank=True, null=True)
    
    # Statut
    statut = models.CharField('Statut', max_length=20, choices=STATUT_CHOICES, default='en_attente')
    commentaire_admin = models.TextField('Commentaire de l\'administrateur', blank=True)
    
    # Lien vers le membre créé
    membre = models.OneToOneField(
        Membre, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='demande_adhesion',
        verbose_name='Membre associé'
    )
    
    # Timestamps
    date_soumission = models.DateTimeField('Date de soumission', auto_now_add=True)
    date_traitement = models.DateTimeField('Date de traitement', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Demande d\'adhésion'
        verbose_name_plural = 'Demandes d\'adhésion'
        ordering = ['-date_soumission']
    
    def __str__(self):
        return f'Demande de {self.prenom} {self.nom} ({self.get_statut_display()})'
    
    def est_pending(self):
        return self.statut == 'en_attente'
    
    def peut_etre_acceptee(self):
        """Vérifier si la demande peut être acceptée"""
        return self.statut in ['en_attente', 'en_cours']
    
    def peut_etre_refusee(self):
        """Vérifier si la demande peut être refusée"""
        return self.statut in ['en_attente', 'en_cours']
    
    def accepter(self):
        """Accepter la demande et créer le membre"""
        from django.utils import timezone
        
        # Créer le membre
        membre = Membre.objects.create(
            nom=self.nom,
            prenom=self.prenom,
            email=self.email,
            telephone=self.telephone,
            est_actif=True,
            date_validation=timezone.now(),
        )
        
        # Générer le token d'activation
        membre.generer_token_activation()
        
        # Lier le membre à la demande
        self.membre = membre
        self.statut = 'acceptee'
        self.date_traitement = timezone.now()
        self.save()
        
        return membre
    
    def refuser(self, commentaire=''):
        """Refuser la demande"""
        from django.utils import timezone
        self.statut = 'refusee'
        self.date_traitement = timezone.now()
        if commentaire:
            self.commentaire_admin = commentaire
        self.save()
    
    def renvoyer_invitation(self):
        """Renvoyer l'invitation avec un nouveau token"""
        if self.membre:
            self.membre.generer_token_activation()
            return self.membre.token_activation
        return None
    
class HistoriqueEmail(models.Model):
    """
    Historique des emails envoyés aux membres
    """
    TYPE_CHOICES = [
        ('invitation', 'Invitation à activer le compte'),
        ('rappel', 'Rappel d\'activation'),
        ('confirmation', 'Confirmation d\'activation'),
        ('refus', 'Refus de la demande'),
        ('validation', 'Validation de la demande'),
    ]
    
    STATUT_CHOICES = [
        ('envoye', 'Envoyé'),
        ('erreur', 'Erreur'),
        ('en_attente', 'En attente'),
    ]
    
    membre = models.ForeignKey(
        Membre, 
        on_delete=models.CASCADE, 
        related_name='historique_emails',
        verbose_name='Membre'
    )
    demande = models.ForeignKey(
        'DemandeAdhesion', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='historique_emails',
        verbose_name='Demande associée'
    )
    type_email = models.CharField('Type d\'email', max_length=20, choices=TYPE_CHOICES)
    sujet = models.CharField('Sujet', max_length=255)
    destinataire = models.EmailField('Destinataire')
    contenu = models.TextField('Contenu', blank=True)
    token = models.CharField('Token associé', max_length=255, blank=True, null=True)
    statut = models.CharField('Statut', max_length=20, choices=STATUT_CHOICES, default='envoye')
    message_erreur = models.TextField('Message d\'erreur', blank=True)
    date_envoi = models.DateTimeField('Date d\'envoi', auto_now_add=True)
    ip_admin = models.GenericIPAddressField('IP de l\'admin', null=True, blank=True)
    admin_nom = models.CharField('Nom de l\'admin', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Historique d\'email'
        verbose_name_plural = 'Historique des emails'
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f'{self.get_type_email_display()} - {self.destinataire} ({self.date_envoi.strftime("%d/%m/%Y %H:%M")})'