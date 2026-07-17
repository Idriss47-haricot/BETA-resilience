"""
Administration de l'application Projets
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from apps.core.admin import admin_site  # ✅ IMPORT DU ADMIN PERSONNALISÉ
from apps.projets.models import CategorieProjet, Projet, ProjetEtape
import csv


@admin.register(CategorieProjet, site=admin_site)  # ✅ site=admin_site
class CategorieProjetAdmin(admin.ModelAdmin):
    """
    Gestion des catégories de projets
    """
    list_display = ('nom', 'slug', 'icone_preview', 'ordre')
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ('ordre', 'nom')
    
    def icone_preview(self, obj):
        return format_html('<i class="{}" style="font-size: 16px; color: #2E7D32;"></i>', obj.icone)
    icone_preview.short_description = 'Icône'


class ProjetEtapeInline(admin.TabularInline):
    """
    Affichage des étapes d'un projet en ligne
    """
    model = ProjetEtape
    extra = 0
    fields = ('titre', 'description', 'date_debut', 'date_fin', 'est_realisee', 'ordre')
    ordering = ('ordre',)


@admin.register(Projet, site=admin_site)  # ✅ site=admin_site
class ProjetAdmin(admin.ModelAdmin):
    """
    Gestion des projets
    """
    list_display = (
        'titre',
        'statut_badge',
        'date_debut',
        'date_fin',
        'est_publie',
        'est_mis_en_avant',
        'get_image_preview'
    )
    list_filter = ('statut', 'est_publie', 'est_mis_en_avant', 'categories', 'date_debut')
    search_fields = ('titre', 'description_courte', 'description_longue')
    prepopulated_fields = {'slug': ('titre',)}
    filter_horizontal = ('categories', 'partenaires')
    ordering = ('-date_debut',)
    inlines = [ProjetEtapeInline]
    
    fieldsets = (
        ('📝 Informations générales', {
            'fields': ('titre', 'slug', 'description_courte', 'description_longue')
        }),
        ('🖼️ Images', {
            'fields': ('image_principale',)
        }),
        ('📅 Dates', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('⚙️ Statut', {
            'fields': ('statut', 'est_termine', 'est_publie', 'est_mis_en_avant')
        }),
        ('📂 Catégories et partenaires', {
            'fields': ('categories', 'partenaires')
        }),
        ('🔗 Liens', {
            'fields': ('lien_externe', 'document_projet')
        }),
        ('🔍 SEO', {
            'fields': ('meta_titre', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    # ✅ Champs auto_now_add/auto_now en lecture seule
    readonly_fields = ('created_at', 'updated_at')
    
    def get_image_preview(self, obj):
        if obj.image_principale:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;"/>',
                obj.image_principale.url
            )
        return '-'
    get_image_preview.short_description = 'Image'
    
    def statut_badge(self, obj):
        """Afficher le statut avec une couleur"""
        colors = {
            'en_cours': '#28a745',
            'boucle': '#6c757d',
            'suspendu': '#dc3545',
            'en_attente': '#ffc107',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;">{}</span>',
            colors.get(obj.statut, '#6c757d'),
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'
    
    actions = ['publier_selection', 'depublier_selection', 'exporter_projets']
    
    def publier_selection(self, request, queryset):
        count = queryset.update(est_publie=True)
        self.message_user(request, f'{count} projet(s) publié(s).')
    publier_selection.short_description = '📤 Publier les projets sélectionnés'
    
    def depublier_selection(self, request, queryset):
        count = queryset.update(est_publie=False)
        self.message_user(request, f'{count} projet(s) dépublié(s).')
    depublier_selection.short_description = '📥 Dépublier les projets sélectionnés'
    
    def exporter_projets(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projets.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Titre', 'Statut', 'Date début', 'Date fin', 'Publié', 'Catégories'])
        
        for projet in queryset:
            categories = ', '.join([cat.nom for cat in projet.categories.all()])
            writer.writerow([
                projet.titre,
                projet.get_statut_display(),
                projet.date_debut.strftime('%d/%m/%Y'),
                projet.date_fin.strftime('%d/%m/%Y') if projet.date_fin else '',
                'Oui' if projet.est_publie else 'Non',
                categories
            ])
        
        return response
    exporter_projets.short_description = '📊 Exporter les projets en CSV'


@admin.register(ProjetEtape, site=admin_site)  # ✅ site=admin_site
class ProjetEtapeAdmin(admin.ModelAdmin):
    """
    Gestion des étapes de projets
    """
    list_display = ('titre', 'projet', 'date_debut', 'date_fin', 'est_realisee', 'ordre')
    list_filter = ('est_realisee', 'projet')
    search_fields = ('titre', 'description')
    ordering = ('projet', 'ordre', 'date_debut')
    
    fieldsets = (
        ('📝 Informations', {
            'fields': ('projet', 'titre', 'description')
        }),
        ('📅 Dates', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('⚙️ Paramètres', {
            'fields': ('est_realisee', 'ordre')
        }),
    )