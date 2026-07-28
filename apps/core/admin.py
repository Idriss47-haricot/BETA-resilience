"""
Administration de l'application Core - Version complète et corrigée
"""
import csv
import logging
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from django.http import HttpResponse
from apps.core.models import SiteConfiguration, Page

logger = logging.getLogger(__name__)


# ============================================================
# 1. ADMIN PERSONNALISÉ
# ============================================================
class CustomAdminSite(AdminSite):
    """
    Panneau d'administration personnalisé pour BETA-Résilience
    """
    site_header = '🌿 BETA-Résilience Administration'
    site_title = 'BETA-Résilience - Panneau d\'administration'
    index_title = '📊 Tableau de bord - Gestion du site'
    
    def has_permission(self, request):
        """
        Vérifier que l'utilisateur a les permissions adéquates
        """
        return request.user.is_active and request.user.is_staff
    
    def login(self, request, extra_context=None):
        """
        Journaliser les tentatives de connexion
        """
        if request.method == 'POST':
            username = request.POST.get('username', 'inconnu')
            ip = request.META.get('REMOTE_ADDR', 'inconnu')
            logger.info(f"Tentative de connexion admin: {username} depuis {ip}")
        
        return super().login(request, extra_context)
    
    def get_app_list(self, request, app_label=None):
        """
        Personnaliser l'affichage des applications avec des icônes
        """
        # ✅ CORRECTION : Gérer le cas où app_label est fourni
        if app_label:
            return super().get_app_list(request, app_label)
        
        app_list = super().get_app_list(request)
        
        # Renommer les sections pour plus de clarté
        app_names = {
            'auth': '🔐 Authentification et autorisation',
            'core': '⚙️ Gestion du site',
            'membres': '👥 Membres',
            'actualites': '📰 Actualités',
            'documents': '📄 Documents',
            'projets': '📁 Projets',
            'services': '🛠️ Services',
            'partenaires': '🤝 Partenaires',
            'contacts': '✉️ Contacts',
        }
        
        for app in app_list:
            if app['app_label'] in app_names:
                app['name'] = app_names[app['app_label']]
        
        return app_list


# ============================================================
# 2. INSTANCIER LE SITE ADMIN PERSONNALISÉ
# ============================================================
admin_site = CustomAdminSite(name='admin')


# ============================================================
# 3. ADMIN DES UTILISATEURS (AUTH)
# ============================================================
class UserAdmin(BaseUserAdmin):
    """
    Administration personnalisée des utilisateurs
    """
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'is_active', 
        'last_login'
    )
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activer_utilisateurs', 'desactiver_utilisateurs', 'exporter_utilisateurs']
    
    def activer_utilisateurs(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} utilisateur(s) activé(s).')
    activer_utilisateurs.short_description = '✅ Activer les utilisateurs sélectionnés'
    
    def desactiver_utilisateurs(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} utilisateur(s) désactivé(s).')
    desactiver_utilisateurs.short_description = '❌ Désactiver les utilisateurs sélectionnés'
    
    def exporter_utilisateurs(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="utilisateurs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nom', 'Prénom', 'Email', 'Nom d\'utilisateur', 'Staff', 'Actif', 'Dernière connexion'])
        
        for user in queryset:
            writer.writerow([
                user.last_name,
                user.first_name,
                user.email,
                user.username,
                'Oui' if user.is_staff else 'Non',
                'Oui' if user.is_active else 'Non',
                user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Jamais'
            ])
        
        return response
    exporter_utilisateurs.short_description = '📊 Exporter les utilisateurs en CSV'


# ============================================================
# 4. ENREGISTRER LES MODÈLES AUTH AVEC ADMIN_SITE
# ============================================================
admin_site.register(User, UserAdmin)
admin_site.register(Group)


# ============================================================
# 5. ADMIN DE LA CONFIGURATION DU SITE
# ============================================================
@admin.register(SiteConfiguration, site=admin_site)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """
    Configuration du site
    """
    fieldsets = (
        ('🏢 Informations générales', {
            'fields': ('site_name', 'site_tagline')
        }),
        ('📞 Coordonnées', {
            'fields': ('email', 'email_contact', 'phone', 'phone_whatsapp', 'address', 'boite_postale')
        }),
        ('🌐 Réseaux sociaux', {
            'fields': ('facebook', 'linkedin', 'twitter', 'instagram', 'youtube', 'whatsapp')
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('🎨 Design', {
            'fields': ('primary_color', 'secondary_color', 'accent_color', 'logo', 'logo_footer', 'favicon'),
            'classes': ('collapse',)
        }),
        ('📄 Footer', {
            'fields': ('footer_text', 'copyright_text'),
            'classes': ('collapse',)
        }),
        ('📊 Analytics', {
            'fields': ('google_analytics_id',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        if SiteConfiguration.objects.exists():
            return False
        return True


# ============================================================
# 6. ADMIN DES PAGES STATIQUES
# ============================================================
@admin.register(Page, site=admin_site)
class PageAdmin(admin.ModelAdmin):
    """
    Gestion des pages statiques
    """
    list_display = (
        'title', 
        'slug', 
        'is_published', 
        'is_in_menu', 
        'order', 
        'get_cover_preview',
        'created_at'
    )
    list_filter = ('is_published', 'is_in_menu')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order', 'title')
    
    fieldsets = (
        ('📝 Contenu', {
            'fields': ('title', 'slug', 'content', 'cover_image')
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('⚙️ Paramètres d\'affichage', {
            'fields': ('order', 'is_published', 'is_in_menu')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;"/>', 
                obj.cover_image.url
            )
        return '-'
    get_cover_preview.short_description = 'Aperçu'