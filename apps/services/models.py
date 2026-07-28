"""
Modèles pour la gestion des services de BETA-Résilience
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Service(models.Model):
    """
    Service proposé par BETA-Résilience
    """
    titre = models.CharField('Titre du service', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    description_courte = models.TextField('Description courte', max_length=300)
    description_longue = models.TextField('Description longue', blank=True)
    
    # Icônes (Font Awesome)
    icone = models.CharField('Icône Font Awesome', max_length=100, default='fas fa-cog')
    image = models.ImageField('Image d\'illustration', upload_to='services/', blank=True, null=True)
    
    # Affichage et organisation
    ordre = models.IntegerField('Ordre d\'affichage', default=0)
    est_actif = models.BooleanField('Service actif', default=True)
    est_mis_en_avant = models.BooleanField('Mis en avant sur l\'accueil', default=False)
    
    # Métadonnées SEO
    meta_titre = models.CharField('Titre SEO', max_length=200, blank=True)
    meta_description = models.TextField('Description SEO', max_length=300, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['ordre', 'titre']
    
    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('services:detail', kwargs={'slug': self.slug})


class ServiceAvantage(models.Model):
    """
    Avantages ou caractéristiques d'un service
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='avantages', verbose_name='Service')
    avantage = models.CharField('Avantage', max_length=300)
    ordre = models.IntegerField('Ordre d\'affichage', default=0)
    
    class Meta:
        verbose_name = 'Avantage'
        verbose_name_plural = 'Avantages'
        ordering = ['ordre']
    
    def __str__(self):
        return self.avantage