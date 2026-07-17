"""
Administration de l'application Partenaires
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin import admin_site  # ✅ IMPORT DU ADMIN PERSONNALISÉ
from apps.partenaires.models import Partenaire


@admin.register(Partenaire, site=admin_site)  # ✅ site=admin_site
class PartenaireAdmin(admin.ModelAdmin):
    """
    Gestion des partenaires
    """
    list_display = (
        'nom', 
        'type_partenaire', 
        'est_actif', 
        'est_mis_en_avant', 
        'ordre', 
        'get_logo_preview'
    )
    list_filter = ('type_partenaire', 'est_actif', 'est_mis_en_avant')
    search_fields = ('nom', 'description', 'email', 'telephone')
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ('ordre', 'nom')
    
    fieldsets = (
        ('🏢 Informations générales', {
            'fields': ('nom', 'slug', 'description')
        }),
        ('🖼️ Logo', {
            'fields': ('logo',)
        }),
        ('📞 Contact', {
            'fields': ('site_web', 'email', 'telephone', 'adresse')
        }),
        ('🏷️ Type', {
            'fields': ('type_partenaire',)
        }),
        ('⚙️ Paramètres', {
            'fields': ('est_actif', 'est_mis_en_avant', 'ordre')
        }),
    )
    
    # ✅ Champs auto_now_add/auto_now en lecture seule
    readonly_fields = ('created_at', 'updated_at')
    
    def get_logo_preview(self, obj):
        """
        Afficher un aperçu du logo dans la liste
        """
        if obj.logo:
            return format_html(
                '<img src="{}" width="60" height="40" style="object-fit:contain; border-radius:5px;"/>', 
                obj.logo.url
            )
        # ✅ CORRECTION : Retourner une chaîne simple (sans format_html)
        return '<span style="color:#999;font-size:12px;">Aucun logo</span>'
    get_logo_preview.short_description = 'Logo'
    
    def type_partenaire_display(self, obj):
        return obj.get_type_partenaire_display()
    type_partenaire_display.short_description = 'Type'
    
    actions = ['activer_partenaires', 'desactiver_partenaires']
    
    def activer_partenaires(self, request, queryset):
        count = queryset.update(est_actif=True)
        self.message_user(request, f'{count} partenaire(s) activé(s).')
    activer_partenaires.short_description = '✅ Activer les partenaires sélectionnés'
    
    def desactiver_partenaires(self, request, queryset):
        count = queryset.update(est_actif=False)
        self.message_user(request, f'{count} partenaire(s) désactivé(s).')
    desactiver_partenaires.short_description = '❌ Désactiver les partenaires sélectionnés'