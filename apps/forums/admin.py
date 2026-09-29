from django.contrib import admin
from apps.core.admin import admin_site
from .models import ForumCategorie, ForumSujet, ForumMessage


@admin.register(ForumCategorie, site=admin_site)
class ForumCategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre', 'est_active')
    list_editable = ('ordre', 'est_active')
    search_fields = ('nom',)


@admin.register(ForumSujet, site=admin_site)
class ForumSujetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'auteur', 'date_creation')
    list_filter = ('categorie',)
    search_fields = ('titre', 'contenu')


@admin.register(ForumMessage, site=admin_site)
class ForumMessageAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'auteur', 'date_creation')
    search_fields = ('contenu',)
