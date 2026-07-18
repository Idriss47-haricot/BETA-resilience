from django.contrib import admin
from .models import ForumCategorie, ForumSujet, ForumMessage
from .models import CategorieForum

@admin.register(CategorieForum)
class CategorieForumAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('titre',)}
    list_display = ('id', 'titre')

@admin.register(ForumCategorie)
class ForumCategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre', 'est_active')
    list_editable = ('ordre', 'est_active')
    search_fields = ('nom',)

@admin.register(ForumSujet)
class ForumSujetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'auteur', 'date_creation')
    list_filter = ('categorie',)
    search_fields = ('titre', 'contenu')

@admin.register(ForumMessage)
class ForumMessageAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'auteur', 'date_creation')
    search_fields = ('contenu',)
