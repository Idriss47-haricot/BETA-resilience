"""
Administration de l'application Demandes avec envoi d'email automatique
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.core.mail import get_connection, EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from apps.core.admin import admin_site
from apps.demandes.models import Demande
import csv


@admin.register(Demande, site=admin_site)
class DemandeAdmin(admin.ModelAdmin):
    list_display = (
        'nom_complet',
        'entite_badge',
        'get_type_demande',
        'date_soumission',
        'statut_badge',
        'get_fichier_link'
    )
    list_filter = ('entite', 'statut', 'type_demande', 'date_soumission')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'societe', 'objet', 'message')
    ordering = ('-date_soumission',)

    fieldsets = (
        ('🏢 Entité et type de demande', {
            'fields': ('entite', 'type_demande', 'autre_type')
        }),
        ('👤 Informations personnelles', {
            'fields': ('nom', 'prenom', 'email', 'telephone')
        }),
        ('💼 Informations professionnelles', {
            'fields': ('societe', 'fonction')
        }),
        ('📝 Demande', {
            'fields': ('objet', 'message', 'fichier')
        }),
        ('⚙️ Traitement', {
            'fields': ('statut', 'commentaire_admin')
        }),
        ('🔍 Informations techniques', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('date_soumission', 'date_modification', 'ip_address', 'user_agent')

    # ===== AFFICHAGE =====

    def nom_complet(self, obj):
        return f'{obj.prenom} {obj.nom}'
    nom_complet.short_description = 'Demandeur'

    def get_type_demande(self, obj):
        return obj.get_type_demande_display()
    get_type_demande.short_description = 'Type de demande'

    def statut_badge(self, obj):
        colors = {
            'en_attente': '#FFA000',
            'en_cours': '#1565C0',
            'traite': '#2E7D32',
            'rejete': '#C62828',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 12px;border-radius:12px;font-size:11px;">{}</span>',
            colors.get(obj.statut, '#757575'),
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'

    def entite_badge(self, obj):
        colors = {
            'association': '#2E7D32',
            'bureau_etude': '#1565C0',
            'invest': '#E65100',
            'laboratoire': '#6A1B9A',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 12px;border-radius:12px;font-size:11px;">{}</span>',
            colors.get(obj.entite, '#757575'),
            obj.get_entite_display()
        )
    entite_badge.short_description = 'Entité'

    def get_fichier_link(self, obj):
        if obj.fichier:
            return format_html('<a href="{}" target="_blank">📄 Voir</a>', obj.fichier.url)
        return '-'
    get_fichier_link.short_description = 'Fichier'

    # ===== SAUVEGARDE AVEC ENVOI EMAIL =====

    def save_model(self, request, obj, form, change):
        old_statut = None
        if change:
            try:
                old_obj = Demande.objects.get(pk=obj.pk)
                old_statut = old_obj.statut
            except Demande.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        if change and old_statut != obj.statut:
            self.envoyer_email_changement_statut(obj, old_statut, request)

    # ===== ENVOI EMAIL — MÉTHODE DANS LA CLASSE =====

    def envoyer_email_changement_statut(self, demande, old_statut, request):
        statuts_avec_email = ['traite', 'rejete']

        if demande.statut not in statuts_avec_email:
            return

        try:
            if demande.statut == 'traite':
                sujet = f'✅ Votre demande a été validée - {demande.get_entite_display()}'
            else:
                sujet = f'❌ Votre demande a été refusée - {demande.get_entite_display()}'

            context = {
                'demande': demande,
                'site_name': 'BETA-Résilience',
                'site_url': 'http://127.0.0.1:8000',
                'admin_comment': demande.commentaire_admin or '',
                'old_statut': old_statut,
            }

            message_html = render_to_string(
                'demandes/email_changement_statut.html', context
            )

            # Nouvelle connexion forcée à chaque envoi sur port 465
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host='smtp.gmail.com',
                port=465,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_ssl=True,
                use_tls=False,
                fail_silently=False,
            )

            email = EmailMessage(
                sujet,
                message_html,
                settings.DEFAULT_FROM_EMAIL,
                [demande.email],
                reply_to=[settings.CONTACT_EMAIL],
                connection=connection,
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)

            self.message_user(
                request,
                f'✅ Email envoyé à {demande.email}'
            )

        except Exception as e:
            self.message_user(
                request,
                f'⚠️ Erreur envoi email : {str(e)}',
                level='ERROR'
            )

    # ===== ACTIONS EN MASSE =====

    actions = ['exporter_csv', 'marquer_traite', 'marquer_en_cours', 'marquer_rejete', 'envoyer_email_selection']

    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="demandes.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Entité', 'Type', 'Nom', 'Prénom', 'Email', 'Téléphone', 'Société', 'Objet', 'Message', 'Statut'])

        for demande in queryset:
            writer.writerow([
                demande.date_soumission.strftime('%d/%m/%Y %H:%M'),
                demande.get_entite_display(),
                demande.get_type_demande_display(),
                demande.nom,
                demande.prenom,
                demande.email,
                demande.telephone,
                demande.societe,
                demande.objet,
                demande.message,
                demande.get_statut_display()
            ])

        return response
    exporter_csv.short_description = '📊 Exporter les demandes en CSV'

    def marquer_traite(self, request, queryset):
        count = 0
        for demande in queryset:
            if demande.statut != 'traite':
                demande.statut = 'traite'
                demande.date_traitement = timezone.now()
                demande.save()
                self.envoyer_email_changement_statut(demande, None, request)
                count += 1
        self.message_user(request, f'{count} demande(s) marquée(s) comme traitées.')
    marquer_traite.short_description = '✅ Marquer comme traité + envoyer email'

    def marquer_en_cours(self, request, queryset):
        count = queryset.update(statut='en_cours')
        self.message_user(request, f'{count} demande(s) marquée(s) comme en cours.')
    marquer_en_cours.short_description = '🔄 Marquer comme en cours'

    def marquer_rejete(self, request, queryset):
        count = 0
        for demande in queryset:
            if demande.statut != 'rejete':
                demande.statut = 'rejete'
                demande.date_traitement = timezone.now()
                demande.save()
                self.envoyer_email_changement_statut(demande, None, request)
                count += 1
        self.message_user(request, f'{count} demande(s) rejetée(s).')
    marquer_rejete.short_description = '❌ Marquer comme rejeté + envoyer email'

    def envoyer_email_selection(self, request, queryset):
        count = 0
        for demande in queryset:
            if demande.email:
                self.envoyer_email_changement_statut(demande, None, request)
                count += 1
        self.message_user(request, f'{count} email(s) envoyé(s) aux demandeurs sélectionnés.')
    envoyer_email_selection.short_description = '📧 Envoyer un email aux demandeurs sélectionnés'