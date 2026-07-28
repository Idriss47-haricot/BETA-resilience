"""
Administration de l'application Notifications
"""
from django import forms  # ✅ AJOUTER CETTE LIGNE
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib import messages
from apps.core.admin import admin_site
from apps.notifications.models import Notification, PreferenceNotification
from apps.notifications.utils import envoyer_notification_a_tous, envoyer_notification_a_groupe, envoyer_email_notification


class NotificationAdminForm(forms.ModelForm):
    """
    Formulaire personnalisé pour l'admin
    """
    envoyer_a_tous = forms.BooleanField(
        required=False,
        label='📧 Envoyer à tous les membres',
        help_text='Cocher pour envoyer cette notification à tous les membres actifs'
    )
    envoyer_par_email = forms.BooleanField(
        required=False,
        label='📧 Envoyer aussi par email',
        help_text='Les membres recevront aussi un email'
    )
    
    class Meta:
        model = Notification
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['utilisateur'].required = False
        self.fields['envoyer_a_tous'].initial = True


@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = (
        'titre_court',
        'get_type_badge',
        'utilisateur',
        'date_creation',
        'est_lue_badge',
        'get_icone_preview'
    )
    list_filter = ('type', 'est_lue', 'date_creation')
    search_fields = ('titre', 'message', 'utilisateur__username', 'utilisateur__email')
    ordering = ('-date_creation',)
    
    fieldsets = (
        ('📨 Informations', {
            'fields': ('type', 'titre', 'message', 'lien')
        }),
        ('👤 Destinataire', {
            'fields': ('utilisateur', 'envoyer_a_tous', 'envoyer_par_email')
        }),
        ('📊 Statut', {
            'fields': ('est_lue', 'date_lecture'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('date_creation', 'date_lecture')
    
    def save_model(self, request, obj, form, change):
        """Sauvegarder et envoyer les notifications"""
        envoyer_a_tous = form.cleaned_data.get('envoyer_a_tous', False)
        envoyer_par_email = form.cleaned_data.get('envoyer_par_email', False)
        
        if envoyer_a_tous:
            # Envoyer à tous les membres actifs
            from apps.membres.models import Membre
            membres = Membre.objects.filter(est_actif=True, est_compte_active=True)
            count = 0
            
            for membre in membres:
                if membre.user:
                    notification = Notification.objects.create(
                        utilisateur=membre.user,
                        type=obj.type,
                        titre=obj.titre,
                        message=obj.message,
                        lien=obj.lien,
                    )
                    count += 1
                    
                    # Envoyer par email si demandé
                    if envoyer_par_email:
                        from apps.notifications.utils import envoyer_email_notification
                        envoyer_email_notification(notification)
            
            self.message_user(
                request,
                f'✅ Notification envoyée à {count} membres !'
            )
            # Ne pas sauvegarder l'objet actuel (il a été dupliqué)
            return
        
        # Sauvegarde normale
        super().save_model(request, obj, form, change)
    
    def titre_court(self, obj):
        return obj.titre[:50] + '...' if len(obj.titre) > 50 else obj.titre
    titre_court.short_description = 'Titre'
    
    def get_type_badge(self, obj):
        icons = {
            'demande_validee': '✅',
            'demande_refusee': '❌',
            'nouveau_document': '📄',
            'evenement_proche': '📅',
            'message_forum': '💬',
            'systeme': '⚙️',
        }
        return format_html(
            '<span style="color:{};">{} {}</span>',
            obj.get_couleur(),
            icons.get(obj.type, '🔔'),
            obj.get_type_display()
        )
    get_type_badge.short_description = 'Type'
    
    def est_lue_badge(self, obj):
        if obj.est_lue:
            return format_html('<span style="color:#28a745;">✅ Lue</span>')
        return format_html('<span style="color:#dc3545;">🔴 Non lue</span>')
    est_lue_badge.short_description = 'Statut'
    
    def get_icone_preview(self, obj):
        return format_html(
            '<i class="fas {}" style="color:{};font-size:1.2rem;"></i>',
            obj.get_icone(),
            obj.get_couleur()
        )
    get_icone_preview.short_description = 'Icône'
    
    actions = ['envoyer_selection', 'envoyer_a_tous_action']
    
    def envoyer_selection(self, request, queryset):
        """Envoyer les notifications sélectionnées aux membres"""
        from apps.membres.models import Membre
        membres = Membre.objects.filter(est_actif=True, est_compte_active=True)
        count = 0
        
        for notification in queryset:
            for membre in membres:
                if membre.user:
                    Notification.objects.create(
                        utilisateur=membre.user,
                        type=notification.type,
                        titre=notification.titre,
                        message=notification.message,
                        lien=notification.lien,
                    )
                    count += 1
        
        self.message_user(request, f'✅ Notification envoyée à {count} membres !')
    envoyer_selection.short_description = '📧 Envoyer aux membres'
    
    def envoyer_a_tous_action(self, request, queryset):
        """Envoyer à tous les membres (action en masse)"""
        from apps.membres.models import Membre
        membres = Membre.objects.filter(est_actif=True, est_compte_active=True)
        count = 0
        
        for notification in queryset:
            for membre in membres:
                if membre.user:
                    Notification.objects.create(
                        utilisateur=membre.user,
                        type=notification.type,
                        titre=notification.titre,
                        message=notification.message,
                        lien=notification.lien,
                    )
                    count += 1
        
        self.message_user(request, f'✅ Notification envoyée à {count} membres !')
    envoyer_a_tous_action.short_description = '📧 Envoyer à tous les membres (massif)'


@admin.register(PreferenceNotification, site=admin_site)
class PreferenceNotificationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'email_notifications', 'push_notifications')
    search_fields = ('utilisateur__username',)