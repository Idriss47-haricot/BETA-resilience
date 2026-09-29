"""
Administration de l'application Contacts
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from apps.core.admin import admin_site  # ✅ IMPORT DU ADMIN PERSONNALISÉ
from apps.contacts.models import MessageContact
import csv


@admin.register(MessageContact, site=admin_site)  # ✅ site=admin_site
class MessageContactAdmin(admin.ModelAdmin):
    """
    Gestion des messages de contact
    """
    list_display = (
        'nom_complet',
        'email',
        'get_sujet_display',
        'date_envoi',
        'est_lu_badge',
        'est_repondu_badge'
    )
    list_filter = ('est_lu', 'est_repondu', 'sujet', 'date_envoi')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'message')
    ordering = ('-date_envoi',)
    
    fieldsets = (
        ('📋 Informations de l\'expéditeur', {
            'fields': ('nom', 'prenom', 'email', 'telephone')
        }),
        ('📝 Message', {
            'fields': ('sujet', 'sujet_personnalise', 'message')
        }),
        ('📊 Statut', {
            'fields': ('est_lu', 'est_repondu', 'reponse')
        }),
        ('🔍 Informations techniques', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    # ✅ Champs auto_now_add/auto_now en lecture seule
    readonly_fields = ('date_envoi', 'date_reponse')
    
    def nom_complet(self, obj):
        return f'{obj.prenom} {obj.nom}'
    nom_complet.short_description = 'Expéditeur'
    
    def get_sujet_display(self, obj):
        return obj.get_sujet_complet()
    get_sujet_display.short_description = 'Sujet'
    
    def est_lu_badge(self, obj):
        if obj.est_lu:
            return format_html('<span class="badge bg-success">✅ Lu</span>')
        return format_html('<span class="badge bg-warning">📕 Non lu</span>')
    est_lu_badge.short_description = 'Status'
    
    def est_repondu_badge(self, obj):
        if obj.est_repondu:
            return format_html('<span class="badge bg-info">📨 Répondu</span>')
        return format_html('<span class="badge bg-secondary">⏳ En attente</span>')
    est_repondu_badge.short_description = 'Réponse'
    
    def get_readonly_fields(self, request, obj=None):
        """Rendre certains champs modifiables uniquement si le message est lu"""
        if obj and obj.est_lu:
            return self.readonly_fields
        return self.readonly_fields + ('reponse',)
    
    actions = ['marquer_lu', 'marquer_non_lu', 'exporter_csv']
    
    def marquer_lu(self, request, queryset):
        count = queryset.update(est_lu=True)
        self.message_user(request, f'{count} message(s) marqué(s) comme lu.')
    marquer_lu.short_description = '📖 Marquer comme lu'
    
    def marquer_non_lu(self, request, queryset):
        count = queryset.update(est_lu=False)
        self.message_user(request, f'{count} message(s) marqué(s) comme non lu.')
    marquer_non_lu.short_description = '📕 Marquer comme non lu'
    
    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="messages_contact.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nom', 'Prénom', 'Email', 'Téléphone', 'Sujet', 'Message', 'Date', 'Lu', 'Répondu'])
        
        for msg in queryset:
            writer.writerow([
                msg.nom,
                msg.prenom,
                msg.email,
                msg.telephone,
                msg.get_sujet_complet(),
                msg.message,
                msg.date_envoi.strftime('%d/%m/%Y %H:%M'),
                'Oui' if msg.est_lu else 'Non',
                'Oui' if msg.est_repondu else 'Non'
            ])
        
        return response
    exporter_csv.short_description = '📊 Exporter les messages en CSV'
    
    def save_model(self, request, obj, form, change):
        """Mettre à jour la date de réponse si le message est marqué comme répondu"""
        if change and 'est_repondu' in form.changed_data and obj.est_repondu:
            from django.utils import timezone
            obj.date_reponse = timezone.now()
        super().save_model(request, obj, form, change)