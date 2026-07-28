"""
Modèles pour la gestion des actualités, blog et événements - Version finale
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from apps.membres.models import Membre
from django.core.exceptions import ValidationError
from django.utils import timezone


class CategorieActualite(models.Model):
    """
    Catégorie d'actualité (Blog, Actualité, Événement, etc.)
    """
    nom = models.CharField('Nom', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    icone = models.CharField('Icône Font Awesome', max_length=100, default='fas fa-tag')
    couleur = models.CharField('Couleur', max_length=20, default='#2E7D32', help_text='Code hexadécimal')
    ordre = models.IntegerField('Ordre d\'affichage', default=0)
    est_active = models.BooleanField('Active', default=True)
    
    class Meta:
        verbose_name = 'Catégorie d\'actualité'
        verbose_name_plural = 'Catégories d\'actualités'
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('actualites:categorie', kwargs={'slug': self.slug})


class Article(models.Model):
    """
    Article de blog ou actualité
    """
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé'),
        ('programme', 'Programmé'),
    ]
    
    # Informations générales
    titre = models.CharField('Titre', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    contenu = RichTextField('Contenu', config_name='default')
    extrait = models.TextField('Extrait', max_length=300, blank=True)
    
    # Images et médias
    image_couverture = models.ImageField(
        'Image de couverture', 
        upload_to='actualites/%Y/%m/',
        blank=True, 
        null=True,
        help_text='Image principale de l\'article (format 16:9 recommandé)'
    )
    images_supplementaires = models.JSONField('Images supplémentaires', blank=True, default=list)
    video = models.URLField('Lien vidéo (YouTube)', blank=True)
    
    # Métadonnées
    categories = models.ManyToManyField(
        CategorieActualite, 
        related_name='articles', 
        verbose_name='Catégories', 
        blank=True
    )
    auteur = models.ForeignKey(
        Membre, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='articles', 
        verbose_name='Auteur'
    )
    
    # Dates
    date_publication = models.DateTimeField('Date de publication', auto_now_add=True)
    date_modification = models.DateTimeField('Date de modification', auto_now=True)
    date_evenement = models.DateField('Date de l\'événement (si applicable)', null=True, blank=True)
    date_programmation = models.DateTimeField('Date de programmation', null=True, blank=True)
    
    # Statut
    statut = models.CharField('Statut', max_length=20, choices=STATUT_CHOICES, default='brouillon')
    est_publie = models.BooleanField('Publié', default=True)
    est_a_la_une = models.BooleanField('À la une', default=False)
    est_en_avant = models.BooleanField('En avant', default=False)
    
    # Tags pour le référencement
    tags = models.CharField('Tags (séparés par des virgules)', max_length=500, blank=True)
    
    # Statistiques
    nb_vues = models.PositiveIntegerField('Nombre de vues', default=0)
    nb_partages = models.PositiveIntegerField('Nombre de partages', default=0)
    nb_commentaires = models.PositiveIntegerField('Nombre de commentaires', default=0)
    
    # Métadonnées SEO
    meta_titre = models.CharField('Titre SEO', max_length=200, blank=True)
    meta_description = models.TextField('Description SEO', max_length=300, blank=True)
    meta_keywords = models.CharField('Mots-clés SEO', max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-date_publication']
        get_latest_by = 'date_publication'
        indexes = [
            models.Index(fields=['slug', 'est_publie']),
            models.Index(fields=['date_publication']),
        ]
    
    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        
        # Générer l'extrait automatiquement si vide
        if not self.extrait and self.contenu:
            from django.utils.html import strip_tags
            self.extrait = strip_tags(self.contenu)[:300] + '...'
        
        # Gérer la publication programmée
        if self.statut == 'programme' and self.date_programmation:
            if self.date_programmation <= timezone.now():
                self.statut = 'publie'
                self.est_publie = True
            else:
                self.est_publie = False
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('actualites:detail', kwargs={'slug': self.slug})
    
    def incrementer_vues(self):
        """Incrémenter le compteur de vues"""
        self.nb_vues += 1
        self.save(update_fields=['nb_vues', 'updated_at'])
    
    def incrementer_commentaires(self):
        """Incrémenter le compteur de commentaires"""
        self.nb_commentaires += 1
        self.save(update_fields=['nb_commentaires'])
    
    @property
    def is_evenement(self):
        """Vérifier si c'est un événement"""
        return self.categories.filter(nom__icontains='Événement').exists()
    
    @property
    def is_blog(self):
        """Vérifier si c'est un article de blog"""
        return self.categories.filter(nom__icontains='Blog').exists()
    
    @property
    def is_actualite(self):
        """Vérifier si c'est une actualité"""
        return self.categories.filter(nom__icontains='Actualité').exists()
    
    @property
    def temps_lecture(self):
        """Estimer le temps de lecture en minutes"""
        from django.utils.html import strip_tags
        content = strip_tags(self.contenu)
        words = len(content.split())
        return max(1, round(words / 200))  # 200 mots par minute
    
    @property
    def status_badge(self):
        """Retourner le badge de statut"""
        colors = {
            'brouillon': 'secondary',
            'publie': 'success',
            'archive': 'danger',
            'programme': 'warning',
        }
        return colors.get(self.statut, 'secondary')


class Commentaire(models.Model):
    """
    Commentaire sur un article
    """
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        related_name='commentaires', 
        verbose_name='Article'
    )
    auteur = models.CharField('Nom', max_length=100)
    email = models.EmailField('Email')
    site_web = models.URLField('Site web', blank=True)
    contenu = models.TextField('Commentaire')
    est_approuve = models.BooleanField('Approuvé', default=False)
    est_signale = models.BooleanField('Signalé', default=False)
    ip_address = models.GenericIPAddressField('Adresse IP', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    date_creation = models.DateTimeField('Créé le', auto_now_add=True)
    date_modification = models.DateTimeField('Modifié le', auto_now=True)
    
    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f'Commentaire de {self.auteur} sur {self.article.titre}'
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and self.est_approuve:
            self.article.incrementer_commentaires()