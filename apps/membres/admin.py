"""
Administration de l'application Membres - Version avec envoi d'identifiants
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from apps.core.admin import admin_site
from apps.membres.models import Membre, Fonction, DemandeAdhesion
from apps.membres.utils import envoyer_invitation, envoyer_refus, envoyer_identifiants_membre
import csv
from apps.membres.models import Membre, Fonction, DemandeAdhesion, HistoriqueEmail


@admin.register(Fonction, site=admin_site)
class FonctionAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre', 'est_actif')
    list_filter = ('est_actif',)
    search_fields = ('nom',)
    ordering = ('ordre',)


@admin.register(Membre, site=admin_site)
class MembreAdmin(admin.ModelAdmin):
    """
    Administration des membres
    """
    list_display = (
        'get_photo_preview',
        'nom_complet',
        'fonction',
        'est_membre_bureau',
        'est_actif',
        'est_compte_active',
        'date_validation',
        'get_token_status'
    )
    list_filter = ('est_actif', 'est_membre_bureau', 'est_compte_active', 'date_validation')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'biographie')
    prepopulated_fields = {'slug': ('prenom', 'nom')}
    ordering = ('-est_membre_bureau', 'fonction__ordre', 'nom')
    
    fieldsets = (
        ('🔐 Compte utilisateur', {
        'fields': ('user',)
        }),
        ('👤 Informations personnelles', {
            'fields': ('nom', 'prenom', 'photo', 'fonction', 'statut', 'biographie')
        }),
        ('📞 Contact', {
            'fields': ('email', 'telephone')
        }),
        ('🔗 Réseaux sociaux', {
            'fields': ('linkedin', 'twitter', 'researchgate', 'google_scholar'),
            'classes': ('collapse',)
        }),
        ('📋 Adhésion et activation', {
            'fields': ('est_actif', 'est_membre_bureau', 'est_compte_active', 'date_validation')
        }),
        ('🔑 Token d\'activation', {
            'fields': ('token_activation', 'token_expiration', 'date_invitation'),
            'classes': ('collapse',)
        }),
        ('🔗 URL', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'date_adhesion',
        'created_at',
        'updated_at',
        'token_activation',
        'token_expiration',
        'date_invitation',
        'date_validation'
    )
    
    def get_photo_preview(self, obj):
        """Afficher un aperçu de la photo"""
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:50%; border:2px solid #2E7D32;"/>',
                obj.photo.url
            )
        return format_html(
            '<span style="font-size:20px;">👤</span>'
        )
    get_photo_preview.short_description = 'Photo'
    
    def nom_complet(self, obj):
        """Retourner le nom complet"""
        return f'{obj.prenom} {obj.nom}'
    nom_complet.short_description = 'Nom complet'
    
    def get_token_status(self, obj):
        """Afficher le statut du token d'activation"""
        if obj.est_compte_active:
            return format_html('<span style="color:#2E7D32;font-weight:bold;">✅ Activé</span>')
        if obj.token_expiration:
            if obj.est_token_expire():
                return format_html('<span style="color:#C62828;font-weight:bold;">⏰ Expiré</span>')
            return format_html(
                '<span style="color:#FFA000;font-weight:bold;">⏳ {}</span>',
                obj.get_token_expiration_display()
            )
        return format_html('<span style="color:#999;">-</span>')
    get_token_status.short_description = 'Token'
    
    actions = ['exporter_csv', 'activer_membres', 'desactiver_membres']
    
    def exporter_csv(self, request, queryset):
        """Exporter les membres en CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="membres.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Nom', 
            'Prénom', 
            'Email', 
            'Téléphone', 
            'Fonction', 
            'Actif', 
            'Compte activé', 
            'Date validation'
        ])
        
        for membre in queryset:
            writer.writerow([
                membre.nom,
                membre.prenom,
                membre.email,
                membre.telephone,
                membre.fonction.nom if membre.fonction else '',
                'Oui' if membre.est_actif else 'Non',
                'Oui' if membre.est_compte_active else 'Non',
                membre.date_validation.strftime('%d/%m/%Y') if membre.date_validation else ''
            ])
        
        return response
    exporter_csv.short_description = '📊 Exporter les membres en CSV'
    
    def activer_membres(self, request, queryset):
        """Activer les membres sélectionnés"""
        count = queryset.update(est_actif=True)
        self.message_user(request, f'✅ {count} membre(s) activé(s).')
    activer_membres.short_description = '✅ Activer les membres sélectionnés'
    
    def desactiver_membres(self, request, queryset):
        """Désactiver les membres sélectionnés"""
        count = queryset.update(est_actif=False)
        self.message_user(request, f'❌ {count} membre(s) désactivé(s).')
    desactiver_membres.short_description = '❌ Désactiver les membres sélectionnés'


admin.register(DemandeAdhesion, site=admin_site)
class DemandeAdhesionAdmin(admin.ModelAdmin):
    list_display = (
        'nom_complet',
        'email',
        'get_statut_badge',
        'date_soumission',
        'get_membre_lien',
        'email_envoye_badge'
    )
    list_filter = ('statut', 'date_soumission')
    search_fields = ('nom', 'prenom', 'email', 'motivation')
    ordering = ('-date_soumission',)
    
    fieldsets = (
        ('📋 Informations du demandeur', {
            'fields': ('nom', 'prenom', 'email', 'telephone', 'date_naissance', 'profession')
        }),
        ('📝 Motivation et compétences', {
            'fields': ('motivation', 'competences')
        }),
        ('📄 Documents', {
            'fields': ('cv', 'lettre_motivation')
        }),
        ('⚙️ Traitement', {
            'fields': ('statut', 'commentaire_admin')
        }),
        ('🔗 Membre associé', {
            'fields': ('membre',),
            'classes': ('collapse',)
        }),
        ('⚙️ Actions', {
            'fields': (),
            'description': """
            <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                <button type="submit" name="_accept" class="button" style="background:#2E7D32;color:white;padding:8px 20px;border:none;border-radius:5px;cursor:pointer;">
                    ✅ Accepter + Envoyer les identifiants
                </button>
                <button type="submit" name="_refuse" class="button" style="background:#C62828;color:white;padding:8px 20px;border:none;border-radius:5px;cursor:pointer;">
                    ❌ Refuser la demande
                </button>
                <button type="submit" name="_resend" class="button" style="background:#FFA000;color:white;padding:8px 20px;border:none;border-radius:5px;cursor:pointer;">
                    📧 Renvoyer l'invitation
                </button>
            </div>
            """
        }),
    )
    
    readonly_fields = ('date_soumission', 'date_traitement')
    
    def nom_complet(self, obj):
        return f'{obj.prenom} {obj.nom}'
    nom_complet.short_description = 'Demandeur'
    
    def get_statut_badge(self, obj):
        colors = {
            'en_attente': '#FFA000',
            'acceptee': '#2E7D32',
            'refusee': '#C62828',
            'en_cours': '#1565C0',
            'invitation_envoyee': '#4CAF50',
            'compte_active': '#1B5E20',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 12px;border-radius:12px;font-size:11px;">{}</span>',
            colors.get(obj.statut, '#757575'),
            obj.get_statut_display()
        )
    get_statut_badge.short_description = 'Statut'
    
    def get_membre_lien(self, obj):
        if obj.membre:
            url = reverse('admin:membres_membre_change', args=[obj.membre.id])
            return format_html('<a href="{}" target="_blank">👤 Voir</a>', url)
        return '-'
    get_membre_lien.short_description = 'Membre'
    
    def email_envoye_badge(self, obj):
        if obj.membre and obj.membre.email_envoye:
            return format_html('<span style="color:#2E7D32;">✅ Email envoyé</span>')
        return format_html('<span style="color:#FFA000;">⏳ Non envoyé</span>')
    email_envoye_badge.short_description = 'Email'
    
    # ===== ACTIONS PERSONNALISÉES =====
    actions = ['accepter_et_envoyer_identifiants', 'refuser_demandes', 'renvoyer_invitations', 'exporter_csv']
    
    def accepter_et_envoyer_identifiants(self, request, queryset):
        """
        Accepter les demandes sélectionnées, créer un compte et envoyer les identifiants
        """
        count = 0
        erreurs = 0
        
        for demande in queryset:
            if demande.statut == 'acceptee':
                self.message_user(
                    request,
                    f'⚠️ La demande de {demande.prenom} {demande.nom} est déjà acceptée.',
                    level='WARNING'
                )
                continue
            
            # Vérifier si un membre existe déjà
            if not demande.membre:
                # Créer le membre
                membre = Membre.objects.create(
                    nom=demande.nom,
                    prenom=demande.prenom,
                    email=demande.email,
                    telephone=demande.telephone,
                    est_actif=True,
                )
                demande.membre = membre
                demande.save()
            
            # Envoyer les identifiants
            success, username, password = envoyer_identifiants_membre(demande, demande.membre)
            
            if success:
                demande.statut = 'acceptee'
                demande.date_traitement = timezone.now()
                demande.save()
                count += 1
                self.message_user(
                    request,
                    f'✅ Identifiants envoyés à {demande.prenom} {demande.nom} (username: {username})'
                )
            else:
                erreurs += 1
                self.message_user(
                    request,
                    f'⚠️ Erreur lors de l\'envoi des identifiants pour {demande.prenom} {demande.nom}',
                    level='ERROR'
                )
        
        if count > 0:
            self.message_user(
                request,
                f'✅ {count} demande(s) acceptée(s) et identifiants envoyés !'
            )
        if erreurs > 0:
            self.message_user(
                request,
                f'⚠️ {erreurs} erreur(s) lors de l\'envoi des identifiants.',
                level='ERROR'
            )
    
    accepter_et_envoyer_identifiants.short_description = '✅ Accepter + Envoyer les identifiants'
    
    def refuser_demandes(self, request, queryset):
        """Refuser les demandes sélectionnées et envoyer l'email de refus"""
        count = 0
        for demande in queryset:
            if demande.peut_etre_refusee():
                try:
                    demande.refuser()
                    envoyer_refus(demande, request)
                    count += 1
                except Exception as e:
                    self.message_user(
                        request, 
                        f'⚠️ Erreur pour {demande.prenom} {demande.nom}: {str(e)}',
                        level='ERROR'
                    )
        self.message_user(request, f'✅ {count} demande(s) refusée(s) et email(s) envoyé(s).')
    refuser_demandes.short_description = '❌ Refuser + Envoyer l\'email de refus'
    
    def renvoyer_invitations(self, request, queryset):
        """Renvoyer l'invitation aux demandes acceptées"""
        count = 0
        for demande in queryset:
            if demande.statut == 'acceptee' and demande.membre:
                try:
                    demande.renvoyer_invitation()
                    envoyer_invitation(demande, request)
                    count += 1
                except Exception as e:
                    self.message_user(
                        request, 
                        f'⚠️ Erreur pour {demande.prenom} {demande.nom}: {str(e)}',
                        level='ERROR'
                    )
        self.message_user(request, f'✅ {count} invitation(s) renvoyée(s).')
    renvoyer_invitations.short_description = '📧 Renvoyer l\'invitation'
    
    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="demandes_adhesion.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nom', 'Prénom', 'Email', 'Téléphone', 'Profession', 'Statut', 'Date de soumission'])
        
        for demande in queryset:
            writer.writerow([
                demande.nom,
                demande.prenom,
                demande.email,
                demande.telephone,
                demande.profession,
                demande.get_statut_display(),
                demande.date_soumission.strftime('%d/%m/%Y %H:%M')
            ])
        
        return response
    exporter_csv.short_description = '📊 Exporter les demandes en CSV'
    
    def save_model(self, request, obj, form, change):
        """Sauvegarder et gérer les changements de statut"""
        old_statut = None
        if change:
            try:
                old_obj = DemandeAdhesion.objects.get(pk=obj.pk)
                old_statut = old_obj.statut
            except DemandeAdhesion.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)
        
        # Si le statut a changé
        if change and old_statut != obj.statut:
            # Si le statut devient 'acceptee'
            if obj.statut == 'acceptee' and not obj.membre:
                try:
                    # Créer le membre
                    membre = Membre.objects.create(
                        nom=obj.nom,
                        prenom=obj.prenom,
                        email=obj.email,
                        telephone=obj.telephone,
                        est_actif=True,
                    )
                    obj.membre = membre
                    obj.save()
                    
                    # Envoyer les identifiants
                    success, username, password = envoyer_identifiants_membre(obj, membre)
                    
                    if success:
                        self.message_user(
                            request, 
                            f'✅ Demande acceptée et identifiants envoyés à {obj.email} (username: {username})'
                        )
                    else:
                        self.message_user(
                            request, 
                            f'⚠️ Demande acceptée mais erreur lors de l\'envoi des identifiants à {obj.email}',
                            level='ERROR'
                        )
                except Exception as e:
                    self.message_user(
                        request, 
                        f'⚠️ Erreur lors de l\'acceptation: {str(e)}',
                        level='ERROR'
                    )
            # Si le statut devient 'refusee'
            elif obj.statut == 'refusee':
                try:
                    envoyer_refus(obj, request)
                    self.message_user(
                        request, 
                        f'✅ Email de refus envoyé à {obj.email}'
                    )
                except Exception as e:
                    self.message_user(
                        request, 
                        f'⚠️ Erreur lors de l\'envoi du refus: {str(e)}',
                        level='ERROR'
                    )

