"""
Modèles pour la gestion des demandes des entités
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Demande(models.Model):
    """
    Demande soumise par un utilisateur pour une entité
    """
    ENTITE_CHOICES = [
        ('association', 'BETA-Résilience Association'),
        ('bureau_etude', 'BETA-Résilience Bureau d\'étude'),
        ('invest', 'BETA-Résilience INVEST'),
        ('laboratoire', 'Laboratoire Résilience'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de traitement'),
        ('traite', 'Traité'),
        ('rejete', 'Rejeté'),
    ]
    
    # Types de demande par entité
    TYPE_CHOICES = {
        'association': [
            ('adhesion', 'Adhésion'),
            ('benefice', 'Bénévolat'),
            ('don', 'Don'),
            ('partenariat', 'Partenariat associatif'),
            ('information', 'Demande d\'information'),
        ],
        'bureau_etude': [
            ('etude', 'Étude environnementale'),
            ('expertise', 'Expertise technique'),
            ('conseil', 'Conseil stratégique'),
            ('formation', 'Formation'),
            ('prestation', 'Prestation de service'),
        ],
        'invest': [
            ('investissement', 'Investissement'),
            ('partenariat', 'Partenariat économique'),
            ('financement', 'Financement de projet'),
            ('conseil', 'Conseil en investissement'),
        ],
        'laboratoire': [
            ('collaboration', 'Collaboration scientifique'),
            ('recherche', 'Projet de recherche'),
            ('publication', 'Publication scientifique'),
            ('stage', 'Stage / Recherche'),
            ('partenariat', 'Partenariat académique'),
        ],
    }
    
    # Informations générales
    entite = models.CharField('Entité concernée', max_length=20, choices=ENTITE_CHOICES)
    type_demande = models.CharField('Type de demande', max_length=50)
    autre_type = models.CharField('Autre type (précisez)', max_length=100, blank=True)
    
    # Informations personnelles
    nom = models.CharField('Nom', max_length=100)
    prenom = models.CharField('Prénom', max_length=100)
    email = models.EmailField('Email')
    telephone = models.CharField('Téléphone', max_length=50)
    
    # Informations professionnelles
    societe = models.CharField('Société / Institution', max_length=200, blank=True)
    fonction = models.CharField('Fonction', max_length=100, blank=True)
    
    # Message
    objet = models.CharField('Objet de la demande', max_length=200)
    message = models.TextField('Message')
    
    # Pièce jointe (optionnelle)
    fichier = models.FileField('Document joint', upload_to='demandes/%Y/%m/', blank=True, null=True)
    
    # Statut
    statut = models.CharField('Statut', max_length=20, choices=STATUT_CHOICES, default='en_attente')
    commentaire_admin = models.TextField('Commentaire de l\'administrateur', blank=True)
    
    # IP et métadonnées
    ip_address = models.GenericIPAddressField('Adresse IP', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    
    # Timestamps
    date_soumission = models.DateTimeField('Date de soumission', auto_now_add=True)
    date_traitement = models.DateTimeField('Date de traitement', null=True, blank=True)
    date_modification = models.DateTimeField('Date de modification', auto_now=True)
    
    class Meta:
        verbose_name = 'Demande'
        verbose_name_plural = 'Demandes'
        ordering = ['-date_soumission']
    
    def __str__(self):
        return f'{self.get_entite_display()} - {self.prenom} {self.nom} ({self.get_statut_display()})'
    
    def get_absolute_url(self):
        return reverse('demandes:detail', kwargs={'pk': self.pk})
    
    def get_type_demande_display(self):
        """Retourner le libellé du type de demande"""
        types = self.TYPE_CHOICES.get(self.entite, [])
        for value, label in types:
            if value == self.type_demande:
                return label
        return self.type_demande
    
    def get_type_choices(self):
        """Retourner les types de demande pour l'entité sélectionnée"""
        return self.TYPE_CHOICES.get(self.entite, [])
    
    @property
    def nom_complet(self):
        return f'{self.prenom} {self.nom}'
    
    @property
    def entite_icone(self):
        """Retourner l'icône de l'entité"""
        icons = {
            'association': 'fa-users',
            'bureau_etude': 'fa-building',
            'invest': 'fa-chart-line',
            'laboratoire': 'fa-flask',
        }
        return icons.get(self.entite, 'fa-question-circle')
    
    @property
    def entite_couleur(self):
        """Retourner la couleur de l'entité"""
        colors = {
            'association': '#2E7D32',
            'bureau_etude': '#1565C0',
            'invest': '#E65100',
            'laboratoire': '#6A1B9A',
        }
        return colors.get(self.entite, '#757575')
    
    @property
    def entite_badge(self):
        """Retourner le badge HTML de l'entité"""
        from django.utils.html import format_html
        return format_html(
            '<span style="background:{};color:white;padding:3px 12px;border-radius:12px;font-size:11px;">{}</span>',
            self.entite_couleur,
            self.get_entite_display()
        )