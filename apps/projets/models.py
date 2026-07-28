"""
Modèles pour la gestion des projets de BETA-Résilience
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from apps.partenaires.models import Partenaire
import os

class CategorieProjet(models.Model):
    """
    Catégorie de projet (Environnement, Social, Économique, etc.)
    """
    nom = models.CharField('Nom', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    icone = models.CharField('Icône Font Awesome', max_length=100, default='fas fa-tag')
    ordre = models.IntegerField('Ordre', default=0)
    
    class Meta:
        verbose_name = 'Catégorie de projet'
        verbose_name_plural = 'Catégories de projets'
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Projet(models.Model):
    """
    Projet réalisé ou en cours par BETA-Résilience
    """
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('boucle', 'Bouclé'),
        ('suspendu', 'Suspendu'),
        ('en_attente', 'En attente de lancement'),
    ]
    
    # Informations générales
    titre = models.CharField('Titre du projet', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    description_courte = models.TextField('Description courte', max_length=300)
    description_longue = models.TextField('Description longue', blank=True)
    
    # Images
    image_principale = models.ImageField('Image principale', upload_to='projets/', blank=True, null=True)
    images_supplementaires = models.JSONField('Images supplémentaires', blank=True, default=list)
    
    # Dates
    date_debut = models.DateField('Date de début')
    date_fin = models.DateField('Date de fin', null=True, blank=True)
    
    # Statut
    statut = models.CharField('Statut', max_length=20, choices=STATUT_CHOICES, default='en_cours')
    est_termine = models.BooleanField('Terminé', default=False)
    est_publie = models.BooleanField('Publié', default=True)
    est_mis_en_avant = models.BooleanField('Mis en avant', default=False)
    
    # Catégorie
    categories = models.ManyToManyField(CategorieProjet, related_name='projets', verbose_name='Catégories', blank=True)
    
    # Partenaires
    partenaires = models.ManyToManyField(Partenaire, related_name='projets', verbose_name='Partenaires', blank=True)
    
    # Lien vers site/projet
    lien_externe = models.URLField('Lien externe', blank=True)
    document_projet = models.FileField('Document du projet', upload_to='projets/documents/', blank=True, null=True)
    
    # Métadonnées SEO
    meta_titre = models.CharField('Titre SEO', max_length=200, blank=True)
    meta_description = models.TextField('Description SEO', max_length=300, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['-date_debut']
    
    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('projets:detail', kwargs={'slug': self.slug})
    
    @property
    def duree_mois(self):
        """Calculer la durée du projet en mois"""
        if not self.date_fin:
            return None
        delta = self.date_fin - self.date_debut
        return delta.days // 30


class ProjetEtape(models.Model):
    """
    Étapes de réalisation d'un projet
    """
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='etapes', verbose_name='Projet')
    titre = models.CharField('Titre de l\'étape', max_length=200)
    description = models.TextField('Description', blank=True)
    date_debut = models.DateField('Date de début')
    date_fin = models.DateField('Date de fin', null=True, blank=True)
    est_realisee = models.BooleanField('Réalisée', default=False)
    ordre = models.IntegerField('Ordre', default=0)
    
    class Meta:
        verbose_name = 'Étape de projet'
        verbose_name_plural = 'Étapes de projet'
        ordering = ['ordre', 'date_debut']
    
    def __str__(self):
        return f'{self.projet.titre} - {self.titre}'