@admin.register(HistoriqueEmail, site=admin_site)
class HistoriqueEmailAdmin(admin.ModelAdmin):
    """
    Administration de l'historique des emails
    """
    list_display = (
        'destinataire',
        'get_type_email_badge',
        'sujet_court',
        'date_envoi',
        'get_statut_badge',
        'get_membre_lien',
        'get_demande_lien'
    )
    list_filter = ('type_email', 'statut', 'date_envoi')
    search_fields = ('destinataire', 'sujet', 'contenu', 'admin_nom')
    ordering = ('-date_envoi',)
    
    fieldsets = (
        ('📧 Informations sur l\'email', {
            'fields': ('type_email', 'sujet', 'destinataire', 'contenu')
        }),
        ('🔗 Liens associés', {
            'fields': ('membre', 'demande', 'token')
        }),
        ('📊 Statut', {
            'fields': ('statut', 'message_erreur')
        }),
        ('👤 Administration', {
            'fields': ('admin_nom', 'ip_admin')
        }),
    )
    
    readonly_fields = ('date_envoi',)
    
    def sujet_court(self, obj):
        return obj.sujet[:60] + '...' if len(obj.sujet) > 60 else obj.sujet
    sujet_court.short_description = 'Sujet'
    
    def get_type_email_badge(self, obj):
        colors = {
            'invitation': '#2E7D32',
            'rappel': '#FFA000',
            'confirmation': '#1565C0',
            'refus': '#C62828',
            'validation': '#4CAF50',
        }
        labels = {
            'invitation': '📧 Invitation',
            'rappel': '⏰ Rappel',
            'confirmation': '✅ Confirmation',
            'refus': '❌ Refus',
            'validation': '📋 Validation',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 12px;border-radius:12px;font-size:11px;">{}</span>',
            colors.get(obj.type_email, '#757575'),
            labels.get(obj.type_email, obj.type_email)
        )
    get_type_email_badge.short_description = 'Type'
    
    def get_statut_badge(self, obj):
        colors = {
            'envoye': '#2E7D32',
            'erreur': '#C62828',
            'en_attente': '#FFA000',
        }
        labels = {
            'envoye': '✅ Envoyé',
            'erreur': '❌ Erreur',
            'en_attente': '⏳ En attente',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 12px;border-radius:12px;font-size:11px;">{}</span>',
            colors.get(obj.statut, '#757575'),
            labels.get(obj.statut, obj.statut)
        )
    get_statut_badge.short_description = 'Statut'
    
    def get_membre_lien(self, obj):
        if obj.membre:
            url = reverse('admin:membres_membre_change', args=[obj.membre.id])
            return format_html('<a href="{}" target="_blank">👤 Voir</a>', url)
        return '-'
    get_membre_lien.short_description = 'Membre'
    
    def get_demande_lien(self, obj):
        if obj.demande:
            url = reverse('admin:membres_demandeadhesion_change', args=[obj.demande.id])
            return format_html('<a href="{}" target="_blank">📋 Voir</a>', url)
        return '-'
    get_demande_lien.short_description = 'Demande'
    
    actions = ['exporter_csv']
    
    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="historique_emails.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Destinataire', 'Sujet', 'Statut', 'Admin'])
        
        for email in queryset:
            writer.writerow([
                email.date_envoi.strftime('%d/%m/%Y %H:%M'),
                email.get_type_email_display(),
                email.destinataire,
                email.sujet,
                email.get_statut_display(),
                email.admin_nom
            ])
        
        return response
    exporter_csv.short_description = '📊 Exporter l\'historique en CSV'