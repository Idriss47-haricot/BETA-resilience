from django.db import models

# Create your models here.
"""
Modèles pour l'application Forums
"""

from django.contrib.auth.models import User
from django.utils.text import slugify


class ForumCategorie(models.Model):
    """
    Catégorie de forum
    """
    nom = models.CharField('Nom', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    icone = models.CharField('Icône Font Awesome', max_length=50, default='fas fa-comments')
    ordre = models.IntegerField('Ordre d\'affichage', default=0)
    est_active = models.BooleanField('Active', default=True)
    
    class Meta:
        verbose_name = 'Catégorie de forum'
        verbose_name_plural = 'Catégories de forums'
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('forums:categorie', kwargs={'slug': self.slug})
    
    def get_nb_sujets(self):
        return self.sujets.filter(est_ferme=False).count()


class ForumSujet(models.Model):
    """
    Sujet de discussion
    """
    titre = models.CharField('Titre', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    categorie = models.ForeignKey(
        ForumCategorie,
        on_delete=models.CASCADE,
        related_name='sujets',
        verbose_name='Catégorie'
    )
    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sujets_forum',
        verbose_name='Auteur'
    )
    contenu = models.TextField('Contenu')
    est_epingle = models.BooleanField('Épinglé', default=False)
    est_ferme = models.BooleanField('Fermé', default=False)
    nb_vues = models.PositiveIntegerField('Nombre de vues', default=0)
    date_creation = models.DateTimeField('Date de création', auto_now_add=True)
    date_modification = models.DateTimeField('Date de modification', auto_now=True)
    dernier_message = models.DateTimeField('Dernier message', auto_now=True)
    
    class Meta:
        verbose_name = 'Sujet de forum'
        verbose_name_plural = 'Sujets de forum'
        ordering = ['-est_epingle', '-dernier_message']
    
    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('forums:sujet_detail', kwargs={'slug': self.slug})
    
    def get_nb_messages(self):
        return self.messages.count()
    
    def get_dernier_message(self):
        return self.messages.order_by('-date_creation').first()
    
    def incrementer_vues(self):
        self.nb_vues += 1
        self.save(update_fields=['nb_vues'])


class ForumMessage(models.Model):
    """
    Message dans un sujet
    """
    sujet = models.ForeignKey(
        ForumSujet,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Sujet'
    )
    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_forum',
        verbose_name='Auteur'
    )
    contenu = models.TextField('Contenu')
    est_edite = models.BooleanField('Édité', default=False)
    date_creation = models.DateTimeField('Date de création', auto_now_add=True)
    date_modification = models.DateTimeField('Date de modification', auto_now=True)
    
    class Meta:
        verbose_name = 'Message de forum'
        verbose_name_plural = 'Messages de forum'
        ordering = ['date_creation']
    
    def __str__(self):
        return f'Message de {self.auteur.username} dans {self.sujet.titre[:30]}'
    
    def get_absolute_url(self):
        return f"{self.sujet.get_absolute_url()}#message-{self.pk}"