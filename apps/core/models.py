"""
Modèles pour l'application Core - Configuration globale du site
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class SiteConfiguration(models.Model):
    """
    Configuration globale du site
    """
    # Informations générales
    site_name = models.CharField('Nom du site', max_length=100, default='BETA-Résilience')
    site_tagline = models.CharField('Slogan', max_length=200, blank=True)
    
    # Coordonnées
    email = models.EmailField('Email général', blank=True)
    email_contact = models.EmailField('Email de contact', blank=True, help_text='Email pour les formulaires de contact')
    phone = models.CharField('Téléphone', max_length=50, blank=True)
    phone_whatsapp = models.CharField('WhatsApp', max_length=50, blank=True)
    address = models.TextField('Adresse', blank=True)
    boite_postale = models.CharField('Boîte postale', max_length=50, blank=True, default='BP 8085 Yaoundé - Cameroun')
    
    # Réseaux sociaux
    facebook = models.URLField('Facebook', blank=True)
    linkedin = models.URLField('LinkedIn', blank=True)
    twitter = models.URLField('Twitter', blank=True)
    instagram = models.URLField('Instagram', blank=True)
    youtube = models.URLField('YouTube', blank=True)
    whatsapp = models.URLField('WhatsApp', blank=True)
    
    # SEO
    meta_title = models.CharField('Titre SEO', max_length=200, blank=True)
    meta_description = models.TextField('Description SEO', max_length=300, blank=True)
    meta_keywords = models.CharField('Mots-clés SEO', max_length=500, blank=True)
    
    # Design
    primary_color = models.CharField('Couleur principale', max_length=20, default='#2E7D32')
    secondary_color = models.CharField('Couleur secondaire', max_length=20, default='#4CAF50')
    accent_color = models.CharField('Couleur d\'accent', max_length=20, default='#FF6F00')
    
    # Logo
    logo = models.ImageField('Logo', upload_to='site/', blank=True, null=True)
    logo_footer = models.ImageField('Logo pour le footer', upload_to='site/', blank=True, null=True)
    favicon = models.ImageField('Favicon', upload_to='site/', blank=True, null=True)
    
    # Footer
    footer_text = models.TextField('Texte du footer', blank=True)
    copyright_text = models.CharField('Copyright', max_length=200, blank=True)
    
    # Google Analytics
    google_analytics_id = models.CharField('Google Analytics ID', max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuration du site'
        verbose_name_plural = 'Configuration du site'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteConfiguration.objects.exists():
            return
        super().save(*args, **kwargs)


class Page(models.Model):
    """
    Pages statiques du site
    """
    title = models.CharField('Titre', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    content = models.TextField('Contenu')
    
    # Métadonnées
    meta_title = models.CharField('Titre SEO', max_length=200, blank=True)
    meta_description = models.TextField('Description SEO', max_length=300, blank=True)
    
    # Image de couverture
    cover_image = models.ImageField('Image de couverture', upload_to='pages/', blank=True, null=True)
    
    # Ordre d'affichage
    order = models.IntegerField('Ordre', default=0)
    
    # Statut
    is_published = models.BooleanField('Publié', default=True)
    is_in_menu = models.BooleanField('Dans le menu', default=True)
    
    # Timestamps
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:page_detail', kwargs={'slug': self.slug})