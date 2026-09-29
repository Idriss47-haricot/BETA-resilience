"""
Administration de l'application Documents
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from apps.core.admin import admin_site  # ✅ IMPORT
from apps.documents.models import CategorieDocument, Document, DocumentVersion
import csv

@admin.register(CategorieDocument)
class CategorieDocumentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'ordre', 'get_documents_count', 'est_publique')
    list_filter = ('est_publique',)
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ('ordre', 'nom')
    
    def get_documents_count(self, obj):
        count = obj.get_documents_count()
        return format_html('<span class="badge bg-success">{}</span>', count)
    get_documents_count.short_description = 'Nb documents'


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    fields = ('version', 'fichier', 'size_display', 'date_creation')
    readonly_fields = ('size_display', 'date_creation')
    
    def size_display(self, obj):
        return obj.size_display if obj else '-'
    size_display.short_description = 'Taille'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'titre',
        'categorie',
        'version',
        'get_file_icon',
        'size_display',
        'nb_telechargements',
        'est_publie',
        'est_recent_badge',
        'get_download_link'
    )
    list_filter = ('categorie', 'est_publie', 'est_telechargeable', 'accessible_aux_membres_seulement', 'date_publication')
    search_fields = ('titre', 'description', 'slug')
    prepopulated_fields = {'slug': ('titre',)}
    ordering = ('categorie', 'ordre', 'titre')
    inlines = [DocumentVersionInline]
    
    fieldsets = (
        ('📄 Informations générales', {
            'fields': ('titre', 'slug', 'description', 'categorie')
        }),
        ('📁 Fichier', {
            'fields': ('fichier', 'version')
        }),
        ('📊 Métadonnées', {
            'fields': ('taille', 'type_fichier', 'nom_fichier_original'),
            'classes': ('collapse',)
        }),
        ('⚙️ Paramètres', {
            'fields': ('ordre', 'est_publie', 'est_telechargeable', 'est_en_avant', 'accessible_aux_membres_seulement')
        }),
        ('📈 Statistiques', {
            'fields': ('nb_telechargements', 'date_publication', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('taille', 'type_fichier', 'nom_fichier_original', 'nb_telechargements', 'date_publication', 'date_modification')
    
    def get_file_icon(self, obj):
        return format_html(
            '<i class="fas {}" style="font-size: 1.5rem; color: #2E7D32;"></i>',
            obj.extension_icon
        )
    get_file_icon.short_description = 'Type'
    
    def size_display(self, obj):
        return obj.size_display if obj else '-'
    size_display.short_description = 'Taille'
    
    def get_download_link(self, obj):
        if obj.fichier:
            return format_html(
                '<a href="{}" target="_blank" class="btn btn-success btn-sm">'
                '<i class="fas fa-download"></i> Télécharger'
                '</a>',
                obj.fichier.url
            )
        return '-'
    get_download_link.short_description = 'Télécharger'
    
    def est_recent_badge(self, obj):
        if obj.est_recent:
            return format_html('<span class="badge bg-success">Nouveau</span>')
        return '-'
    est_recent_badge.short_description = 'Récent'
    
    actions = ['exporter_csv', 'marquer_publie', 'marquer_non_publie', 'reset_telechargements']
    
    def exporter_csv(self, request, queryset):
        """Exporter les documents en CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="documents.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Titre', 'Catégorie', 'Version', 'Taille', 'Téléchargements', 'Publié', 'Date'])
        
        for doc in queryset:
            writer.writerow([
                doc.titre,
                doc.categorie.nom,
                doc.version,
                doc.size_display,
                doc.nb_telechargements,
                'Oui' if doc.est_publie else 'Non',
                doc.date_publication.strftime('%d/%m/%Y')
            ])
        
        return response
    exporter_csv.short_description = '📊 Exporter en CSV'
    
    def marquer_publie(self, request, queryset):
        queryset.update(est_publie=True)
        self.message_user(request, f'{queryset.count()} document(s) publié(s).')
    marquer_publie.short_description = '📤 Publier les documents sélectionnés'
    
    def marquer_non_publie(self, request, queryset):
        queryset.update(est_publie=False)
        self.message_user(request, f'{queryset.count()} document(s) dépublié(s).')
    marquer_non_publie.short_description = '📥 Dépublier les documents sélectionnés'
    
    def reset_telechargements(self, request, queryset):
        for doc in queryset:
            doc.nb_telechargements = 0
            doc.save(update_fields=['nb_telechargements'])
        self.message_user(request, f'Compteurs réinitialisés pour {queryset.count()} document(s).')
    reset_telechargements.short_description = '🔄 Réinitialiser les compteurs'