"""
Administration de l'application Services
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin import admin_site  # ✅ IMPORT DU ADMIN PERSONNALISÉ
from apps.services.models import Service, ServiceAvantage


class ServiceAvantageInline(admin.TabularInline):
    """
    Affichage des avantages d'un service en ligne
    """
    model = ServiceAvantage
    extra = 1
    fields = ('avantage', 'ordre')
    ordering = ('ordre',)


@admin.register(Service, site=admin_site)  # ✅ site=admin_site
class ServiceAdmin(admin.ModelAdmin):
    """
    Gestion des services
    """
    list_display = (
        'titre', 
        'icone_preview',
        'ordre', 
        'est_actif', 
        'est_mis_en_avant', 
        'created_at'
    )
    list_filter = ('est_actif', 'est_mis_en_avant')
    search_fields = ('titre', 'description_courte', 'description_longue')
    prepopulated_fields = {'slug': ('titre',)}
    ordering = ('ordre', 'titre')
    inlines = [ServiceAvantageInline]
    
    fieldsets = (
        ('📝 Informations générales', {
            'fields': ('titre', 'slug', 'description_courte', 'description_longue')
        }),
        ('🎨 Icône et image', {
            'fields': ('icone', 'image')
        }),
        ('⚙️ Paramètres', {
            'fields': ('ordre', 'est_actif', 'est_mis_en_avant')
        }),
        ('🔍 SEO', {
            'fields': ('meta_titre', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    # ✅ Champs auto_now_add/auto_now en lecture seule
    readonly_fields = ('created_at', 'updated_at')
    
    def icone_preview(self, obj):
        """Afficher un aperçu de l'icône"""
        return format_html('<i class="{}" style="font-size: 20px; color: #2E7D32;"></i>', obj.icone)
    icone_preview.short_description = 'Icône'
    
    actions = ['activer_services', 'desactiver_services']
    
    def activer_services(self, request, queryset):
        count = queryset.update(est_actif=True)
        self.message_user(request, f'{count} service(s) activé(s).')
    activer_services.short_description = '✅ Activer les services sélectionnés'
    
    def desactiver_services(self, request, queryset):
        count = queryset.update(est_actif=False)
        self.message_user(request, f'{count} service(s) désactivé(s).')
    desactiver_services.short_description = '❌ Désactiver les services sélectionnés'


@admin.register(ServiceAvantage, site=admin_site)  # ✅ site=admin_site
class ServiceAvantageAdmin(admin.ModelAdmin):
    """
    Gestion des avantages des services
    """
    list_display = ('avantage', 'service', 'ordre')
    list_filter = ('service',)
    search_fields = ('avantage',)
    ordering = ('service', 'ordre')
    
    fieldsets = (
        ('📝 Informations', {
            'fields': ('service', 'avantage', 'ordre')
        }),
    )