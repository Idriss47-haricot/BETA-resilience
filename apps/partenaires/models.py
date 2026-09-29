"""
Modèles pour la gestion des partenaires
"""
from django.db import models
from django.utils.text import slugify
from PIL import Image

class Partenaire(models.Model):
    """
    Partenaire de BETA-Résilience
    """
    TYPE_CHOICES = [
        ('institutionnel', 'Institutionnel'),
        ('technique', 'Technique'),
        ('financier', 'Financier'),
        ('academique', 'Académique'),
        ('associatif', 'Associatif'),
        ('prive', 'Privé'),
    ]
    
    # Informations générales
    nom = models.CharField('Nom du partenaire', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    
    # Logo et médias
    logo = models.ImageField('Logo', upload_to='partenaires/', blank=True, null=True)
    
    # Contact
    site_web = models.URLField('Site web', blank=True)
    email = models.EmailField('Email', blank=True)
    telephone = models.CharField('Téléphone', max_length=50, blank=True)
    adresse = models.TextField('Adresse', blank=True)
    
    # Type et catégorie
    type_partenaire = models.CharField('Type', max_length=20, choices=TYPE_CHOICES, default='institutionnel')
    
    # Affichage
    est_actif = models.BooleanField('Partenaire actif', default=True)
    est_mis_en_avant = models.BooleanField('Mis en avant', default=False)
    ordre = models.IntegerField('Ordre d\'affichage', default=0)
    
    # Timestamps
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Partenaire'
        verbose_name_plural = 'Partenaires'
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        
        super().save(*args, **kwargs)
        
        # Optimiser le logo
        if self.logo:
            self.optimiser_logo()
    
    def optimiser_logo(self):
        """Optimiser le logo pour le web"""
        try:
            img_path = self.logo.path
            img = Image.open(img_path)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            if img.width > 300 or img.height > 300:
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            img.save(img_path, 'JPEG', quality=85, optimize=True)
        except Exception:
            pass
    
    def get_absolute_url(self):
        return reverse('partenaires:detail', kwargs={'slug': self.slug})