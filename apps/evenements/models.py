"""
Modèles pour l'application Événements
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone


class Evenement(models.Model):
    """
    Événement organisé par BETA-Résilience
    """
    TYPE_CHOICES = [
        ('conference', 'Conférence'),
        ('atelier', 'Atelier'),
        ('webinaire', 'Webinaire'),
        ('sortie_terrain', 'Sortie terrain'),
        ('assemblee', 'Assemblée générale'),
        ('reunion', 'Réunion'),
        ('formation', 'Formation'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('a_venir', 'À venir'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
        ('reporte', 'Reporté'),
    ]
    
    # Informations générales
    titre = models.CharField('Titre', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    type_evenement = models.CharField('Type d\'événement', max_length=20, choices=TYPE_CHOICES)
    description = models.TextField('Description')
    programme = models.TextField('Programme', blank=True)
    
    # Dates et lieu
    date_debut = models.DateTimeField('Date de début')
    date_fin = models.DateTimeField('Date de fin')
    lieu = models.CharField('Lieu', max_length=300)
    adresse = models.TextField('Adresse complète', blank=True)
    
    # Capacité
    capacite_max = models.PositiveIntegerField('Capacité maximale', default=50)
    places_restantes = models.PositiveIntegerField('Places restantes', default=50)
    
    # Image
    image = models.ImageField('Image de l\'événement', upload_to='evenements/', blank=True, null=True)
    
    # Statut
    statut = models.CharField('Statut', max_length=20, choices=STATUT_CHOICES, default='a_venir')
    est_publie = models.BooleanField('Publié', default=True)
    est_gratuit = models.BooleanField('Gratuit', default=True)
    prix = models.DecimalField('Prix (FCFA)', max_digits=10, decimal_places=0, default=0)
    
    # Intervenants
    intervenants = models.TextField('Intervenants', blank=True)
    
    # Document
    document = models.FileField('Document associé', upload_to='evenements/documents/', blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'
        ordering = ['date_debut']
    
    def __str__(self):
        return f'{self.titre} ({self.date_debut.strftime("%d/%m/%Y")})'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('evenements:detail', kwargs={'slug': self.slug})
    
    def get_nb_inscriptions(self):
        return self.inscriptions.filter(statut='confirme').count()


class InscriptionEvenement(models.Model):
    """
    Inscription d'un membre à un événement
    """
    STATUT_CHOICES = [
        ('confirme', 'Confirmé'),
        ('en_attente', 'En attente'),
        ('annule', 'Annulé'),
        ('liste_attente', 'Liste d\'attente'),
    ]
    
    evenement = models.ForeignKey(
        Evenement,
        on_delete=models.CASCADE,
        related_name='inscriptions',
        verbose_name='Événement'
    )
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inscriptions_evenements',
        verbose_name='Utilisateur'
    )
    statut = models.CharField('Statut', max_length=20, choices=STATUT_CHOICES, default='confirme')
    date_inscription = models.DateTimeField('Date d\'inscription', auto_now_add=True)
    commentaire = models.TextField('Commentaire', blank=True)
    
    class Meta:
        verbose_name = 'Inscription à un événement'
        verbose_name_plural = 'Inscriptions aux événements'
        unique_together = ['evenement', 'utilisateur']
        ordering = ['date_inscription']
    
    def __str__(self):
        return f'{self.utilisateur.username} - {self.evenement.titre}'