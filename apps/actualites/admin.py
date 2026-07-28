"""
Administration de l'application Actualités
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin import admin_site  # ✅ IMPORT DU ADMIN PERSONNALISÉ
from apps.actualites.models import CategorieActualite, Article, Commentaire


@admin.register(CategorieActualite, site=admin_site)  # ✅ site=admin_site
class CategorieActualiteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'ordre', 'est_active', 'color_preview')
    list_filter = ('est_active',)
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ('ordre', 'nom')
    
    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:{};"></span>',
            obj.couleur
        )
    color_preview.short_description = 'Couleur'


@admin.register(Article, site=admin_site)  # ✅ site=admin_site
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'titre',
        'auteur',
        'get_categories',
        'date_publication',
        'statut',
        'est_a_la_une',
        'nb_vues',
        'get_image_preview'
    )
    list_filter = ('statut', 'est_a_la_une', 'categories', 'date_publication')
    search_fields = ('titre', 'contenu', 'extrait', 'tags')
    prepopulated_fields = {'slug': ('titre',)}
    filter_horizontal = ('categories',)
    ordering = ('-date_publication',)
    
    fieldsets = (
        ('📝 Contenu', {
            'fields': ('titre', 'slug', 'contenu', 'extrait')
        }),
        ('🖼️ Images et médias', {
            'fields': ('image_couverture', 'video')
        }),
        ('📂 Métadonnées', {
            'fields': ('categories', 'auteur', 'tags')
        }),
        ('📅 Dates', {
            'fields': ('date_evenement', 'date_programmation')
        }),
        ('⚙️ Statut et paramètres', {
            'fields': ('statut', 'est_publie', 'est_a_la_une', 'est_en_avant')
        }),
        ('📈 Statistiques', {
            'fields': ('nb_vues', 'nb_partages', 'nb_commentaires'),
            'classes': ('collapse',)
        }),
        ('🔍 SEO', {
            'fields': ('meta_titre', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    # ✅ Champs auto_now_add/auto_now en lecture seule
    readonly_fields = (
        'nb_vues', 
        'nb_partages', 
        'nb_commentaires', 
        'created_at', 
        'updated_at',
        'date_publication',
        'date_modification'
    )
    
    def get_image_preview(self, obj):
        if obj.image_couverture:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;"/>',
                obj.image_couverture.url
            )
        return '-'
    get_image_preview.short_description = 'Image'
    
    def get_categories(self, obj):
        return ', '.join([cat.nom for cat in obj.categories.all()])
    get_categories.short_description = 'Catégories'
    
    actions = ['publier_selection', 'archiver_selection', 'mettre_a_la_une']
    
    def publier_selection(self, request, queryset):
        count = queryset.update(statut='publie', est_publie=True)
        self.message_user(request, f'{count} article(s) publié(s).')
    publier_selection.short_description = '📤 Publier les articles sélectionnés'
    
    def archiver_selection(self, request, queryset):
        count = queryset.update(statut='archive', est_publie=False)
        self.message_user(request, f'{count} article(s) archivé(s).')
    archiver_selection.short_description = '📥 Archiver les articles sélectionnés'
    
    def mettre_a_la_une(self, request, queryset):
        Article.objects.update(est_a_la_une=False)
        count = queryset.update(est_a_la_une=True)
        self.message_user(request, f'{count} article(s) mis à la une.')
    mettre_a_la_une.short_description = '⭐ Mettre à la une'


@admin.register(Commentaire, site=admin_site)  # ✅ site=admin_site
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'article', 'est_approuve', 'est_signale', 'date_creation')
    list_filter = ('est_approuve', 'est_signale', 'date_creation')
    search_fields = ('auteur', 'email', 'contenu')
    ordering = ('-date_creation',)
    
    readonly_fields = ('date_creation', 'date_modification')
    
    actions = ['approuver_commentaires', 'signaler_commentaires']
    
    def approuver_commentaires(self, request, queryset):
        count = queryset.update(est_approuve=True)
        self.message_user(request, f'{count} commentaire(s) approuvé(s).')
    approuver_commentaires.short_description = '✅ Approuver les commentaires sélectionnés'
    
    def signaler_commentaires(self, request, queryset):
        count = queryset.update(est_signale=True)
        self.message_user(request, f'{count} commentaire(s) signalé(s).')
    signaler_commentaires.short_description = '🚫 Signaler les commentaires sélectionnés'