"""
Administration de l'application Membres - Version optimisée sans répétitions
"""
import csv
from io import BytesIO

from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.core.admin import admin_site
from apps.membres.models import (
    DemandeAdhesion,
    Fonction,
    HistoriqueEmail,
    Membre,
    MembreAssociation,
    MembreBureauEtude,
    MembreInvest,
    MembreLaboratoire,
)
from apps.membres.utils import (
    envoyer_identifiants_membre,
    envoyer_invitation,
    envoyer_refus,
)


@admin.register(Fonction, site=admin_site)
class FonctionAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre', 'est_actif')
    list_filter = ('est_actif',)
    search_fields = ('nom',)
    ordering = ('ordre',)

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    def has_delete_permission(self, request, obj=None):
        # Si on consulte le profil d'un superutilisateur, on retire la permission de supprimer
        if obj is not None and obj.is_superuser:
            return False
        
        # Pour les autres utilisateurs, garder le comportement normal
        return super().has_delete_permission(request, obj)


@admin.register(Membre, site=admin_site)
class MembreAdmin(admin.ModelAdmin):
    """
    Administration des membres
    """
    list_display = (
        'get_photo_preview',
        'nom_complet',
        'entite',
        'fonction',
        'est_membre_bureau',
        'est_actif',
        'est_compte_active',
        'date_validation',
        'get_token_status'
    )
    list_filter = ('entite', 'est_actif', 'est_membre_bureau', 'est_compte_active', 'date_validation')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'biographie')
    prepopulated_fields = {'slug': ('prenom', 'nom')}
    ordering = ('-est_membre_bureau', 'fonction__ordre', 'nom')
    
    fieldsets = (
        ('🔐 Compte utilisateur', {
            'fields': ('user',)
        }),
        ('👤 Informations personnelles', {
            'fields': ('entite', 'nom', 'prenom', 'photo', 'fonction', 'statut', 'biographie')
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

    def exporter_pdf_par_entite(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []

        entites_presentes = queryset.values_list('entite', flat=True).distinct()

        for entite_code in entites_presentes:
            entite_label = dict(Membre.ENTITE_CHOICES).get(entite_code, entite_code)
            membres_entite = queryset.filter(entite=entite_code).order_by('nom', 'prenom')

            elements.append(Paragraph(f"État des membres — {entite_label}", styles['Heading1']))
            elements.append(Spacer(1, 0.5*cm))

            data = [['Nom', 'Prénom', 'Email', 'Téléphone', 'Date d\'adhésion']]
            for m in membres_entite:
                data.append([
                    m.nom,
                    m.prenom,
                    m.email,
                    m.telephone or '-',
                    m.date_adhesion.strftime('%d/%m/%Y') if m.date_adhesion else '-',
                ])

            table = Table(data, colWidths=[3.2*cm, 3.2*cm, 5*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E7A3D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E8F3EA')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 1*cm))

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="membres_beta_resilience.pdf"'
        return response
    exporter_pdf_par_entite.short_description = '📄 Exporter en PDF (par entité)'
    
    def get_photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:50%; border:2px solid #2E7D32;"/>',
                obj.photo.url
            )
        return format_html('<span style="font-size:20px;">👤</span>')
    get_photo_preview.short_description = 'Photo'
    
    def nom_complet(self, obj):
        return f'{obj.prenom} {obj.nom}'
    nom_complet.short_description = 'Nom complet'
    
    def get_token_status(self, obj):
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
    
    actions = ['exporter_csv', 'exporter_pdf_par_entite', 'activer_membres', 'desactiver_membres']
    
    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="membres.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Nom', 'Prénom', 'Email', 'Téléphone', 'Fonction', 'Actif', 'Compte activé', 'Date validation'
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
        count = queryset.update(est_actif=True)
        self.message_user(request, f'✅ {count} membre(s) activé(s).')
    activer_membres.short_description = '✅ Activer les membres sélectionnés'
    
    def desactiver_membres(self, request, queryset):
        count = queryset.update(est_actif=False)
        self.message_user(request, f'❌ {count} membre(s) désactivé(s).')
    desactiver_membres.short_description = '❌ Désactiver les membres sélectionnés'


class MembreEntiteAdminBase(MembreAdmin):
    """Base commune pour les 4 rubriques par entité"""
    entite_code = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(entite=self.entite_code)


    def get_list_filter(self, request):
        return [f for f in self.list_filter if f != 'entite']


@admin.register(MembreAssociation, site=admin_site)
class MembreAssociationAdmin(MembreEntiteAdminBase):
    entite_code = 'association'


@admin.register(MembreBureauEtude, site=admin_site)
class MembreBureauEtudeAdmin(MembreEntiteAdminBase):
    entite_code = 'bureau_etude'


@admin.register(MembreInvest, site=admin_site)
class MembreInvestAdmin(MembreEntiteAdminBase):
    entite_code = 'invest'


@admin.register(MembreLaboratoire, site=admin_site)
class MembreLaboratoireAdmin(MembreEntiteAdminBase):
    entite_code = 'laboratoire'


@admin.register(DemandeAdhesion, site=admin_site)
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
    
    # ===== HELPER POUR ÉVITER LA RÉPÉTITION =====
    def _traiter_acceptation(self, request, demande):
        """Méthode utilitaire commune pour créer le membre et envoyer ses identifiants"""
        if not demande.membre:
            membre = Membre.objects.create(
                nom=demande.nom,
                prenom=demande.prenom,
                email=demande.email,
                telephone=demande.telephone,
                est_actif=True,
            )
            demande.membre = membre
            demande.save()

        success, username, _ = envoyer_identifiants_membre(demande, demande.membre)

        if success:
            demande.statut = 'acceptee'
            demande.date_traitement = timezone.now()
            demande.save()
            self.message_user(
                request,
                f'✅ Identifiants envoyés à {demande.prenom} {demande.nom} (username: {username})'
            )
            return True
        else:
            self.message_user(
                request,
                f'⚠️ Erreur lors de l\'envoi des identifiants pour {demande.prenom} {demande.nom}',
                level='ERROR'
            )
            return False

    # ===== ACTIONS PERSONNALISÉES =====
    actions = ['accepter_et_envoyer_identifiants', 'refuser_demandes', 'renvoyer_invitations', 'exporter_csv']
    
    def accepter_et_envoyer_identifiants(self, request, queryset):
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
            
            if self._traiter_acceptation(request, demande):
                count += 1
            else:
                erreurs += 1
        
        if count > 0:
            self.message_user(request, f'✅ {count} demande(s) acceptée(s) et identifiants envoyés !')
        if erreurs > 0:
            self.message_user(request, f'⚠️ {erreurs} erreur(s) lors de l\'envoi des identifiants.', level='ERROR')
    
    accepter_et_envoyer_identifiants.short_description = '✅ Accepter + Envoyer les identifiants'
    
    def refuser_demandes(self, request, queryset):
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
    
    
    def save_model(self, request, obj, form, change):
        old_statut = None
        if change:
            try:
                old_obj = DemandeAdhesion.objects.get(pk=obj.pk)
                old_statut = old_obj.statut
            except DemandeAdhesion.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)
        
        if change and old_statut != obj.statut:
            if obj.statut == 'acceptee':
                try:
                    self._traiter_acceptation(request, obj)
                except Exception as e:
                    self.message_user(
                        request, 
                        f'⚠️ Erreur lors de l\'acceptation: {str(e)}',
                        level='ERROR'
                    )
            elif obj.statut == 'refusee':
                try:
                    envoyer_refus(obj, request)
                    self.message_user(request, f'✅ Email de refus envoyé à {obj.email}')
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
    
    
    
    
    def get_demande_lien(self, obj):
        if obj.demande:
            url = reverse('admin:membres_demandeadhesion_change', args=[obj.demande.id])
            return format_html('<a href="{}" target="_blank">📋 Voir</a>', url)
        return '-'
    get_demande_lien.short_description = 'Demande'
    
    actions = ['exporter_csv']
    
   
