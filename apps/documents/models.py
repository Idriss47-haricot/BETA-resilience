"""
Modèles pour la gestion des documents téléchargeables
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
import os
from datetime import datetime

class CategorieDocument(models.Model):
    """
    Catégorie de document (Statuts, Rapports, Articles, etc.)
    """
    nom = models.CharField('Nom', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    icone = models.CharField('Icône Font Awesome', max_length=100, default='fas fa-folder')
    ordre = models.IntegerField('Ordre d\'affichage', default=0)
    est_publique = models.BooleanField('Visible par tous', default=True)
    
    class Meta:
        verbose_name = 'Catégorie de document'
        verbose_name_plural = 'Catégories de documents'
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def get_documents_count(self):
        return self.documents.filter(est_publie=True).count()


class Document(models.Model):
    """
    Document téléchargeable avec gestion de version
    """
    # Informations générales
    titre = models.CharField('Titre du document', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    
    # Catégorie
    categorie = models.ForeignKey(
        CategorieDocument, 
        on_delete=models.CASCADE, 
        related_name='documents', 
        verbose_name='Catégorie'
    )
    
    # Fichier
    fichier = models.FileField('Fichier', upload_to='documents/%Y/%m/')
    
    # Métadonnées du fichier (remplies automatiquement)
    taille = models.BigIntegerField('Taille (octets)', editable=False, default=0)
    type_fichier = models.CharField('Type de fichier', max_length=50, editable=False, default='')
    nom_fichier_original = models.CharField('Nom original', max_length=200, editable=False, default='')
    
    # Version
    version = models.CharField('Version', max_length=20, default='1.0')
    date_publication = models.DateField('Date de publication', auto_now_add=True)
    date_modification = models.DateField('Date de modification', auto_now=True)
    
    # Affichage
    est_publie = models.BooleanField('Publié', default=True)
    est_telechargeable = models.BooleanField('Téléchargeable', default=True)
    est_en_avant = models.BooleanField('Mis en avant', default=False)
    ordre = models.IntegerField('Ordre d\'affichage', default=0)
    
    # Statistiques
    nb_telechargements = models.PositiveIntegerField('Nombre de téléchargements', default=0)
    
    # Sécurité - Restreindre aux membres connectés
    accessible_aux_membres_seulement = models.BooleanField(
        'Réservé aux membres', 
        default=False,
        help_text='Cocher pour que ce document ne soit accessible qu\'aux membres connectés'
    )
    
    # Timestamps
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['categorie', 'ordre', 'titre']
        indexes = [
            models.Index(fields=['categorie', 'est_publie']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f'{self.titre} (v{self.version})'
    
    def save(self, *args, **kwargs):
        # Générer le slug
        if not self.slug:
            self.slug = slugify(self.titre)
        
        # Mettre à jour les métadonnées du fichier
        if self.fichier:
            try:
                self.taille = self.fichier.size
                extension = os.path.splitext(self.fichier.name)[1][1:].upper()
                self.type_fichier = extension if extension else 'FICHIER'
                self.nom_fichier_original = os.path.basename(self.fichier.name)
            except Exception:
                pass
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('documents:detail', kwargs={'slug': self.slug})
    
    def get_download_url(self):
        return reverse('documents:telecharger', kwargs={'slug': self.slug})
    
    def get_filename(self):
        """Retourner le nom du fichier"""
        return os.path.basename(self.fichier.name) if self.fichier else ''
    
    def incrementer_telechargements(self):
        """Incrémenter le compteur de téléchargements"""
        self.nb_telechargements += 1
        self.save(update_fields=['nb_telechargements'])
    
    @property
    def size_display(self):
        """Afficher la taille en format lisible"""
        size = self.taille
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        elif size < 1024 * 1024 * 1024:
            return f'{size / (1024 * 1024):.1f} MB'
        else:
            return f'{size / (1024 * 1024 * 1024):.1f} GB'
    
    @property
    def extension_icon(self):
        """Retourner l'icône Font Awesome en fonction du type de fichier"""
        ext = self.type_fichier.lower()
        icons = {
            'pdf': 'fa-file-pdf',
            'doc': 'fa-file-word',
            'docx': 'fa-file-word',
            'xls': 'fa-file-excel',
            'xlsx': 'fa-file-excel',
            'ppt': 'fa-file-powerpoint',
            'pptx': 'fa-file-powerpoint',
            'jpg': 'fa-file-image',
            'jpeg': 'fa-file-image',
            'png': 'fa-file-image',
            'gif': 'fa-file-image',
            'zip': 'fa-file-archive',
            'rar': 'fa-file-archive',
            'mp3': 'fa-file-audio',
            'mp4': 'fa-file-video',
            'txt': 'fa-file-alt',
        }
        return icons.get(ext, 'fa-file')
    
    @property
    def est_recent(self):
        """Vérifier si le document a été publié dans les 30 derniers jours"""
        from datetime import timedelta
        from django.utils import timezone
        return self.date_publication >= (timezone.now().date() - timedelta(days=30))


class DocumentVersion(models.Model):
    """
    Historique des versions d'un document
    """
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE, 
        related_name='versions',
        verbose_name='Document'
    )
    version = models.CharField('Version', max_length=20)
    fichier = models.FileField('Fichier', upload_to='documents/versions/%Y/%m/')
    taille = models.BigIntegerField('Taille (octets)', editable=False, default=0)
    notes = models.TextField('Notes de version', blank=True)
    date_creation = models.DateTimeField('Date de création', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Version de document'
        verbose_name_plural = 'Versions de documents'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f'{self.document.titre} - v{self.version}'
    
    def save(self, *args, **kwargs):
        if self.fichier:
            try:
                self.taille = self.fichier.size
            except Exception:
                pass
        super().save(*args, **kwargs)
    
    def get_filename(self):
        return os.path.basename(self.fichier.name) if self.fichier else ''
    
    @property
    def size_display(self):
        size = self.taille
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        elif size < 1024 * 1024 * 1024:
            return f'{size / (1024 * 1024):.1f} MB'
        else:
            return f'{size / (1024 * 1024 * 1024):.1f} GB'